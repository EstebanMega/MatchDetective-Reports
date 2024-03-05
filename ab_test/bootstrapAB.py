import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.utils import resample

class BootstrapAB():
    
    def __init__(self, baseline_data, treatment_data, metric_name):
        self.baseline = baseline_data
        self.data = treatment_data
        self.metric_name = metric_name
        
    def calculate_bootstrap_means(self, n_iterations):
        # Calculate bootstrap means for treatment and control groups
        control_means = [np.mean(resample(self.baseline[self.metric_name])) for _ in range(n_iterations)]
        treatment_means = [np.mean(resample(self.data[self.metric_name])) for _ in range(n_iterations)]
        return control_means, treatment_means
    
    def plot_bootstrap_distributions(self, control_samples, treatment_samples):
        # Plot the bootstrap distributions
        plt.hist(control_samples, alpha=0.5, label='Control')
        plt.hist(treatment_samples, alpha=0.5, label='Treatment')
        plt.xlabel(self.metric_name)
        plt.ylabel('Frequency')
        plt.title('Bootstrap Distributions')
        plt.legend()
        plt.show()
    
    def perform_bootstrap_ab_test(self, n_iterations=100000):
        # 
        control_samples, treatment_samples = self.calculate_bootstrap_means(n_iterations=n_iterations)
        differences = np.array(treatment_samples) - np.array(control_samples)
        
        # Calculate the observed difference between treatment and control
        observed_difference = np.mean(treatment_samples) - np.median(control_samples)
        
        # Calculate the 95% confidence interval for the difference
        confidence_interval = np.percentile(differences, [2.5,97.5])
        
        # Plot the bootstrap distributions
        self.plot_bootstrap_distributions(control_samples, treatment_samples)
        self.plot_difference_distribution(differences)

        # Print results
        print(f'Observed treatment {np.mean(treatment_samples)}')
        print(f'Observed Control {np.mean(control_samples)}')
        print(f'Observed Difference: {observed_difference:.3f}')
        print(f'95% Confidence Interval: [{confidence_interval[0]:.3f}, {confidence_interval[1]:.3f}]')

        # Check if the observed difference is statistically significant
        if 0 < confidence_interval[0] or 0 > confidence_interval[1]:
            print('The observed difference is statistically significant.')
        else:
            print('The observed difference is not statistically significant.')
            
            
    def plot_difference_distribution(self, differences):
        # Plot the distribution of differences
        confidence_interval = np.percentile(differences, [2.5,97.5])
        plt.hist(differences, bins=30, edgecolor='black', alpha=0.7)
        plt.axvline(np.mean(differences), color='red', linestyle='--', linewidth=2, label='Observed Difference')
        plt.axvline(confidence_interval[0], color='blue', linestyle='--', linewidth=1, label='Alpha/2')
        plt.axvline(confidence_interval[1], color='blue', linestyle='--', linewidth=1, label='1-Alpha/2')
        plt.axvline(0,color='green', linestyle='--', linewidth=2, label='Zero')
        plt.xlabel('Difference (Treatment - Control)')
        plt.ylabel('Frequency')
        plt.title('Distribution of Differences')
        plt.legend()
        plt.show()