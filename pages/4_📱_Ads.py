import streamlit as st
import numpy as np
import pandas as pd
import os
import plotly.express as px
from helpers.functions import *
from helpers.ads import tweak_ads, create_daily_plot

def main():
  path1 = './data/ads/ads.csv'
  path2 = './data/ads/ads2.csv'
  path3= './data/ads/ads_dau.csv'

  df=pd.concat([get_data(path1), get_data(path2)]).pipe(tweak_ads)
  dau = get_data(path3).assign(date=lambda df_: pd.to_datetime(df_.date))
  st.title('Ads by Placement Analysis')
  st.write('This page contains the analysis of impressions and ad revenue.')
  
  right, left = st.columns(2)
  start_date = right.date_input('Start date', df.date.min().date())
  end_date = left.date_input('End date', df.date.max().date())
  df=df[(df.date.dt.date >= start_date) 
    &(df.date.dt.date <= end_date) ]
  dau=dau[(dau.date.dt.date >= start_date) 
    &(dau.date.dt.date <= end_date) ]
  
  st.header('DAU', divider='rainbow')
  fig0=px.line(data_frame=dau,x='date',y='users')
  fig0.update_traces(mode='markers+lines')
  fig0.update_layout(legend=dict(
                  orientation="h",
                  yanchor="bottom",
                  y=1.02,
                  xanchor="right",
                  x=1,
                      )) 
  st.plotly_chart(fig0,use_container_width=True)
  
  st.header('Impressions', divider='rainbow')
  fig01=create_daily_plot(df=df, groups=['date'], metric='event', function='count')
  st.plotly_chart(fig01,use_container_width=True)
  
  st.header('Ads Revenue', divider='rainbow')
  revenue=create_daily_plot(df=df, groups=['date'], metric='revenue', function='sum')
  st.plotly_chart(revenue,use_container_width=True)
  
  st.header('Impressions/user', divider='rainbow')
  fig02=create_daily_plot(df=df, groups=['date'], metric='event', function='count',dau=dau)
  st.plotly_chart(fig02,use_container_width=True)
  
  st.header('ARPAU', divider='rainbow')
  arpu=create_daily_plot(df=df, groups=['date'], metric='revenue', function='sum',dau=dau)
  st.plotly_chart(arpu,use_container_width=True)
                                                                                                          
  st.header('Ads Revenue by placement', divider='rainbow')
  fig1=create_daily_plot(df=df, groups=['date', 'ad_placement'], metric='revenue', function='sum')
  st.plotly_chart(fig1,use_container_width=True)   

  st.header('ARPAU', divider='rainbow')
  fig2=create_daily_plot(df=df, groups=['date', 'ad_placement'], metric='revenue', function='sum', dau=dau)
  st.plotly_chart(fig2,use_container_width=True)
  
  st.header('Impressions', divider='rainbow')
  fig3=create_daily_plot(df=df, groups=['date', 'ad_placement'], metric='event', function='count')
  st.plotly_chart(fig3,use_container_width=True)
  
  st.header('Impressions / User', divider='rainbow')
  fig4=create_daily_plot(df=df, groups=['date', 'ad_placement'], metric='event', function='count', dau=dau)
  st.plotly_chart(fig4,use_container_width=True)

      # Variants comparison
  modify = st.checkbox("AB Test",value=False)
  if modify:
    col1, col2 = st.columns(2)
    impressions_treatment = df[df.ab_test_variants=='Variant A'].event.count()
    impressions_control = df[df.ab_test_variants=='Control'].event.count()
    
    total_revenue_treatment = df[df.ab_test_variants=='Variant A'].revenue.sum()
    total_revenue_control = df[df.ab_test_variants=='Control'].revenue.sum()
    
    col1.metric('**Ads Revenue Treatment group**', f'{round(total_revenue_treatment,2)} $', f'{round((total_revenue_treatment/total_revenue_control-1)*100,2)} %')
    col2.metric('**Ads Revenue Control group**', f'{round(total_revenue_control,2)} $', f'{round((total_revenue_control/total_revenue_treatment-1)*100,2)} %')
    
    col1.metric('**Impressions Treatment group**', f'{round(impressions_treatment,2)} 📲', f'{round((impressions_treatment/impressions_control-1)*100,2)} %')
    col2.metric('**Impressions Control group**', f'{round(impressions_control,2)} 📲', f'{round((impressions_control/impressions_treatment-1)*100,2)} %')
    
    st.header('Ads Revenue by AB Test variant', divider='rainbow')
    fig1=create_daily_plot(df=df, groups=['date', 'ab_test_variants'], metric='revenue', function='sum')
    st.plotly_chart(fig1,use_container_width=True)
    
    st.header('ARPAU AB Test', divider='rainbow')
    df_arpau = df.groupby(['date','ab_test_variants'])['revenue'].sum().reset_index(drop=False).merge(dau, on='date', how='left')
    df_arpau['ARPAU'] = (np.where(df_arpau
                                  .ab_test_variants== 'Variant A', 
                                  round(df_arpau.revenue/df_arpau.treatment,2), 
                                  np.where(df_arpau.ab_test_variants == 'Control', 
                                           round(df_arpau.revenue/df_arpau.control,2),
                                           round(df_arpau.revenue/df_arpau.users,2)))
                         )
    line=px.line(df_arpau, x='date',y='ARPAU',color='ab_test_variants')
    line.update_traces(mode='markers+lines')
    line.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
    ))
    st.plotly_chart(line,use_container_width=True)
    
    st.header('Impressions AB Test', divider='rainbow')
    fig2=create_daily_plot(df=df, groups=['date', 'ab_test_variants'], metric='event', function='count')
    st.plotly_chart(fig2,use_container_width=True)
    
    st.header('Impressions/User AB Test', divider='rainbow')
    df_arpau = df.groupby(['date','ab_test_variants'])['event'].count().reset_index(drop=False).merge(dau, on='date', how='left')
    df_arpau['Impressions/Users'] = (np.where(df_arpau
                                    .ab_test_variants== 'Variant A', 
                                    round(df_arpau.event/df_arpau.treatment,2), 
                                    np.where(df_arpau.ab_test_variants== 'Control', 
                                            round(df_arpau.event/df_arpau.control,2),
                                            round(df_arpau.event/df_arpau.users,2)))
                                    )
    line=px.line(df_arpau, x='date',y='Impressions/Users',color='ab_test_variants')
    line.update_traces(mode='markers+lines')
    line.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
    ))
    st.plotly_chart(line,use_container_width=True)

if __name__ == '__main__':
    main()