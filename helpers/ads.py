import pandas as pd 
import numpy as np
import streamlit as st
import plotly.express as px


def tweak_ads(df: pd.DataFrame) -> pd.DataFrame:
    return (df
            .reset_index(drop=True)
            .assign(event_time = lambda df_:pd.to_datetime(df_.event_time.str.replace('UTC', '').str.strip(), 
                                                                format='ISO8601'),
                    created_cik = lambda df_:pd.to_datetime(df_.created_cik.str.replace('UTC', '').str.strip(), 
                                    format='ISO8601'),
                    date = lambda df_:pd.to_datetime(df_.date),
                    created_date = lambda df_:pd.to_datetime(df_.created_date),
                    install_date = lambda df_:pd.to_datetime(df_.install_date),
                    first_date = lambda df_:pd.to_datetime(df_.first_date),
                    last_interaction_date = lambda df_:pd.to_datetime(df_.last_interaction_date))
            .assign(
                    created_date = lambda df_: df_.created_date.where(df_.created_date != df_.created_date.min(), df_.first_date),
                    install_date = lambda df_: df_.install_date.where(df_.install_date != df_.install_date.min(), df_.first_date),
                    retention_day = lambda df_: ((df_.date - df_.created_date) / np.timedelta64(1,'D')).astype('int')
                    )
            )
    
def create_daily_plot(df: pd.DataFrame, groups: list[str], metric: str, function: list[str],dau:pd.DataFrame =None) -> px.line:
    """
    Create a daily line plot from a pandas DataFrame.
    
    Parameters:
        df (pd.DataFrame): The DataFrame containing the data.
        groups (list[str]): List of column names to group by.
        metric (str): The column name of the metric to plot.
        function (list[str]): List of aggregation functions to apply.
        dau (pd.DataFrame, optional): DataFrame containing daily active users.
        
    Returns:
        px.line: A Plotly line plot.
    """
    try:
        if dau is None:
            y = metric
            grouped = df.groupby(groups).agg({metric: function}).reset_index()      
        else:    
            y=f'{metric}_users'
            grouped = (df
                    .groupby(groups)
                    .agg({metric: function})
                    .reset_index().merge(dau, on='date', how='left')
                    .assign(**{f'{metric}_users':lambda df_: (df_[metric] / df_.users).round(3)})
                    )
        if len(groups) == 2:
            line = px.line(grouped, x=groups[0], y=y, color=groups[1])
        elif len(groups) == 1:
            line = px.line(grouped, x=groups[0], y=y)
 
        line.update_traces(mode='markers+lines')
        line.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ))
        
        return line
    
    except Exception as e:
        print(f"An error occurred: {e}")