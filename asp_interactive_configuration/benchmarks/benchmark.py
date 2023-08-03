import json
import time
from ooasp.interactive import InteractiveConfigurator
from ooasp.kb import OOASPKnowledgeBase
import numpy as np
import pandas as pd
import matplotlib as mpl
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
        print(iconf)
        result = {
           "time": time,
           "size": iconf.config.size,
           "domain_size": iconf.config.domain_size,
        }
        result.update(iconf._statistics)
        self.runs[len(self.runs)]=result


    def set_final_results(self):
        for run in self.runs.values():
            for t in self.final_results.keys():
                self.final_results[t]+=run[t]
            self.final_results['size']=run['size']
            self.final_results['domain_size']=run['domain_size']

        for t in ['time','time-solving','time-grounding']:
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


# --------- Utils
def save_results(bms, name="bm"):
    data = {bm.name:bm.final_results for bm in bms}
    with open(f'benchmarks/results/{name}.json', 'w') as outfile:
        json.dump(data, outfile,indent=4)

def new_iconf():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    return InteractiveConfigurator(racks_kb,"i1",[settings.racks_example_constraints])

# --------- Functions to benchmark

def extend_solve(ne):
    iconf = new_iconf()
    # current limit
    for i in range(ne):
        e = iconf.new_object("elementA")
        # iconf._create_required_objects("elementA",e)
    iconf.extend_domain(ne + 5)
    found = iconf.next_solution()
    iconf.select_found_configuration()
    return iconf

def incremental(ne):
    iconf = new_iconf()
    # current limit
    for i in range(ne):
        iconf.new_object("elementA")
    found = iconf.extend_incrementally(overshoot=True)
    # found = iconf.extend_incrementally()
    iconf.select_found_configuration()
    return iconf

def options(ne):
    iconf = new_iconf()
    # current limit
    iconf.extend_domain(ne-9,"object")
    for i in range(ne):
        iconf.new_object("elementA")
    iconf.get_options()
    return iconf

def options_object(ne):
    iconf = new_iconf()
    iconf.extend_domain(ne,"object")
    iconf.get_options()
    return iconf

# def options_object(ne):
#     iconf = new_iconf()
#     # current limit
#     iconf.extend_domain(ne)
#     iconf.get_options()
#     iconf.show_options()
#     return iconf

# --------- Running benchmarks

def run(n_runs,fun,elements,name = "extend_solve"):
    n_runs = 3
    results = []
    for e in elements:
        results.append(BM(n_runs,e,fun,ne=e))

    save_results(results,name)

# run(2,extend_solve,elements=[13,14,15,16,17,18],name=f"{opt}-os/extend_solve")
# run(2,incremental,elements=[8,9,10,11],name=f"{opt}/incremental-noex")
run(2,incremental,elements=[8,9,10,11],name=f"{opt}-os/incremental")
# run(2,options,elements=[18,20,22,24],name=f"{opt}-os/options")
# run(2,options,elements=[20,22,24,25,26],name=f"{opt}/options")
# run(2,options_object,elements=[18,20,22,24],name=f"{opt}/options_object")
