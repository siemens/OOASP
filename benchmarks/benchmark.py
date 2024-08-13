import json
import time
from typing import Any, Callable, Optional, Union, cast
from ooasp.interactive import InteractiveConfigurator
from ooasp.kb import OOASPKnowledgeBase
import numpy as np
import pandas as pd
import ooasp.utils as utils
from ooasp import settings
import threading
import sys

TIMEOUT = 120


class BM:
    """
    Benchmark container
    """

    def __init__(self, n_runs: int, name: str, fn: Callable, **kwargs) -> None:
        self.n_runs: int = n_runs
        self.name: str = name
        self.timeout = False
        self.runs: dict[int, dict[str, Any]] = {}
        self.final_results: dict[str, Any] = {
            "time": 0,
            "time-solving": 0,
            "time-grounding": 0
        }

        self.fn: Callable = fn
        self.kwargs = kwargs

        self.run()

    def call_and_add_result(self, iconfs_for_runs: list[InteractiveConfigurator], n_run: int, example: str = "racks", **kwargs):
        iconf: InteractiveConfigurator = new_iconf(example=example)
        iconfs_for_runs[n_run] = iconf
        self.fn(iconf=iconf, **kwargs)

    def run(self) -> None:
        args = [f"{k}:{v}" for k, v in self.kwargs.items()]
        print("-"*10 + f"Running {self.fn.__name__}  " + " ".join(args) + "-"*10)
        iconfs_for_runs: list[Optional[InteractiveConfigurator]] = [
            None]*self.n_runs
        self.kwargs["iconfs_for_runs"] = iconfs_for_runs
        for n in range(self.n_runs):
            self.kwargs["n_run"] = n
            thread = threading.Thread(target=self.call_and_add_result, kwargs=self.kwargs)
            t1 = time.time()
            thread.setDaemon(True)
            thread.start()
            thread.join(TIMEOUT)
            t2 = time.time()
            total_time = t2-t1
            if thread.is_alive() or total_time > TIMEOUT:
                print("Time out")
                print(getattr(iconfs_for_runs[n], 'domain_size', None))
                threading.Event().set()
                total_time = TIMEOUT
                self.timeout = 1
                timeout = 1
            else:
                timeout = 0
            self.add_run_results(total_time, cast(
                InteractiveConfigurator, iconfs_for_runs[n]), timeout)
        self.set_final_results()

    def add_run_results(self, time: float, iconf: InteractiveConfigurator, timeout) -> None:
        result: dict[str, Any] = {
            "time": time,
            "timeout": timeout,
            "size": 0 if timeout else iconf.config.size,
            "domain_size": iconf.domain_size,
            "found_config": iconf.config.fb.asp_str()
        }
        result.update(iconf._statistics)
        self.runs[len(self.runs)] = result

    def set_final_results(self):
        for run in self.runs.values():
            for t in self.final_results.keys():
                if t in run:
                    self.final_results[t] += run[t]
            self.final_results['timeout'] = run['timeout']
            self.final_results['size'] = run['size']
            self.final_results['domain_size'] = run['domain_size']
            self.final_results['found_config'] = run['found_config']

        for t in ['time', 'time-solving', 'time-grounding']:
            if t in self.final_results:
                self.final_results[t] = self.final_results[t]/self.n_runs

        times_per_domain = ["per-domain-grounding", "per-domain-solving"]
        for tpd in times_per_domain:
            g_times = {v: r[tpd] for v, r in self.runs.items()}
            df = pd.DataFrame.from_dict(g_times, orient="index")
            means: pd.Series[float] = df.aggregate(np.mean)
            self.final_results[tpd] = means.to_dict()

    @property
    def dic(self):
        return {
            "kwargs": self.kwargs,
            "results": self.final_results,
            "runs": self.runs
        }

    def __str__(self):
        return utils.pretty_dic(self.dic)


# --------- Utils
def save_results(bms: list[BM], name: str = "bm") -> None:
    """Saves the results as a json file

    Parameters:
        bms: Benchmarks
        name (str, optional): Name. Defaults to "bm".
    """
    data: dict[str, dict[str, Any]] = {bm.name: bm.final_results for bm in bms}
    f_name = f'benchmarks/results/{name}.json'
    with open(f_name, 'w') as outfile:
        json.dump(data, outfile, indent=4)
    print("Results saved in " + f_name)


