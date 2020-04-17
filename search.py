import sys
import yaml
import requests

def is_fitted(item):
    flag = item['flag']
    return 11 <= flag <= 34 or 92 <= flag <= 99 or 125 <= flag <= 132

def km_filter(esi_km, required_item_block_li):
    fitting_li = [item['item_type_id'] for item in esi_km['victim']['items'] if is_fitted(item)]
    for required_item_block in required_item_block_li:
        if type(required_item_block) is not list:
            # It's a market group
            required_item_block = requests.get(
                'https://esi.evetech.net/latest/markets/groups/{}'.format(required_item_block)
            ).json()['types']
        item_found = False
        for item in required_item_block:
            if item in fitting_li:
                item_found = True
        if not item_found:
            return False
    return True

config = {}
with open(sys.argv[1], 'r') as config_file:
    config = yaml.load(config_file, Loader=yaml.FullLoader)
zkill_km_li = requests.get(
    'https://zkillboard.com/api/losses/shipTypeID/{}/'.format(config['ship'])
).json()
for zkill_km in zkill_km_li:
    km_id = zkill_km['killmail_id']
    km_hash = zkill_km['zkb']['hash']
    esi_km = requests.get(
        'https://esi.evetech.net/latest/killmails/{}/{}'.format(km_id, km_hash)
    ).json()
    if km_filter(esi_km, config['item']):
        print('https://zkillboard.com/kill/{}/'.format(km_id))
