import os
import time
import pandas
import appdirs
import logging

logger = logging.getLogger()


class RecipeData:
    DATA_COLUMNS = ['name', 'building', 'prod_1', 'prod_rate_1', 'prod_unit_1', 'prod_2', 'prod_rate_2', 'prod_unit_2', 'ing_1', 'rate_1', 'unit_1',
                    'ing_2', 'rate_2', 'unit_2', 'ing_3', 'rate_3', 'unit_3', 'ing_4', 'rate_4', 'unit_4']
    LIQUIDS = ['water', 'crude-oil', 'nitrogen-gas', 'sulfuric-acid', 'fuel', 'biofuel',
               'nitric-acid', 'liquid-biofuel', 'heavy-oil-residue', 'alumina-solution']
    _connection = None
    _raw_data = None

    def __init__(self,
                 base_url: str = 'https://satisfactory.fandom.com/wiki/',
                 url_extensions=['Constructor', 'Assembler', 'Manufacturer',
                                 'Packager', 'Refinery', 'Blender', 'Smelter', 'Foundry'],
                 data_location=appdirs.user_data_dir(
                     'satisfactory_planner', 'conceivilize'),
                 filename='recipes.csv',
                 db='sqlite:///' + os.path.join(appdirs.user_data_dir(
                     'satisfactory_planner', 'conceivilize'), 'satisfactory_data.sqlite')):
        self.base_url = base_url
        self.url_extensions = url_extensions
        try:
            os.makedirs(data_location)
        except:
            pass
        self.filepath = os.path.join(data_location, filename)
        self.db_path = db

    def __download_recipes(self) -> pandas.DataFrame:
        '''
        Download data from fandom wiki
        @author Supratik Chatterjee
        '''
        logging.info('Downloading recipes')
        final_data = pandas.DataFrame(columns=self.DATA_COLUMNS)
        for extended_url in self.url_extensions:
            logging.info(extended_url + 'Recipes')
            data = pandas.read_html(
                self.base_url+extended_url, match="Recipe Name")
            recipe_data = data[0]
            recipe_data = recipe_data.rename(columns={
                'Recipe Name': 'name', 'Crafting Time (sec)': 'time',
                'Ingredients': 'ings', 'Products': 'prods'
            })
            res = pandas.DataFrame(columns=self.DATA_COLUMNS)
            for _, rowdata in recipe_data.iterrows():
                arr = {k: None for k in self.DATA_COLUMNS}
                arr['name'] = rowdata['name'].lower()
                if arr['name'].endswith('mas'):
                    arr['name'] = arr['name'][:-8]
                arr['building'] = extended_url.lower()
                iter_count = 60 / rowdata['time']  # count of runs per minute
                ings = rowdata['ings'].lower().split('/min')
                ctr = 1
                for ing in ings[:-1]:
                    temp = ing.split('x ')
                    arr['rate_'+str(ctr)] = float(temp[0]) * iter_count
                    arr['ing_'+str(ctr)
                        ] = temp[1].rstrip('0123456789.').replace(' ', '-')
                    arr['unit_'+str(ctr)] = 'items/min' if arr['ing_' +
                                                               str(ctr)] not in self.LIQUIDS else 'm3/min'
                    ctr += 1

                prods = rowdata['prods'].lower().split('/min')
                ctr = 1
                for prod in prods[:-1]:
                    temp = prod.split('x ')
                    arr['prod_rate_'+str(ctr)] = float(temp[0]) * iter_count
                    arr['prod_'+str(ctr)
                        ] = temp[1].rstrip('0123456789.').replace(' ', '-')
                    arr['prod_unit_'+str(ctr)] = 'items/min' if arr['prod_' +
                                                                    str(ctr)] not in self.LIQUIDS else 'm3/min'
                    ctr += 1
                res = res.append(arr, ignore_index=True)
                final_data = pandas.concat([final_data, res])
        logging.info('Raw data fetched')
        recipe_data.to_csv(self.filepath, index=False)

    def _process_data(self):
        raw_data = self.get_raw()

        pass

    def get_raw(self):
        '''
        Get the raw data from the csv file
        @author Supratik Chatterjee
        '''
        if RecipeData._raw_data is not None:
            return RecipeData._raw_data
        if os.path.exists(self.filepath):
            last_updated = os.path.getmtime(self.filepath)
            current_time = time.time()
            if (last_updated - current_time) > 432000:
                self.__download_recipes()
        else:
            self.__download_recipes()
        RecipeData._raw_data = pandas.read_csv(self.filepath)
        return RecipeData._raw_data
