import json
import time
from ooasp.interactive import InteractiveConfigurator
from ooasp.kb import OOASPKnowledgeBase
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from ooasp import settings
import matplotlib.colors as colors

solving_cm = mpl.colormaps['Pastel2'].resampled(8)
grounding_cm = mpl.colormaps['Set2'].resampled(8)

def get_results(name="bm"):
    with open(f'benchmarks/results/{name}.json') as outfile:
        return json.load(outfile)



solving_cm = mpl.colormaps['Pastel2'].resampled(8)
grounding_cm = mpl.colormaps['Set2'].resampled(8)

def plot_gs(bm_names, title):
    plt.clf()
    dfs = {}
    width = 0.25
    for bm_name in bm_names:
        data_dic = get_results(bm_name)
        df = pd.DataFrame.from_dict(data_dic, orient="index")
        df['name']=df.index
        df=df.reset_index()
        dfs[bm_name]=df
    pos = 0
    for bm_name, df in dfs.items():
        plt.bar(df.index+(width*pos),df['time'],color=solving_cm(pos),width=width)
        plt.bar(df.index+(width*pos),df['time-grounding'],color=grounding_cm(pos),width=width)
        pos+=1

    plt.ylabel('Time (sec)')
    plt.xlabel('#elements')
    plt.title(title)
    legends = []
    for bm_name in dfs.keys():
        legends+=[f'solving {bm_name}', f'grounding {bm_name}']
    plt.legend(legends)
    plt.xticks(df.index,df['name'])
    plt.savefig(f'benchmarks/results/{title}.png')
    # plt.show()


def plot_domain(bm_name, title, name):
    plt.clf()
    data_dic = get_results(bm_name)[name]
    d = {
        "grounding": data_dic["per-domain-grounding"],
        "solving": data_dic["per-domain-solving"]
    }

    df = pd.DataFrame.from_dict(d, orient="index")
    df = df.T
    df['time'] = df.sum(axis=1)
    plt.bar(df.index,df['time'],color='lightsteelblue',width=0.3)
    plt.bar(df.index,df['grounding'],color='tan',width=0.3)
    plt.ylabel('Time (sec)')
    plt.xlabel('Domain size')
    plt.title(title)
    plt.legend(['solving','grounding'])
    plt.savefig(f'benchmarks/results/{title}.png')
    # plt.show()


# Extend solve
# plot_gs(["basic/extend_solve","paper/extend_solve","defined/extend_solve"], "Compare Extend Solve")
plot_gs(["basic/incremental",'paper/incremental','defined/incremental','defined-os/incremental'], "Compare Incremental")
# plot_gs(["basic/options",'paper/options','defined/options'], "Compare Options")
# plot_gs(["defined/options",'defined/options_object'], "Compare Options to Object")


plot_domain("defined-os/incremental", "Extend incrementally (From 9 Elements)","9")
# plot_domain("defined/incremental", "Incremental (Domain 10)","10")