def new_iconf(example="racks") -> InteractiveConfigurator:
    """Creates a new interactive configurator for the racks example

    Returns:
        InteractiveConfigurator
    """
    if example == "racks":
        kb = OOASPKnowledgeBase.from_file("racks_v1", settings.racks_example_kb)
        return InteractiveConfigurator(kb, "i1", [settings.racks_example_constraints])
    elif example == "metro":
        kb = OOASPKnowledgeBase.from_file("metro_v1", settings.metro_example_kb)
        return InteractiveConfigurator(kb, "i1", [settings.metro_example_constraints])
    elif example == "metrof":
        kb = OOASPKnowledgeBase.from_file("metro_v1", settings.metrof_example_kb)
        return InteractiveConfigurator(kb, "i1", [settings.metrof_example_constraints])
    else:
        raise Exception("Invalid example for configuration")

# --------- Functions to benchmark


def extend_solve(iconf: InteractiveConfigurator, ne: int) -> InteractiveConfigurator:
    for i in range(ne):
        e = iconf.new_object("elementA")
    iconf.extend_domain(ne + 5)
    found = iconf.next_solution()
    iconf.select_found_configuration()
    return iconf


def incremental(iconf: InteractiveConfigurator, ne: int, cls: str = "element", overshoot: bool = False, step_size: int = 1) -> InteractiveConfigurator:
    for i in range(ne):
        iconf.new_object(cls)
    found = iconf.extend_incrementally(overshoot=overshoot, step_size=step_size)
    iconf.select_found_configuration()
    return iconf


def options(iconf, ne):
    iconf.extend_domain(ne-9, "object")
    for i in range(ne):
        iconf.new_object("elementA")
    iconf.get_options()
    return iconf


def options_object(iconf, ne):
    iconf.extend_domain(ne, "object")
    iconf.get_options()
    return iconf


def wagons(iconf, ne, overshoot=False, step_size=1, intopt='enumint'):
    iconf.new_object("wagon")
    if intopt == 'enumint':
        iconf.select_value(1, "nr_passengers", ne)
    else:
        iconf.select_fvalue(1, "nr_passengers", ne)
    found = iconf.extend_incrementally(overshoot=overshoot, step_size=step_size)
    iconf.select_found_configuration()
    print(found)
    return iconf

# --------- Running benchmarks


def run(n_runs: int, fun: Callable, elements: list[int], name: str = "extend_solve", **kwargs) -> None:
    """Main function called to run a benchmark

    Parameters:
        n_runs: Number of types to run the function
        fun: function to benchmark
        elements: the elements used for each run
        name (str, optional): The benchmark name used for saving
    """
    results: list[BM] = []
    for e in elements:
        results.append(BM(n_runs, name, fun, ne=e, **kwargs))

    save_results(results, name)


# Racks
run(1, incremental, [1, 2, 3, 4, 5, 6], "inc_rack_overshoot", cls='rackDouble', overshoot=True)
run(1, incremental, [1, 2, 3, 4, 5, 6], "inc_rack", cls='rackDouble')


# Element
run(1, incremental, [9, 10, 11, 12], "inc_elem_step_4", cls='element', step_size=4)
run(1, incremental, [9, 10, 11, 12], "inc_elem_step_5", cls='element', step_size=5)
run(1, incremental, [9, 10, 11, 12], "inc_elem_step_6", cls='element', step_size=6)
run(1, incremental, [9, 10, 11, 12], "inc_elem_step_7", cls='element', step_size=7)
run(1, incremental, [9, 10, 11, 12], "inc_elem_overshoot", cls='element', overshoot=True)
run(1, incremental, [9, 10, 11, 12], "inc_elem", cls='element')

# Metro
run(1, wagons, [50, 60, 70], "wagon_people_f", example="metrof", intopt='int')
run(1, wagons, [50, 60, 70], "wagon_people", example="metro", intopt='enumint')

sys.exit(0)
