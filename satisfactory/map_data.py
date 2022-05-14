# /home/supratik/.steam/debian-installation/steamapps/compatdata/526870/pfx/drive_c/users/steamuser/AppData/Local/FactoryGame/MapData-Export/
# %LOCALAPPDATA%\FactoryGame\MapData-Export
import os
import time
import json
import pandas


class ResourceData:
    _connection = None
    _raw_data = None

    def __init__(self,
                 appdata_location=os.path.expanduser(
                     '~/.steam/debian-installation/steamapps/compatdata/526870/pfx/drive_c/users/steamuser/AppData/Local/'),
                 mapdatafile='ResourceNodes.json',
                 data_location=os.path.join('res', 'data'),
                 filename='resources.csv',
                 db='sqlite:///' + os.path.join('res', 'data', 'satisfactory_data.sqlite')):
        if not os.path.exists(appdata_location):
            print('The AppData location does not exist. \
                We depend on Map Data Mod, on Satisfactory Mod Manager, and it\'s location. \
                The correct location will contain the folder \'MapData-Export\'')
            os._exit(os.EX_DATAERR)
        try:
            os.makedirs(data_location)
        except:
            pass
        self.mapdata_path = os.path.join(
            appdata_location, 'MapData-Export', mapdatafile)
        self.filepath = os.path.join(data_location, filename)
        self.db_path = db

    def _process_mapdata(self):
        resources = None
        with open(self.mapdata_path, 'r') as resources_file:
            resources = json.load(resources_file)

        # for key in resources.keys():
        #     print(key, len(resources[key]))
        # Transform all values into the format specified below
        # name purity x y z
        nodes_list = []
        for node in resources['nodes']:
            res = {}
            res['name'] = node['item']['name'].lower().replace(' ', '-')
            res['purity'] = node['purity'][3:]
            res.update(node['location'])
            nodes_list.append(res)

        for core in resources['frackingCores']:
            res = {}
            res['name'] = core['item']['name'].lower().replace(' ', '-')
            res['purity'] = None
            res.update(core['location'])
            nodes_list.append(res)

        for geyser in resources['geysers']:
            res = {}
            res['name'] = geyser['item']['name'].lower().replace(' ', '-')
            res['purity'] = geyser['purity'][3:]
            res.update(geyser['location'])
            nodes_list.append(res)

        for satellite in resources['frackingSatellites']:
            res = {}
            res['name'] = satellite['item']['name'].lower().replace(' ', '-') + \
                '-satellite'
            res['purity'] = satellite['purity'][3:]
            res.update(satellite['location'])
            nodes_list.append(res)

        nodes_df = pandas.DataFrame(nodes_list)
        del nodes_list
        nodes_df.to_csv(self.filepath, index=False)

    def get_raw(self):
        if ResourceData._raw_data is not None:
            return ResourceData._raw_data
        if os.path.exists(self.filepath):
            last_updated = os.path.getmtime(self.filepath)
            current_time = time.time()
            if (last_updated - current_time) > 432000:
                self._process_mapdata()
        else:
            self._process_mapdata()
        ResourceData._raw_data = pandas.read_csv(self.filepath)
        return ResourceData._raw_data
