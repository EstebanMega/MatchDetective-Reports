import statsmodels.api as sm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.stats.power import TTestIndPower, tt_ind_solve_power
from statsmodels.stats.weightstats import ttest_ind
from statsmodels.stats.proportion import proportions_chisquare, confint_proportions_2indep


class FrequentistAB():
    
    def __init__(self, baseline_data, power, alpha, metric_name, metric_type = "proportion",data=None):
        self.baseline = baseline_data
        self.data=data
        self.power=power
        self.alpha=alpha
        self.metric_name =metric_name
        self.metric_type=metric_type
        
    def calculate_sample_size(self, mde):
        # We calculate the 
       
        self.p1 = self.baseline[self.metric_name].mean()
        self.p2 = self.p1*(1+mde)
        
        if self.metric_type=='proportion':
            # Estimate the sample size required per group
            self.cohen_D = sm.stats.proportion_effectsize(self.p1, self.p2)
            
        elif self.metric_type=='mean':
            self.cohen_D = mde
        
        n = tt_ind_solve_power(effect_size=self.cohen_D, power=self.power, alpha=self.alpha)
        n = int(round(n,2)) # Round up to the nearest thousand
        
        self.sample_size = n
        
    
    def plot_power_analysis(self):
        
        n=self.sample_size
        effect_size=self.cohen_D
        p1= self.p1
        p2= self.p2
        print(p1,p2)
        
        if self.metric_type =='proportion':
            stat =100*p1
            percentage = "%"
        else:
            stat = p1
            percentage=''
            
        print(f'To detect an effect of {100*(p2/p1-1):.1f}% lift from the baseline statistic at {stat:.2f}{percentage}, '
                f'the sample size per group required is {n}.'
                f'\nThe total sample required in the experiment is {2*n}.')
        
        if self.data is not None:
            print("The current sample size per group is", self.data.groupby('ab_test_variants')['progress_id'].nunique().reset_index(drop=False))

        # Explore power across sample sizes
        ttest_power = TTestIndPower()
        ttest_power.plot_power(dep_var='nobs', nobs=np.arange(round(n*0.1), round(n*5), round(n*0.1)), effect_size=[effect_size], title='Power Analysis')

        # Set plot parameters
        plt.axhline(self.power, linestyle='--', label='Desired Power', alpha =0.5)
        plt.axvline(n, linestyle='--', color='orange', label='Sample Size', alpha=0.5)
        plt.ylabel('Statistical Power')
        plt.grid(alpha=0.08)
        plt.legend()
        plt.show()
        
    def ttest_for_proportions(self):
        treatment = self.data[data.ab_test_variants == "Variant A"][self.metric_name]
        control = self.data[data.ab_test_variants == "Control"][self.metric_name]
        
        print(f'---- Summary {self.metric_name}')
        print(self.data.groupby('ab_test_variants')[self.metric_name].agg(['count','mean']))
        print(f'The actual difference in the groups is {round((treatment.mean()/control.mean() -1),2) * 100}%')
        
        # Execute test
        AB_tstat, AB_pvalue, AB_df = ttest_ind(treatment, control)

        # Print results
        print(f'-------- AB Test ---------\n')
        print('Ho: Groups are the same.')
        print('Ha: Groups are different.\n')
        print(f'Significance level: {self.alpha}')

        print(f'T-Statistic = {AB_tstat:.3f} | P-value = {AB_pvalue:.3f}')

        print('\nConclusion:')
        if AB_pvalue < self.alpha:
            print('Reject Ho and conclude that there is statistical significance in the difference the two groups.')
        else:
            print('Fail to reject Ho.')
        
data = pd.read_csv('ab_test_09.csv')
data=data[data.level_20==1]
data_previous = pd.read_csv('ab_test_09_previous.csv')
data_previous=data_previous[data_previous.level_20==1]

ab_test = FrequentistAB(data=data,baseline_data=data_previous,power=0.8,alpha=0.05,metric_name="ads_watched",metric_type="mean")

ab_test.calculate_sample_size(mde=0.1)
ab_test.plot_power_analysis()
ab_test.ttest_for_proportions()
