import pandas as pd
import numpy as np
import SALib
from toposort import toposort, toposort_flatten
import json
import os
#sensitivity analysis and partial sorting 
from SALib.sample import saltelli as sample_saltelli
from SALib.analyze import sobol as analyze_sobol
from SALib.sample import latin as sample_latin
from SALib.test_functions.Sobol_G import evaluate, \
    total_sensitivity_index as total_sa, sensitivity_index as main_sa,\
    partial_first_order_variance as pfoa, \
    total_variance
# import settings for Sobol G-function and returns necessary elements
# import settings for Sobol G-function and returns necessary elements
from utils.Sobol_G_setting import set_sobol_g_func
from utils.group_fix import group_fix
from utils.partial_sort import to_df, partial_rank

a, x, x_bounds, x_names, len_params, problem = set_sobol_g_func()
f_dir = '../../../Research/G_func_ff/output/sobol/revision/'
cache_file = '{}{}'.format(f_dir, 'sobol_test.json')
# calculate results with fixed parameters
x_all = sample_latin.sample(problem, 1000, seed=101)
y_true = evaluate(x_all, a)
y_true_ave = np.average(y_true)
x_default = 0.25
rand = np.random.randint(0, y_true.shape[0], size=(1000, y_true.shape[0]))
error_dict = {}
pool_res = {}

if not os.path.exists(cache_file):
    # Loop of Morris
    file_exist = False
    partial_order = {}
    sa_total = {}
    sa_main = {}
    n_start, n_end, n_step = 200, 1200, 200
    x_large_size = sample_saltelli.sample(problem, n_end, calc_second_order=False)
    for i in range(n_start, n_end, n_step):
        # partial ordering
        x_sobol = x_large_size[:i * (len_params + 2)]
        if i == n_start:
            y_sobol = evaluate(x_sobol, a)
        else:
            y_eval = evaluate(x_sobol[-(len_params + 2) * n_step:], a)
            y_sobol =  np.append(y_sobol, y_eval)

        y_sobol = evaluate(x_sobol, a)
        sa_sobol = analyze_sobol.analyze(problem, 
                    y_sobol, calc_second_order=False, num_resamples=1000, conf_level=0.95)
        # use toposort find parameter sa block
        conf_low = sa_sobol['total_rank_ci'][0]
        conf_up = sa_sobol['total_rank_ci'][1]

        abs_sort = partial_rank(len_params, conf_low, conf_up)
        rank_list = list(toposort(abs_sort))

        key = 'result_'+str(i)
        partial_order[key] = {j: list(rank_list[j]) for j in range(len(rank_list))}
#         #save results of sobol indices
        sa_total[key] = sa_sobol['ST']         
        sa_main[key] = sa_sobol['S1']

        error_dict[key], pool_res = group_fix(partial_order[key], evaluate, 
                        x_all, y_true, x_default, rand, pool_res, a, file_exist)
    with open(cache_file, 'w') as fp:
        json.dump(partial_order, fp, indent=2)
else:
    file_exist = True
    with open(cache_file, 'r') as fp:
        partial_order = json.load(fp)
    for key, value in partial_order.items():
        error_dict[key], pool_res = group_fix(value, evaluate, x_all, y_true, 
                                        x_default, rand, pool_res, a, file_exist)
