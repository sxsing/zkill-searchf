import sys
import yaml
import asyncio
import aiohttp


async def fetch_json(url):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        for i in range(5):
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return await response.json(content_type=None)
            except asyncio.TimeoutError:
                continue
        raise asyncio.TimeoutError

async def name_worker(type_id):
    url = 'https://esi.evetech.net/latest/universe/types/{}'.format(type_id)
    response = await fetch_json(url)
    return response['name']

async def config_group_worker(group_maybe):
    if type(group_maybe) is list:
        task_li = []
        for item in group_maybe:
            task_li.append(asyncio.create_task(name_worker(item)))
        name_li = await asyncio.gather(*task_li)
        return group_maybe, name_li
    else:
        url = 'https://esi.evetech.net/latest/markets/groups/{}'.format(group_maybe)
        response = await fetch_json(url)
        name = response['name']
        if name in ['Micro', 'Small', 'Medium', 'Large', 'Capital']:
            parent_group_id = response['parent_group_id']
            url = 'https://esi.evetech.net/latest/markets/groups/{}'.format(parent_group_id)
            parent_response = await fetch_json(url)
            name = '{} {}'.format(name, parent_response['name'])
        return response['types'], name

async def zkill_api_worker(km_queue, config, task_li):
    for i in range(5):
        page = i + 1
        url = 'https://zkillboard.com/api/losses/shipTypeID/{}/page/{}/'.format(config['ship'], page)
        response = await fetch_json(url)
        for zkill_km in response:
            await km_queue.put(zkill_km)
    try:
        await asyncio.wait_for(km_queue.join(), 5)
    except asyncio.TimeoutError:
        pass
    for task in task_li:
        task.cancel()

def is_fitted(item):
    flag = item['flag']
    return 11 <= flag <= 34 or 92 <= flag <= 99 or 125 <= flag <= 132

async def esi_worker(km_queue, config, task_li, worker_stat):
    item_block_li = config['item']
    while True:
        zkill_km = await km_queue.get()
        worker_stat['total'] += 1
        km_id = zkill_km['killmail_id']
        km_hash = zkill_km['zkb']['hash']
        url = 'https://esi.evetech.net/latest/killmails/{}/{}'.format(km_id, km_hash)
        try:
            response = await fetch_json(url)
        except asyncio.TimeoutError:
            continue
        fitting_li = [item['item_type_id'] for item in response['victim']['items'] if is_fitted(item)]
        is_km_accepted = True
        for item_block in item_block_li:
            item_found = False
            for item in item_block:
                if item in fitting_li:
                    item_found = True
            if not item_found:
                is_km_accepted = False
        if is_km_accepted:
            print('https://zkillboard.com/kill/{}/'.format(km_id))
            worker_stat['output'] += 1
            if worker_stat['output'] >= config['fetch-limit']:
                for task in task_li:
                    task.cancel()
        km_queue.task_done()

async def main():
    config = {}
    with open(sys.argv[1], 'r') as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)

    ship_name = await name_worker(config['ship'])
    print('Searching for {} killmails with:\n'.format(ship_name))

    config_tasks_li = []
    for entry in config['item']:
        config_tasks_li.append(asyncio.create_task(config_group_worker(entry)))
    parsed_config = await asyncio.gather(*config_tasks_li)
    config['item'] = [x[0] for x in parsed_config]
    desc_li = [x[1] for x in parsed_config]
    print(
        '\nAND '.join(
            ['\t' + ' OR '.join(desc) if type(desc) is list else '\t' + desc 
                for desc in desc_li
            ]
        ) + '\n'
    )

    km_queue = asyncio.Queue(maxsize=100)
    task_li = []
    worker_stat = {'output': 0, 'total': 0}
    task_li.append(asyncio.create_task(zkill_api_worker(km_queue, config, task_li)))
    for i in range(100):
        task_li.append(asyncio.create_task(esi_worker(km_queue, config, task_li, worker_stat)))
    await asyncio.gather(*task_li, return_exceptions=True)
    print(
        '\nFinished. {} matching killmails found. {} killmails examined in total.'
        .format(worker_stat['output'], worker_stat['total'])
    )

def cli_entry_point():
    asyncio.run(main())

if __name__ == '__main__':
    asyncio.run(main())