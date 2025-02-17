import seaborn as sns
import matplotlib.pyplot as plt

import pandas as pd

def visual_outlier(X_df, feature:str)
   '''
    Example) sns.boxplot(data=X_df[X_df['label']==1][['SizeOfCode']])
   '''
    sns.boxplot(data=X_df[[feature]])

def show_sns_histplot(df, x, hue):
    sns.histplot(data=df, x=x, hue=df[hue])

def VT_show_plt_plot(df):
    all_vendors = df['malicious_vendors'].explode()
    vendor_counts = all_vendors.value_counts()
    vendor_counts.plot(kind='bar')
    plt.title('Vendor Occurrences')
    plt.xlabel('Vendor')
    plt.ylabel('Occurrences')
    plt.xticks(rotation=45)
    plt.show()

def VT_show_plt_hist(df):
    plt.hist(df['malicious_count'], bins=range(1, df['malicious_count'].max() + 2), align='left', rwidth=0.8)
    plt.title('Malicious count')
    plt.xlabel('Length')
    plt.ylabel('Frequency')
    plt.xticks(range(1, df['malicious_count'].max() + 1))
    plt.show()
