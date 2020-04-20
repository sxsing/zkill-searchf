# zkill-searchf

Search for EVE Killmails on Zkillboard by ship and equipments

## Installation

```shell
$ pip install zkill-searchf
```

Python version of 3.7 or higher is required to install this package.

A command-line script *zkill-searchf* will be installed.

## Usage

Before running the script, you need to create a YAML configuration file to specify search criteria - ship type, modules and/or module market groups.

To find EVE item and market group IDs, you will need an online database, such as: <https://everef.net/market>

Here is a sample configuration file:

```yaml
---
  ship: 17720  # ship id
  item:
    - [2897, 9127]  # put item id(s) in list
    - 542  # market group id
    - 131
  fetch-limit: 10
```

- ship: Item id of the ship

- item: Each entry is a search criteria. If an entry is integer, it's considered as a module market group ID. Otherwise a list of item ID should be provided.

- When filtering search results, items in a list are combined by 'OR' relationship, while item lists and market groups are combined by 'AND' relationship.

- fetch-limit: Maximum number of results to be displayed. Note that up to 1000 killmails of the specific ship type will be inspected. Afterward the program will stop anyway.

Give your configuration file to the script:

```shell
$ zkill-searchf <path-to-config-file>

Searching for Cynabal killmails with:

        220mm Vulcan AutoCannon II OR 220mm Medium 'Scout' Autocannon I
AND     Afterburners
AND     Microwarpdrives

https://zkillboard.com/kill/xxxxxxxx/
https://zkillboard.com/kill/xxxxxxxx/
https://zkillboard.com/kill/xxxxxxxx/
......

Finished. 10 matching killmails found. 404 killmails examined in total.
```
