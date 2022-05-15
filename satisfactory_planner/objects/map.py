# /home/supratik/.steam/debian-installation/steamapps/compatdata/526870/pfx/drive_c/users/steamuser/AppData/Local/FactoryGame/MapData-Export/
# %LOCALAPPDATA%\FactoryGame\MapData-Export
import os
import time
import json
import pandas
import appdirs
import logging
import matplotlib
import pkg_resources
import matplotlib.pyplot as plt

from skimage.transform import resize
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

logger = logging.getLogger(__name__)


class ResourceData:
    '''Contains the data related to resources in game.
    This sources the data from the Map Data mod on Satisfactory Mod Manager.

    @author Supratik Chatterjee
    '''
    _connection = None
    _raw_data = None

    def __init__(self,
                 appdata_location=os.path.expanduser(
                     '~/.steam/debian-installation/steamapps/compatdata/526870/pfx/drive_c/users/steamuser/AppData/Local/'),
                 mapdatafile='ResourceNodes.json',
                 data_location=appdirs.user_data_dir(
                     'satisfactory_planner', 'conceivilize'),
                 filename='resources.csv',
                 db='sqlite:///' + os.path.join(appdirs.user_data_dir(
                     'satisfactory_planner', 'conceivilize'), 'satisfactory_data.sqlite')):
        if not os.path.exists(appdata_location):
            print('The AppData location does not exist. \
                We depend on Map Data Mod, on Satisfactory Mod Manager, and it\'s location. \
                The correct location will contain the folder \'FactoryGame\'')
            os._exit(os.EX_DATAERR)
        try:
            os.makedirs(data_location)
            logger.info('Directories made')
        except:
            pass
        self.mapdata_path = os.path.join(
            appdata_location, 'FactoryGame', 'MapData-Export', mapdatafile)
        self.filepath = os.path.join(appdirs.user_data_dir(
            'satisfactory'), os.path.join(data_location, filename))
        self.db_path = db

    def _process_mapdata(self):
        resources = None
        with open(self.mapdata_path, 'r') as resources_file:
            resources = json.load(resources_file)
        logger.info(self.mapdata_path + ' loaded')
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
        nodes_df['purity'] = nodes_df['purity'].str.lower()
        nodes_df.loc[nodes_df['purity'] == 'inpure', 'purity'] = 'impure'
        nodes_df.to_csv(self.filepath, index=False)
        logger.info('CSV prepared and saved to ' + self.filepath)

    def get_raw(self, force_update: bool = False):
        ''' This provides the raw data for the resources.
        It does not update the prepared CSV, stored in the library directory.
        Using force_update=True will force the update.  

        Sample uses  :  
        1. res_data.show_on_map(nodes_df[nodes_df['name'].isin(['coal', 'iron-ore'])])
        2. res_data.show_on_map(nodes_df, segment_key='name', figsize = [20, 20], s=10)
        3. res_data.show_on_map(res_data.get_cluster_points(['iron-ore'], label = 'iron-clusters'))
        4. 
        @author Supratik Chatterjee
        '''
        if ResourceData._raw_data is not None:
            return ResourceData._raw_data
        if os.path.exists(self.filepath):
            last_updated = os.path.getmtime(self.filepath)
            current_time = time.time()
            if (last_updated - current_time) > 432000 or force_update:
                self._process_mapdata()
        else:
            self._process_mapdata()
        ResourceData._raw_data = pandas.read_csv(self.filepath)
        return ResourceData._raw_data

    def show_on_map(self, df: pandas.DataFrame, x: str = 'x', y: str = 'y', z: str = 'z', x_adjust: int = 1670, y_adjust: int = 1670, min_x=None, min_y=None,
                    s: int = 1, segment_key=None, cmap='viridis', figsize=[10, 10]):
        ''' Show points from a dataframe's x and y columns on map.
        We make use of adjustment factors, that have been manually adjusted, to scale on a background image of
        the actual in-game map.

        This helps us find the nodes quite easily and accurately. As well as show analyzed data points on the map.
        @author Supratik Chatterjee
        '''
        nodes_df = self.get_raw()
        if min_x is None:
            min_x = nodes_df['x'].min()
        if min_y is None:
            min_y = nodes_df['y'].min()
        c_df = df.copy()
        c_df[x] = c_df[x].transform(lambda x: ((x - min_x) / x_adjust) + 24)
        c_df[y] = c_df[y].transform(lambda x: ((x - min_y) / y_adjust) + 35)
        # display plots
        plt.rcParams['figure.figsize'] = figsize
        im = plt.imread(pkg_resources.resource_filename(
            'satisfactory_planner', 'res/images/Map.webp'))
        im = resize(im, (450, 450))
        if segment_key is None:
            plt.scatter(x=c_df[x], y=c_df[y], s=s, c='r')
        else:
            colors = matplotlib.cm.get_cmap(cmap)
            ctr = 1
            fig, ax = plt.subplots()
            entries = df[segment_key].unique()
            for entry in entries:
                p_df = c_df[c_df[segment_key] == entry]
                ax.scatter(p_df[x], p_df[y], color=[colors(
                    ctr / len(entries))], label=entry, s=s)
                ctr += 1
            ax.legend(loc=4)
        plt.imshow(im)
        plt.show()

    def get_cluster_points(self, resources, max_count=12, label=None):
        nodes_df = self.get_raw()
        p_df = nodes_df[nodes_df['name'].isin(resources)]

        def apply_bias(x):
            if x['purity'] == 'Inpure':
                # print('Inpure')
                x['x'] *= 0.25
                x['y'] *= 0.25
            if x['purity'] == 'Normal':
                # print('Normal')
                x['x'] *= 0.5
                x['y'] *= 0.5
            if x['purity'] == 'Pure':
                # print('Pure')
                x['x'] *= 1
                x['y'] *= 1
            return x
        # p_df = p_df.transform(apply_bias, axis=1)
        res_df = p_df[['x', 'y', 'z']]
        del p_df
        if len(res_df) == 0:
            raise Exception("No resources found for list : ", resources)
        kmeans = ResourceData.get_kmeans(res_df, kmax=max_count)
        del res_df
        res_df = pandas.DataFrame(
            kmeans.cluster_centers_, columns=['x', 'y', 'z'])
        res_df['label'] = label
        del kmeans
        return res_df

    @staticmethod
    def get_kmeans(df, kmax=12, debug=False, label='Unlabelled'):
        res = None
        c_max = 0
        c_ind = 0
        # dissimilarity would not be defined for a single cluster, thus, minimum number of clusters should be 2
        for k in range(2, kmax+1 if kmax < len(df) else len(df)):
            kmeans = KMeans(n_clusters=k).fit(df)
            labels = kmeans.labels_
            sil_score = silhouette_score(df, labels, metric='euclidean')
            if debug:
                print('k : ', k, ', silhoutte score : ', sil_score)
            if c_max < sil_score:
                c_max = sil_score
                res = kmeans
        return res
