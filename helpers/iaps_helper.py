import pandas as pd
import requests


# Get exchange rates
def fetch_exchange_rates():
    try:
        response = requests.get('https://www.floatrates.com/daily/usd.json')
        response.raise_for_status()
        print(response)
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    response_json = response.json()
    currencies = {response_json[i]['code']:response_json[i]['rate'] for i in response_json}
    currencies['USD'] =1
    return currencies

# Transform IAP's DataFrame
def tweak_df(df):
    currencies=fetch_exchange_rates()
    return (df.assign(
            revenue_usd = lambda df_: (df_.local_revenue_gross
            / df_.local_currency_code.map(currencies)).fillna(0).round(2), 
            event_time = lambda df_: pd.to_datetime(df_.event_time),
            date = lambda df_:pd.to_datetime(df_.date, format='%Y-%m-%d'),
            install_date = lambda df_: pd.to_datetime(df_.install_date, format='%Y-%m-%d'),
            install_datetime = lambda df_: pd.to_datetime(df_.install_datetime),
            month = lambda df_:df_.date.dt.strftime('%Y-%m')
            ).loc[:,['event_time', 'client_country', 'date', 
                    'install_date','progress_id','retention_day',
                    'transaction_id','price','local_currency_code',
                    'local_revenue_gross','sku','ab_test_variants','revenue_usd','month']])