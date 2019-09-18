from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn import metrics
import pandas
from glob import glob
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

from Python_Files import rasterops as rops


def create_dataframe(input_file_dir, out_df, pattern='*.tif', exclude_years=()):
    """
    Create dataframe from file list
    :param input_file_dir: Input directory where the file names begin with <Variable>_<Year>, e.g, ET_2015.tif
    :param out_df: Output Dataframe file
    :param pattern: File pattern to look for in the folder
    :param exclude_years: Exclude these years from the dataframe
    :return: Pandas dataframe
    """

    raster_dict = defaultdict(lambda: [])
    file_list = glob(input_file_dir + '/' + pattern)
    for f in file_list:
        sep = f.rfind('_')
        variable, year = f[f.rfind('/') + 1: sep], f[sep + 1: f.rfind('.')]
        if int(year) not in exclude_years:
            raster_arr = rops.read_raster_as_arr(f, get_file=False)
            raster_arr = raster_arr.reshape(raster_arr.shape[0] * raster_arr.shape[1])
            if variable == 'GW':
                raster_arr *= 1233.48 * 1000. / 2.59e+6
            raster_list = raster_arr.tolist()
            raster_dict[variable].append(raster_list)
        # print(len(raster_list))
        # raster_dict['YEAR'].append([year] * len(raster_list))

    for attr in raster_dict.keys():
        arr_list = raster_dict[attr]
        arr_final = []
        for arr in arr_list:
            arr_final = arr_final + arr
        raster_dict[attr] = arr_final

    df = pandas.DataFrame(data=raster_dict)
    df = df.dropna(axis=0)
    df.to_csv(out_df, index=False)
    return df


def rf_regressor(input_df, out_dir, n_estimators=200, random_state=0, test_size=0.2, pred_attr='GW_KS',
                 plot_graphs=False):
    """
    Perform random forest regression
    :param input_df: Input pandas dataframe
    :param out_dir: Output file directory for storing intermediate results
    :param n_estimators: RF hyperparameter
    :param random_state: RF hyperparameter
    :param test_size: RF hyperparameter
    :param pred_attr: Prediction attribute name in the dataframe
    :param plot_graphs: Plot Actual vs Prediction graph
    :return: Random forest model
    """

    y = input_df[pred_attr]
    dataset = input_df.drop(columns=[pred_attr])
    X = dataset.iloc[:, 0: len(dataset.columns)].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
    regressor = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state)
    regressor.fit(X_train, y_train)
    y_pred = regressor.predict(X_test)

    feature_imp = " ".join(str(np.round(i, 3)) for i in regressor.feature_importances_)
    train_score = np.round(regressor.score(X_train, y_train), 3)
    test_score = np.round(regressor.score(X_test, y_test), 3)
    mae = np.round(metrics.mean_absolute_error(y_test, y_pred), 3)
    rmse = np.round(np.sqrt(metrics.mean_squared_error(y_test, y_pred)), 3)

    if plot_graphs:
        plt.plot(y_pred, y_test, 'ro')
        plt.xlabel('GW_Predict')
        plt.ylabel('GW_Actual')
        plt.show()

    df = {'N_Estimator': [n_estimators], 'Random_State': [random_state], 'F_IMP': [feature_imp],
          'Train_Score': [train_score], 'Test_Score': [test_score], 'MAE': [mae], 'RMSE': [rmse]}
    print(df)
    df = pandas.DataFrame(data=df)
    df.to_csv(out_dir + 'RF_Results.csv', mode='a', index=False)
