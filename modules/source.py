import os
import json
import pandas

import requests
from bs4 import BeautifulSoup


columns = ['name', 'building', 'prod_1', 'prod_rate_1', 'prod_unit_1', 'prod_2', 'prod_rate_2', 'prod_unit_2', 'ing_1', 'rate_1', 'unit_1', 
           'ing_2', 'rate_2', 'unit_2', 'ing_3', 'rate_3', 'unit_3', 'ing_4', 'rate_4', 'unit_4']
liquids = ['water', 'crude-oil', 'nitrogen-gas', 'sulfuric-acid', 'fuel', 'biofuel', 'nitric-acid', 'liquid-biofuel', 'heavy-oil-residue', 'alumina-solution']

def download_recipes(base_url:str = 'https://satisfactory.fandom.com/wiki/',  extended_url:str = 'Constructor') -> pandas.DataFrame:
    # rest_req = requests.get(base_url+extended_url)
    # soup = BeautifulSoup(rest_req.text, "html.parser")
    # tables = soup.find_all("table", class_="wikitable")
    # recipes_table = tables[0]
    global columns, liquids
    data = pandas.read_html(base_url+extended_url, match="Recipe Name")
    recipe_data = data[0]
    recipe_data = recipe_data.rename(columns={'Recipe Name':'name', 'Crafting Time (sec)': 'time', 'Ingredients' : 'ings', 'Products':'prods'})
    res = pandas.DataFrame(columns=columns)
    for _index_, rowdata  in recipe_data.iterrows():
        arr = {k:None for k in columns}
        arr['name'] = rowdata['name'].lower()
        if arr['name'].endswith('mas'):
            arr['name'] = arr['name'][:-8]
        arr['building'] = extended_url.lower()
        iter_count = 60 / rowdata['time'] # count of runs per minute
        ings = rowdata['ings'].lower().split('/min')
        ctr = 1
        for ing in ings[:-1]:
            temp = ing.split('x ')
            arr['rate_'+str(ctr)] = float(temp[0]) * iter_count
            arr['ing_'+str(ctr)] = temp[1].rstrip('0123456789.').replace(' ', '-')
            arr['unit_'+str(ctr)] = 'items/min' if arr['ing_'+str(ctr)] not in liquids else 'm3/min'
            ctr += 1
        
        prods = rowdata['prods'].lower().split('/min')
        ctr = 1
        for prod in prods[:-1]:
            temp = prod.split('x ')
            arr['prod_rate_'+str(ctr)] = float(temp[0]) * iter_count
            arr['prod_'+str(ctr)] = temp[1].rstrip('0123456789.').replace(' ', '-')
            arr['prod_unit_'+str(ctr)] = 'items/min' if arr['prod_'+str(ctr)] not in liquids else 'm3/min'
            ctr += 1
        res = res.append(arr, ignore_index = True)
    return res

def recipes_from_wiki(filepath:str='download_recipes.csv') -> pandas.DataFrame :
    recipe_data = pandas.DataFrame(columns=columns)
    buildings = ['Constructor', 'Assembler', 'Manufacturer', 'Packager', 'Refinery', 'Blender', 'Smelter', 'Foundry']
    url = 'https://satisfactory.fandom.com/wiki/'
    for building in buildings:
        temp = download_recipes(base_url=url, extended_url = building)
        recipe_data = pandas.concat([recipe_data, temp])
    recipe_data.to_csv(filepath, index=False)
    return recipe_data