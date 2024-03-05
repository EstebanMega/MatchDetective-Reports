import streamlit as st
import pandas as pd

def tweak_df(df):
    return (
        df.assign(
        created_date = lambda df_: pd.to_datetime(df_.created_date,format='%Y-%m-%d'),
        date = lambda df_:pd.to_datetime(df_.date,format='%Y-%m-%d'),
        event_time = lambda df_:pd.to_datetime(df_.event_time.str.replace(' UTC',''), format="ISO8601"))
        )

def top_n_pie(df, n=5, default='others'):
    sorted = df.sort_values(by=['coins'], ascending=False)
    return df.reward_reason.where(df.reward_reason.isin(sorted.reward_reason[:n]), default)