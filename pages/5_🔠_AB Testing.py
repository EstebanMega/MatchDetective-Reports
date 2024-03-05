import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
from ab_test.bootstrapAB import BootstrapAB

def main():

    path = './data/ab_test/ab_test.csv'
    ab_test=pd.read_csv(path)
    ab_test = (ab_test
            [['progress_id', 'install_date', 'ab_test_variants', 'n_days_active','n_levels', 
                'boosters_used', 'coins_used', 'n_purchases', 'ad_revenue','ads_watched']]
            [ab_test.ab_test_variants
                .isin(['Control', 'Variant A'])
                ].reset_index(drop=True)
            )

    control_size = ab_test[ab_test.ab_test_variants=='Control']['progress_id'].nunique()
    treatment_size = ab_test[ab_test.ab_test_variants=='Variant A']['progress_id'].nunique()
    
    st.title("AB Testing report")
    
    column1, column2=st.columns(2)
    
    column1.metric("Control group size", control_size)
    column2.metric("Treatment group size", value=treatment_size)
    
    metric = st.selectbox('Select metric to test', options = ['n_days_active','n_levels', 
                'boosters_used', 'coins_used', 'n_purchases', 'ad_revenue', 'retention','ads_watched'])
    
    if metric not in ['retention']:
        st.subheader(f'Metric to analize: "{metric}"', divider='rainbow')
        column1, column2=st.columns(2)
        control_metric_mean = ab_test[ab_test.ab_test_variants=='Control'][metric].mean()
        treatment_metric_mean = ab_test[ab_test.ab_test_variants=='Variant A'][metric].mean()
        table = ab_test[ab_test.ab_test_variants.isin(['Control','Variant A'])].groupby('ab_test_variants')[metric].mean().reset_index(drop=False)
        
        fig = px.bar(table, x='ab_test_variants',y=metric)
        column1.metric('Treatment comparison',value = round(control_metric_mean,2))
        column2.metric('Treatment comparison',value = round(treatment_metric_mean,2), delta= f'{round((treatment_metric_mean/control_metric_mean -1) *100,2)}%')
        st.plotly_chart(fig, use_container_width=False)
        
    method = st.selectbox('Choose AB testing method',options=['Bootstrap', 'Parametric', 'Bayesian'])
    
    if method in ['Bootstrap']:
        ab = BootstrapAB(ab_test[ab_test.ab_test_variants =='Control'],ab_test[ab_test.ab_test_variants =='Variant A'], metric_name=metric)
        iterations = st.selectbox('Choose number of iterations',options = [1000,10000,100000])
        if st.button("Run Experiment"):
            st.info('Creating bootstrap Distributions')
            control, treatment = ab.calculate_bootstrap_means(n_iterations=iterations)
            diffs = np.array(treatment) - np.array(control)
            observed_difference = np.mean(diffs)
            confidence_interval = np.percentile(diffs, [2.5,97.5])
            series = [control,treatment]
            labels = ['Control', 'Treatment']
            fig = ff.create_distplot(series, labels, bin_size=.2)
            st.subheader(f'Bootstrap Distributions for {metric}')
            st.plotly_chart(fig, use_container_width=True)
            st.success('Bootstrap distributions succesfully created')
            st.subheader(f'Mean Difference Distribution for {metric}')
            diff_fig = px.histogram(diffs,labels='Difference in Mean')
            diff_fig.add_vline(0,line_width=3, line_dash="dash", line_color="green", annotation_text='Zero Line', annotation_position='top left')
            diff_fig.add_vrect(x0=confidence_interval[0], x1=confidence_interval[1],fillcolor="blue", annotation_text="95% confidence interval", opacity=0.1, line_width=0)
            st.metric(label='Observed Difference', value=round(observed_difference,2))
            st.plotly_chart(diff_fig, use_container_width=True)
                    # Check if the observed difference is statistically significant
            if 0 < confidence_interval[0] or 0 > confidence_interval[1]:
                st.success('The observed difference is statistically significant.')
            else:
                st.error('The observed difference is not statistically significant.')
    
if __name__ == '__main__':
    main()
