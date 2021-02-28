import numpy as np


def normalize_tick(df):

    # normalize target high & low values to percent of opening values, create new columns for 'day of week' and 'week of year'
    df['percent_high'] = np.where(df['High'] < 1, df['High'], df['High']/df['Open'])
    df['percent_low']= np.where(df['Low'] < 1, df['Low'], df['Low']/df['Open'])
    df['percent_close']= np.where(df['Close'] < 1, df['Close'], df['Close']/df['Open'])
    df['Date'] = df.index
    df['day_of_week'] = df['Date'].apply(lambda x: x.weekday())
    df['week_num']=df['Date'].dt.isocalendar().week

    df_norm = df

    return df_norm