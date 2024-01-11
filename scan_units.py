import argparse
import os
import lupa
import json

def iter_units(path):
    all_units = list()

    stats = dict()
    stats['Faction'] = 'Arm'
    stats['Tech level'] = 'T1'
    stats['Category'] = 'Bots'

    for dirpath, dirname, filenames in os.walk(path + '/units/ArmBots/'):
        for filename in filenames:
            all_units.append(load_unit(stats.copy(), dirpath + filename))
        break

    store(all_units)

def load_unit(stats, path):
    unit = load_lua_file(path)
    keys = sorted(unit.keys())
    assert len(keys) == 1
    internal_name = keys[0]
    table = unit[internal_name]
    
    stats['id'] = internal_name
    stats['Name'] = language_data['units']['names'][internal_name]
    stats['Description'] = language_data['units']['descriptions'][internal_name]
    gather_stats(stats, table)

    return stats

def gather_stats(stats, table):
    stats['Metalcost'] = table['metalcost']
    stats['Energycost'] = table['energycost']
    stats['Buildtime'] = table['buildtime'] / 100
    stats['Health'] = table['health']
    stats['Speed'] = table['speed']
    stats['Sight'] = table['sightdistance']

    if table['workertime']:
        stats['Buildpower'] = table['workertime']

    if table['buildoptions']:
        buildoptions = list()
        for item in sorted(table['buildoptions'].items()):
            buildoptions.append(item[1])
        stats['buildoptions'] = buildoptions

    if table['weapondefs']:
        weapons = list()
        keys = sorted(table['weapondefs'].keys())
        for key in keys:
            weapondef = table['weapondefs'][key]
            weapon = dict()
            weapon['Name'] = weapondef['weapontype']
            weapon['Range'] = weapondef['range']
            weapon['Damage'] = weapondef['damage']['default']
            weapon['Antiair damage'] = weapondef['damage']['vtol']
            if weapondef['burst']:
                weapon['Burst'] = weapondef['burst']
            weapon['Reload time'] = weapondef['reloadtime']
            weapon['Area of effect'] = weapondef['areaofeffect']
            weapons.append(weapon)
        stats['Weapons'] = weapons

def load_lua_file(path):
    with open(path) as f:
        data = f.read()[7:]
        return lupa.LuaRuntime(unpack_returned_tuples=True).eval(data)

def store(stats):
    with open('units.json', 'w') as f:
        json.dump(stats, f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a json file with stats for BAR units')
    parser.add_argument('path', help='path to BAR repo')
    args = parser.parse_args()
    path = os.path.expanduser(args.path)

    with open(path + '/language/en/units.json') as f:
        language_data = json.load(f)

    iter_units(path)
