from sklearn.ensemble import RandomForestRegressor as rfr
from sklearn.model_selection import train_test_split as tts
from sklearn import metrics
import pandas
from glob import glob
import numpy as np

from Python_Port import rasterops as rops


def create_dataframe(input_file_dir, pattern='*.tif'):
    """
    Create dataframe from file list
    :param input_file_dir: Input directory where the file names begin with <Variable>_<Year>, e.g, ET_2015.tif
    :param pattern: File pattern to look for in the folder
    :return: Pandas dataframe
    """

    raster_dict = {}
    file_list = glob(input_file_dir + '/' + pattern)
    print(file_list)
    for f in file_list:
        sep = f.rfind('_')
        variable, year = f[f.rfind('/') + 1: sep], f[sep + 1: f.rfind('.')]
        raster_arr = rops.read_raster_as_arr(f, get_file=False)
        raster_arr = raster_arr.reshape(raster_arr.shape[0] * raster_arr.shape[1])
        if variable == 'URBAN':
            raster_arr[np.isnan(raster_arr)] = 0
        raster_dict[variable] = raster_arr

    return pandas.DataFrame(data=raster_dict)


def rf_regressor(input_df, outfile_path):
    """
    Perform random forest regression
    :param input_df: Input pandas dataframe
    :param outfile_path: Output file path for storing intermediate results
    :return: Random forest model
    """

    input_df = input_df.dropna()
    input_df.to_csv(outfile_path, index=False)












