import streamlit as st
import pandas as pd
import plotly.express as px
from helpers.coins import *
from helpers.functions import *
from datetime import datetime

def main():
    st.title('🪙 Coins Analysis 🪙')
    path = './data/coins/coins.csv'
    df = get_data(path).pipe(tweak_df)
      
    st.write(f'This page contains the analysis of coins sink and source since {df.date.min().date()}.')
    right, left = st.columns(2)
    start_date = right.date_input('Start date', df.date.min().date())
    end_date = left.date_input('End date', df.date.max().date())
    
    if start_date and end_date:
        # Daily coins flow
        st.subheader('Daily Coins Flow', divider='rainbow')
        daily_coins =  df.groupby(['date','event'])['coins'].sum().reset_index()
        daily_coins = daily_coins[(daily_coins.date.dt.date >= start_date) & (daily_coins.date.dt.date <= end_date)]
        container = st.container()
        with container:
            fig = px.bar(daily_coins, x='date', y='coins',color='event',barmode="group")
            fig.update_layout(legend=dict(yanchor="top", xanchor="left"))
            st.plotly_chart(fig, theme='streamlit',use_container_width=True)
            csv1 = convert_df(daily_coins)
            st.download_button(
                        label="Download data",
                        data=csv1,
                        file_name="coins_daily_usage.csv",
                        mime="text/csv"
                    )
                
        # Coins collected y source
        st.subheader('Coins collected by source', divider='rainbow')
        n = st.slider('Choose the number of coins sources to display', min_value=1, max_value=len(df[(df.event == 'reward:collected') ].reward_reason.unique()), value=5)   
        filtered_df = df[(df.event == 'reward:collected') 
                         & (df.date.dt.date >= start_date) 
                         & (df.date.dt.date <= end_date)].assign(reward_reason = lambda df_:df_.reward_reason.pipe(top_n, n))
        container = st.container()
        with container:
            coins_source = filtered_df.groupby(['reward_reason'])['coins'].sum().reset_index()
            pie = px.pie(coins_source, values='coins', names='reward_reason')
            pie.update_layout(legend=dict(yanchor="top", xanchor="left"))
            st.plotly_chart(pie, theme='streamlit',use_container_width=True)
            csv2 = convert_df(coins_source)
            st.download_button(
                        label="Download data",
                        data=csv2,
                        file_name="coins_source.csv",
                        mime="text/csv"
                    )
        container = st.container()
        with container:
            coins_source_daily = filtered_df.groupby(['date','reward_reason'])['coins'].sum().reset_index()
            line = px.line(coins_source_daily, x='date',y='coins',color='reward_reason')
            line.update_traces(mode='markers+lines')
            line.update_layout(legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    title='Reward source'
                        ))
            st.markdown('### **Daily coins rewards by source**')
            st.plotly_chart(line, theme='streamlit',use_container_width=True)
            csv3 = convert_df(coins_source_daily)
            st.download_button(
                        label="Download data",
                        data=csv3,
                        file_name="coins_source_daily.csv",
                        mime="text/csv"
                    )
        
        # Coins spent 
        st.subheader('Coins spent by source', divider='rainbow')
        n = st.slider('Choose the number of coins sink placements to display', min_value=1, max_value=len(df[(df.event == 'reward:used') ].reward_reason.unique()), value=5)
        filtered_df = df[(df.event == 'reward:used') 
                    & (df.date.dt.date >= start_date) 
                    & (df.date.dt.date <= end_date)].assign(reward_reason = lambda df_:df_.reward_reason.pipe(top_n, n),
                                                            coins = lambda x: x.coins *(-1))
        container = st.container()
        with container:
            coins_sink= filtered_df.groupby(['reward_reason'])['coins'].sum().reset_index()
            pie = px.pie(coins_sink, values='coins', names='reward_reason')
            pie.update_layout(legend=dict(yanchor="top", xanchor="left"))
            st.plotly_chart(pie, theme='streamlit',use_container_width=True)
            csv4 = convert_df(coins_sink)
            st.download_button(
                        label="Download data",
                        data=csv4,
                        file_name="coins_sink.csv",
                        mime="text/csv"
                    )
            
        container = st.container()
        with container:
            coins_sink= filtered_df.groupby(['date','reward_reason'])['coins'].sum().reset_index()
            bar = px.line(coins_sink, y='coins', x='date',color='reward_reason',log_y=True)
            bar.update_layout(legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    title='Sink'
                        ))
            st.markdown('### **Daily coins spent by placement**')
            st.plotly_chart(bar, theme='streamlit',use_container_width=True)
            csv5 = convert_df(coins_sink)
            st.download_button(
                        label="Download data",
                        data=csv5,
                        file_name="coins_sink_daily.csv",
                        mime="text/csv"
                    )
    else:
        st.error('Choose a date range')
    
    ab = st.checkbox('AB Test')
    if ab:
        st.header('Coins usage by variant')
        filtered_df = df[(df.event == 'reward:used') 
                    & (filtered_df.ab_test_variants != 'No AB Test')
                    & (df.date.dt.date >= start_date) 
                    & (df.date.dt.date <= end_date)].assign(coins = lambda x: x.coins *(-1))
        AB_summary = filtered_df.groupby(['ab_test_variants','reward_reason']).agg({'coins':'sum'
                                                       ,'event': 'count',
                                                       'progress_id':'nunique'
                                                       }).rename(columns={'event':'purchases', 'progress_id':'users'}).reset_index(drop=False)
        control = AB_summary[AB_summary.ab_test_variants=='Control'].loc[:,'reward_reason':'users'].sort_values('coins',ascending=False).set_index('reward_reason')
        treatment = AB_summary[AB_summary.ab_test_variants=='Variant A'].loc[:,'reward_reason':'users'].sort_values('coins',ascending=False).set_index('reward_reason')
        
        col1, col2, col3 = st.columns(3)
        
        t_t_coins = treatment['coins'].sum()
        c_t_coins =control['coins'].sum()
        
        spenders_t=filtered_df[filtered_df.ab_test_variants=='Variant A']['progress_id'].nunique()
        spenders_c=filtered_df[filtered_df.ab_test_variants=='Control']['progress_id'].nunique()
        
        coins_purchases_t=treatment['purchases'].sum()
        coins_purchases_c=control['purchases'].sum()
        
        
        col1.metric("Treatment total 🪙", f"{t_t_coins}", f"{round(100*(t_t_coins/c_t_coins)-100,1)} % lift")
        col2.metric("🪙 Spenders",  f"{spenders_t}", f"{round(100*(spenders_t/spenders_c)-100,1)} %")
        col3.metric("🪙 Purchases", f"{coins_purchases_t}", f"{round(100*(coins_purchases_t/coins_purchases_c) -100 ,1)} %")
        
        right, left = st.columns(2)
        right.markdown('**Control group**')
        left.markdown('**Treatment group**')
        right.dataframe(control ,use_container_width=True)
        left.dataframe(treatment ,use_container_width=True)
        st.markdown('### Treatment-Control % difference')
        st.dataframe(round(100*(treatment/control) -100,1),use_container_width=True)
        
        csv6 = convert_df(AB_summary)
        st.download_button(
                        label="Download data",
                        data=csv6,
                        file_name="coins_ab_test.csv",
                        mime="text/csv"
                    )
        

if __name__ == '__main__':
    main()