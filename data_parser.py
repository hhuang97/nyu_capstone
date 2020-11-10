import pandas as pd
import pickle


_RAW_DATA_FILE = 'data/CLO_Data.xlsx'
_PICKLED_DATA_FILE = 'data/all_data.p'
_STRESS_2016 = 'data/stress_2018.p'
_STRESS_2020 = 'data/stress_2020.p'


def process_data():
    main_df = pd.read_excel(_RAW_DATA_FILE, sheet_name='Sheet1')
    main_df = main_df.set_index('Date')
    with open(_PICKLED_DATA_FILE, 'wb') as f:
        pickle.dump(main_df, f)
    stress_2016 = main_df[(main_df.index > '2018-1-1') & (main_df.index < '2018-12-31')]
    stress_2020 = main_df[(main_df.index > '2020-3-1') & (main_df.index < '2020-10-31')]
    with open(_STRESS_2016, 'wb') as f:
        pickle.dump(stress_2016, f)
    with open(_STRESS_2020, 'wb') as f:
        pickle.dump(stress_2020, f)


def get_2018_data():
    with open(_STRESS_2016, 'rb') as f:
        df_2016 = pickle.load(f)
    return df_2016


def get_2020_data():
    with open(_STRESS_2020, 'rb') as f:
        df_2020 = pickle.load(f)
    return df_2020


def get_all_data():
    with open(_PICKLED_DATA_FILE, 'rb') as f:
        df_all = pickle.load(f)
    return df_all


if __name__ == '__main__':
    process_data()
    x = get_2018_data()
    y = get_2020_data()
    z = get_all_data()
    print('done')
