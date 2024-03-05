import streamlit as st
import time
import numpy as np
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
from helpers.iaps_helper import *
from helpers.functions import get_data, convert_df
from pandas.api.types import (
    is_object_dtype,
)

st.set_page_config(page_title="IAP's Report", page_icon="📈")


# Ger data and preprocess date columns
path = './data/iaps/iaps.csv'
df = get_data(path).pipe(tweak_df) 
df2 = df.copy()       
            
st.markdown("# IAP's Report")
st.sidebar.header("IAPs since 2023-12-01")
st.write(
    """The following report shows the evolution of IAP's in the last few months"""
)
st.markdown("""
            ### **Insights**
            - We can see a revenue spike on the 4th-6th of each month.
            - Average revenue has increased in the last versions. 
            - We are having a considerable higher number of IAP's compared to december.
         """)
right, left = st.columns(2)
start_date = right.date_input('Start date', df.date.min().date())
end_date = left.date_input('End date', df.date.max().date())
df=df[(df.date.dt.date >= start_date) 
      &(df.date.dt.date <= end_date) ]

# Gross revenue 
monthly = st.checkbox('Monthly aggregation')
if monthly:
    aggregation ='month'
else:
    aggregation = 'date'
    
selection = st.selectbox(label='Select metric' ,options=['Revenue', 'Number of purchases'])
d_revenue = df.groupby(aggregation)['revenue_usd'].agg(['sum','count']).reset_index(drop=False).rename(columns={'sum': 'Revenue USD', 'count':'Number of purchases'})
if selection =='Revenue':
    st.subheader(f'IAPs gross Revenue USD ({aggregation})',divider='rainbow')
    fig = px.bar(d_revenue, x=aggregation, y = 'Revenue USD' )
    chart = st.plotly_chart(fig,theme='streamlit',use_container_width=True)
    
elif selection=='Number of purchases':
    st.subheader(f'Number of purchases ({"daily" if aggregation=="date" else "monthly"})',divider='rainbow')
    fig = px.bar(d_revenue, x=aggregation, y = 'Number of purchases' )
    chart = st.plotly_chart(fig,theme='streamlit',use_container_width=True)
    
csv = convert_df(d_revenue)
st.download_button(
                label="Download data",
                data=csv,
                file_name=f'iaps_revenue_{"daily" if aggregation=="date" else "monthly"}.csv',
                mime="text/csv"
            )

# Purchases figure
st.subheader('Number of purchases by bundle',divider='rainbow')
sku = df.groupby('sku')['progress_id'].count().sort_values(ascending=True)
fig = px.bar(sku,orientation='h')
purchases = st.plotly_chart(fig ,theme='streamlit',use_container_width=True)

# Sku daily
skus = st.multiselect('Choose sku', options=df.sku.unique(), default=df.sku.unique()[0])
sku_daily = df[df.sku.isin(skus)].groupby(['date','sku'])['progress_id'].count().reset_index(drop=False)
fig2 = px.line(sku_daily, x='date', y='progress_id', color='sku')
fig2.update_traces(mode='markers+lines')
fig2.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1,
))
daily_purchases=st.plotly_chart(fig2,theme='streamlit',use_container_width=True)

# Revenue by LTV
rev_ins = round(100*df.groupby('retention_day')['revenue_usd'].sum() /df.revenue_usd.sum(),2)

st.subheader('IAPs Revenue % by retention day',divider='rainbow')
st.metric("IAP's total revenue", f"{round(df['revenue_usd'].sum(),2)} USD",)
st.bar_chart(rev_ins)


# Variants comparison
modify = st.checkbox("AB Test",value=False)
if modify:
    ab_revenue = df[(df.date.dt.date >= start_date) & (df.date.dt.date <= end_date)].copy().groupby(['date','ab_test_variants'])['revenue_usd'].sum().reset_index(drop=False)
    summary = df[(df.date.dt.date >= start_date) & (df.date.dt.date <= end_date)].copy().groupby('ab_test_variants').agg({'revenue_usd':'sum','progress_id':'nunique', 'event_time':'count'}).reset_index(drop=False)
    sku_variant = df[(df.date.dt.date >= start_date) & (df.date.dt.date <= end_date)].copy().groupby(['sku','ab_test_variants'])['progress_id'].count().reset_index(drop=False).sort_values('progress_id', ascending=True)
    sku_variant.columns= ['sku', 'ab_test_variants', 'Purchases']
    summary.columns= ['ab_test_variants', 'Revenue $', 'Buyers','Purchases']
    st.subheader('Gross IAP Revenue USD by variant',divider='rainbow')
    fig=px.bar(data_frame=ab_revenue,x='date', y = 'revenue_usd',color='ab_test_variants')
    fig2 = px.bar(data_frame=sku_variant, y='sku', x='Purchases',orientation='h',barmode='group', color='ab_test_variants')
    # Render graphs
    purchases = st.plotly_chart(fig ,theme='streamlit',use_container_width=True)
    st.plotly_chart(fig2,use_container_width=True)
    st.dataframe(summary,use_container_width=True)

# Inspect Purchases
show_data = st.checkbox("Inspect Data")
if show_data:
    csv = df[['event_time','transaction_id','progress_id','client_country','install_date','price','revenue_usd','local_currency_code','sku','ab_test_variants']].copy()
    st.subheader('IAPs List',divider = 'rainbow')
    st.dataframe(
        csv,
        hide_index=True)

    csv = convert_df(csv)
    st.download_button(
                label="Download data",
                data=csv,
                file_name="Funnel.csv",
                mime="text/csv"
            )

    