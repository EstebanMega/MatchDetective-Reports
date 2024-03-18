import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import plotly.express as px
from urllib.error import URLError
from helpers.functions import *
from helpers.funnel_helper import *
        
def main():
    path = './data/funnel/funnel.csv'
    df= get_data(path)
    max_users = df.users.max()
    df['Users Percentage %'] = df['users'].apply(lambda x: round(100* (x/max_users) ,2))
    df['Step'] = df.apply(lambda x: create_funnel_step(x),axis=1)
    incent_data = df[df.event != "app:init:completed"]
    max_incent = incent_data['incent_users'].max()
    max_non_incent = incent_data['non_incent_users'].max()
    incent_data['Incent Users Percentage %'] = df['incent_users'].apply(lambda x: round(100* (x/max_incent) ,2))
    incent_data['Non Incent Users Percentage %'] = df['non_incent_users'].apply(lambda x: round(100* (x/max_non_incent) ,2))
    incent_data['Step'] = df.apply(lambda x: create_funnel_step(x),axis=1)
    
    st.title('Match Detective Funnel')
    st.markdown("""**Description:** 
                The following report analizes the number of users who reach a certain step on the game. 
                We separate the funnels in 3 main parts tutorial funnel, levels funnel and progression funnel.
                """)
    st.header('Tutorial Funnel', divider='rainbow')
    column1, column2, column3 = st.columns(3)
    slider1 = column1.number_input('Min Level', min_value=1,max_value=50,value=1)
    slider2 = column2.number_input('Max Level', min_value=1,max_value=50,value=50)
    min_percentage = column3.number_input('Min percentage', value=9)
    steps_df =df[(df.level >= slider1) & 
                 (df.level <= slider2) &
                 (df['Users Percentage %']  >= min_percentage)]
    steps_df = (
        steps_df[steps_df
                 .event.isin(['app:init:completed', 
                              'button:clicked']) & 
                 steps_df
                 .feature.isin([np.nan, 
                                'tutorial', 
                                'gameplay_tutorial'])]
        .sort_values(['level','Users Percentage %'],ascending=[True,False])
        )
    
    fig = px.funnel(data_frame=steps_df, x='Users Percentage %', y='Step',hover_data ='users')
    st.plotly_chart(fig,use_container_width=True)
    
    csv = convert_df(steps_df.reset_index(drop=True))
    st.download_button(
        label="Download data",
        data=csv,
        file_name="steps_df.csv",
        mime="text/csv"
        )
    
    st.header('Levels Funnel', divider='rainbow')
    column1, column2= st.columns(2)
    min_percentage = column1.number_input(label = "Minimum percentage", value=10)
    events=column2.multiselect('Choose events', options=['app:init:completed', 'level:started', 'level:completed'],default='level:started')
    slider1,slider2 = st.slider('Select levels', min_value=1,max_value=425, value=(1, 50))
    case_scene_df =df[(df.level >= slider1) & 
                 (df.level <= slider2) &
                 (df['Users Percentage %']  >= min_percentage)]
    case_scene_df = (
        case_scene_df[case_scene_df
                 .event.isin(events)]
        .sort_values(['level','Users Percentage %'],ascending=[True,False])
        )
    
    fig = px.funnel(data_frame=case_scene_df, x='Users Percentage %', y='Step',hover_data ='users')
    st.plotly_chart(fig,use_container_width=True)
    
    csv = convert_df(case_scene_df[['Step','users', 'Users Percentage %']].reset_index(drop=True))
    st.download_button(
        label="Download data",
        data=csv,
        file_name="levels.csv",
        mime="text/csv"
        )
    
    st.header('Levels Funnel incent vs non incent', divider='rainbow')
    column1, column2= st.columns(2)
    min_percentage = column1.number_input(label = "Min percentage", value=10)
    events=column2.multiselect('Choose events', options=['level:started', 'level:completed'],default='level:started')
    slider1,slider2 = st.slider('Choose levels', min_value=1,max_value=425, value=(1, 50))
    incent = (incent_data
              [['Step', 'level','event','Incent Users Percentage %', 'Non Incent Users Percentage %']]
              .melt(id_vars=['Step', 'level','event'], 
                    value_vars = ['Incent Users Percentage %', 'Non Incent Users Percentage %'])
              )
    incent =incent[(incent.level >= slider1) & 
                 (incent.level <= slider2) &
                 (incent['value']  >= min_percentage)]
    incent = (
        incent[incent
                 .event.isin(events)]
        .sort_values(['level','value'],ascending=[True,False])
        )
    
    fig = px.funnel(data_frame=incent, x='value', y='Step', color='variable')
    st.plotly_chart(fig,use_container_width=True)
    
    csv = convert_df(incent)
    st.download_button(
        label="Download data",
        data=csv,
        file_name="incent_levels.csv",
        mime="text/csv"
        )    
     
    
    if st.checkbox('Raw Data', value=False):
        st.header('Funnel Data', divider='rainbow')
        selected_columns = st.multiselect('Select Columns:', 
                                    list(df.columns), default= ['Step','users','Users Percentage %']
                                            )
        if not selected_columns:
            st.error('Please select at least one column.')
        else:
            filtered_df = df[selected_columns]
            filtered_df = filter_dataframe(filtered_df)
            filtered_df.style.highlight_null(props="color: transparent;")
            filtered_df.style.format("{:.2%}")
            
            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True
                )       
            csv = convert_df(filtered_df.reset_index(drop=True))
            st.download_button(
                label="Download data",
                data=csv,
                file_name="Funnel.csv",
                mime="text/csv"
            )
            
if __name__ == '__main__':
    main()