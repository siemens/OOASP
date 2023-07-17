import json
import time
from ooasp.interactive import InteractiveConfigurator
from ooasp.kb import OOASPKnowledgeBase
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


import functools
import time
import ooasp.utils as utils


class BM:

    def __init__(self, n_runs, name, fn, **kwargs):
        self.n_runs=n_runs
        self.name=name
        self.runs = {}
        self.final_results = {
            "time":0,
            "time-solving":0,
            "time-grounding":0
        }
        self.fn = fn
        self.kwargs = kwargs
        self.run()


    def run(self):
        args = [f"{k}:{v}" for k,v in self.kwargs.items()]
        print("-"*10 +f"Running {self.fn.__name__}  " + " ".join(args) + "-"*10)

        for n in range(self.n_runs):
            t1 = time.time()
            res = self.fn(**self.kwargs)
            t2 = time.time()
            self.add_run_results(t2-t1,res)
        self.set_final_results()

    def add_run_results(self, time, iconf):
        result = {
           "time": time
        }
        result.update(iconf._statistics)
        self.runs[len(self.runs)]=result


    def set_final_results(self):
        for run in self.runs.values():
            for t in self.final_results.keys():
                self.final_results[t]+=run[t]

        for t in self.final_results.keys():
            self.final_results[t]=self.final_results[t]/self.n_runs

        times_per_domain = ["per-domain-grounding","per-domain-solving"]
        for tpd in times_per_domain:
            g_times = {v:r[tpd] for  v,r in self.runs.items()}
            df = pd.DataFrame.from_dict(g_times, orient="index")
            means = df.aggregate(np.mean)
            self.final_results[tpd] = means.to_dict()


    @property
    def dic(self):
        return {
            "kwargs":self.kwargs,
            "results": self.final_results,
            "runs":self.runs
        }
    def __str__(self):
        return utils.pretty_dic(self.dic)


def save_results(bms, name="bm"):
    data = {bm.name:bm.final_results for bm in bms}
    with open(f'benchmarks/results/{name}.json', 'w') as outfile:
        json.dump(data, outfile,indent=4)

def get_results(name="bm"):
    with open(f'benchmarks/results/{name}.json') as outfile:
        return json.load(outfile)


# --------- Plotting


def plot_gs(bm_name, title):
    plt.clf()
    data_dic = get_results(bm_name)
    df = pd.DataFrame.from_dict(data_dic, orient="index")
    df['name']=df.index
    df=df.reset_index()
    plt.bar(df.index,df['time'],color='lightsteelblue',width=0.3)
    plt.bar(df.index,df['time-grounding'],color='tan',width=0.3)
    plt.ylabel('Time (sec)')
    plt.xlabel('#elements')
    plt.title(title)
    plt.legend(['solving','grounding'])
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




# --------- Functions to benchmark
def new_iconf():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1","./examples/racks/kb.lp")
    return InteractiveConfigurator(racks_kb,"i1",["./examples/racks/constraints.lp"])

def extend_solve(ne):
    iconf = new_iconf()
    # current limit
    for i in range(ne):
        iconf.new_leaf("elementA")
    iconf.extend_domain(ne + 5)
    iconf.next_solution()
    return iconf

def incremental(ne):
    iconf = new_iconf()
    # current limit
    for i in range(ne):
        iconf.new_leaf("elementA")
    iconf.extend_incrementally()
    return iconf

def options(ne):
    iconf = new_iconf()
    # current limit
    for i in range(ne):
        iconf.new_leaf("elementA")
    iconf.get_options()
    return iconf

def options_object(ne):
    iconf = new_iconf()
    # current limit
    iconf.extend_domain(ne)
    iconf.get_options()
    return iconf

# --------- Running benchmarks

def run_extend_solve(elements):
    n_runs = 3
    results = []
    for e in elements:
        results.append(BM(n_runs,e,extend_solve,ne=e))

    save_results(results,"extend_solve")



def run_incremental(elements):
    n_runs =2
    results = []
    for r in elements:
        results.append(BM(n_runs,r,incremental,ne=r))

    save_results(results,"incremental")

def run_options(elements, objects=False):
    n_runs =2
    results = []
    for r in elements:
        if objects:
            results.append(BM(n_runs,r,options_object,ne=r))
        else:
            results.append(BM(n_runs,r,options,ne=r))

    save_results(results,"options")

# run_extend_solve(elements=[13,14,15,16,17,18])
# run_incremental(elements=[8,9,10])
run_options(elements=[12,13,14,15,16],objects=True)

plot_gs("options", "Get options")
# plot_gs("extend_solve", "Single")
# plot_gs("incremental", "Extend incrementally")
# plot_domain("incremental", "Extend incrementally (From 9 Elements)","9")
# plot_domain("incremental", "Incremental (Domain 10)","10")