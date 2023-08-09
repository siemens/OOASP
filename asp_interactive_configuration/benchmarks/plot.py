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
    """Gets the results for a given benchamrk name

    Args:
        name (str, optional): The name/path of the benchmark. Defaults to "bm".

    Returns:
        json: Json with the benchmarks info
    """
    with open(f'benchmarks/results/{name}.json') as outfile:
        return json.load(outfile)



solving_cm = mpl.colormaps['Pastel2'].resampled(8)
grounding_cm = mpl.colormaps['Set2'].resampled(8)

def plot_gs(bm_names, title):
    """Compare different benchmarks outputs

    Args:
        bm_names : The name of the benchmark files to compare
        title : The title of the plot and output file
    """
        
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
    for pos, (bm_name, df) in enumerate(dfs.items()):
        ax.bar(df.index+(width*pos),df['time'],color=solving_cm(pos),width=width)
        ax.bar(df.index+(width*pos),df['time-grounding'],color=grounding_cm(pos),width=width)
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
    """Plotting the times for a single call devided per domain

    Args:
        bm_name : The name of the benchmark file saved
        title : The title of the plot and output file
        name : The domain name (Number)
    """
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
