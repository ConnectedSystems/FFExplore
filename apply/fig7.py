#import packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

import matplotlib.ticker as ticker

# read result of the same metric
# select the result on the two rows which represent the identified fixing group
path = '../../../Research/G_func_ff/output/morris/revision/test/'
f_default = np.append([0, 0.1, 0.4, 0.5], np.linspace(0.2, 0.3, 11))
f_default.sort()
f_default = [str(round(i, 2)) for i in f_default]
f_default[0] = '0.0'
names = ['mae', 'var', 'pearson', 'mae_up', 'var_up', 
        'pearson_up', 'mae_low', 'var_low', 'pearson_low'] 
df = {}
for fn in names:
    df[fn] = pd.DataFrame(columns=['group1', 'group2'], index=f_default)
    for val in f_default:
        f_read = pd.read_csv('{}{}{}{}{}'.format(path, val, '/', fn, '.csv'))
        df[fn].loc[val, 'group1'] = f_read.loc[15, 'result_90']
        df[fn].loc[val, 'group2'] = f_read.loc[12, 'result_90']

# transform df from dict into dataframe with multiple columns
df = pd.concat(df, axis=1)
df.index = [float(i) for i in df.index]
df=df.astype('float')

def plot_shadow(col_name, ax, ylim=None):

    df[col_name].plot(kind='line', marker='o', linewidth=1, style='--', ms=3, ax=ax)
    ax.fill_between(df.index, df[f'{col_name}_low', 'group1'], df[f'{col_name}_up', 'group1'], color='lightsteelblue')
    ax.fill_between(df.index, df[f'{col_name}_low', 'group2'], df[f'{col_name}_up', 'group2'], color='moccasin')
    ax.set_xlim(-0.01, 0.51)
    if not (ylim==None):
        ax.set_ylim(ylim[0], ylim[1])
    ax.tick_params(axis='both', which='major', labelsize=16)
    ax.legend(['fix Group1', 'fix Group1 and Group2'], fontsize=16)
# End plot_shadow()
sns.set_style('whitegrid')
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(24, 7))
plot_shadow('mae', axes[0])
plot_shadow('var', axes[1])
fig.suptitle('Morris (n=90)', fontsize=20)
axes[1].set_xlabel('Default value',  fontsize=18)
plot_shadow('pearson', axes[2], [0.990, 1.010])

plt.savefig(f'{path}fig7.jpg', format='jpg', dpi=300)
