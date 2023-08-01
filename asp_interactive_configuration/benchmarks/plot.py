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
    width = 0.2
    fig, ax = plt.subplots()

    for bm_name in bm_names:
        data_dic = get_results(bm_name)
        df = pd.DataFrame.from_dict(data_dic, orient="index")
        df['name']=df.index
        df=df.reset_index()
        dfs[bm_name]=df
        print(df)
    for pos, (bm_name, df) in enumerate(dfs.items()):
        print(bm_name)
        ax.bar(df.index+(width*pos),df['time'],color=solving_cm(pos),width=width)
        ax.bar(df.index+(width*pos),df['time-grounding'],color=grounding_cm(pos),width=width)
        # if bm_name in ['defined-os/incremental','defined/incremental']:
        ax.bar_label(ax.containers[pos*2 ],df['size'].astype(str) + "/" + df['domain_size'].astype(str),fontsize=5)

    ax.set_ylabel('Time (sec)')
    ax.set_xlabel('#elements')
    ax.set_title(title)
    legends = []
    for bm_name in dfs.keys():
        legends+=[f'solving {bm_name}', f'grounding {bm_name}']
    ax.legend(legends)
    ax.set_xticks(df.index,df['name'])
    fig.savefig(f'benchmarks/results/{title}.png')
    print(f"Saved image in benchmarks/results/{title}.png")
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
# plot_gs(["defined/extend_solve","defined-os/extend_solve"], "Compare Extend Solve")
plot_gs(['defined/incremental','defined-os/incremental'], "Compare Incremental")
# plot_gs(["basic/incremental",'paper/incremental','defined/incremental','defined-os/incremental'], "Compare Incremental")
# plot_gs(['defined/options','defined-os/options'], "Compare Options")
# plot_gs(["basic/options",'paper/options','defined/options','defined-os/options'], "Compare Options")
# plot_gs(["defined/options",'defined/options_object'], "Compare Options to Object")


# plot_domain("defined-os/incremental", "Extend incrementally (From 9 Elements)","9")
# plot_domain("defined/incremental", "Incremental (Domain 10)","10")
