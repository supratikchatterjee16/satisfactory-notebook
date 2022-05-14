# /home/supratik/.steam/debian-installation/steamapps/compatdata/526870/pfx/drive_c/users/steamuser/AppData/Local/FactoryGame/MapData-Export/
# %LOCALAPPDATA%\FactoryGame\MapData-Export
import os
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

        for key in resources.keys():
            print(key, len(resources[key]))

    def get_raw(self):
        if ResourceData._raw_data is not None:
            return ResourceData._raw_data
        self._process_mapdata()
        ResourceData._raw_data = pandas.read_csv(self.filepath)
        return ResourceData._raw_data
