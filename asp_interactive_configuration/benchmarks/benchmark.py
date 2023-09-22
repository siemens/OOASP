import json
import time
from ooasp.interactive import InteractiveConfigurator
from ooasp.kb import OOASPKnowledgeBase
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import time
import threading
import ooasp.utils as utils
from ooasp import settings

class BM:
    """
    Benchmark container
    """
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
    """Saves the results as a json file

    Args:
        bms: Benchmarks
        name (str, optional): Name. Defaults to "bm".
    """
    data = {bm.name:bm.final_results for bm in bms}
    with open(f'benchmarks/results/{name}.json', 'w') as outfile:
        json.dump(data, outfile,indent=4)

def new_iconf():
    """Creates a new interactive configurator for the racks example

    Returns:
        InteractiveConfigurator
    """
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    return InteractiveConfigurator(racks_kb,"i1",[settings.racks_example_constraints])

def setup_bm_instance(elemAs, elemBs, elemCs, elemDs):
    """
    Set up a benchmark instance with specified element counts.

    This function creates and configuration for benchmarking.
    It adds the specified number of elementAs, elementBs, elementCs, and elementDs to
    the configuration and returns it.

    Args:
        elemAs (int): The number of 'elementA's to add.
        elemBs (int): The number of 'elementB's to add.
        elemCs (int): The number of 'elementC's to add.
        elemDs (int): The number of 'elementD's to add.

    Returns:
        iconf (InteractiveConfigurator): An instance of the InteractiveConfigurator class
        with the specified elements added to the configuration.
    """
    iconf = new_iconf()
    
    for i in range(elemAs):
        iconf.new_object("elementA")

    for i in range(elemBs):
        iconf.new_object("elementB")

    for i in range(elemCs):
        iconf.new_object("elementC")

    for i in range(elemDs):
        iconf.new_object("elementD")

    return iconf

def extend_incrementally_wrapper(iconf:InteractiveConfigurator):
    """
    Wrap and call the 'extend_incrementally' method of an InteractiveConfigurator.

    This function wraps the 'extend_incrementally' method of an InteractiveConfigurator instance
    and calls it with 'overshoot' set to True. If an exception is raised during the method
    call, it captures and prints the exception message.

    Args:
        iconf (InteractiveConfigurator): An instance of the InteractiveConfigurator class.
    """
    try:
        return iconf.extend_incrementally(overshoot=True)
    except Exception as e:
        if hasattr(e, 'message'):
            print(e.message)
        else:
            print(e)

def add_elements(element:str, n:int, iconf:InteractiveConfigurator):
    """
    Add n elements of a specified type to a configuration.

    Args:
        element (str): The type of element to add (e.g., 'elementA').
        n (int): The number the specified element is to be added.
        iconf (InteractiveConfigurator): An instance of the InteractiveConfigurator class.
    """
    for i in range(n):
        iconf.new_object(element)

# --------- Functions to benchmark
def extend_solve(ne):
    iconf = new_iconf()
    for i in range(ne):
        e = iconf.new_object("elementA")
    iconf.extend_domain(ne + 5)
    found = iconf.next_solution()
    iconf.select_found_configuration()
    return iconf

def incremental(ne):
    iconf = new_iconf()
    for i in range(ne):
        iconf.new_object("elementA")
    found = iconf.extend_incrementally(overshoot=True)
    iconf.select_found_configuration()
    return iconf

def options(ne):
    iconf = new_iconf()
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

def incremental_input_before():
    """
    Perform an incremental configuration benchmark based on user input.

    Before running, this function takes user input for the number of iterations and the number of elements
    for each type in each iteration. It then creates and extends configurations based on
    this input, and saves the result as a PNG image.
    The console input follows as for example:   5 - 3 2 
    (creates 5 elementA, 0 elementB, 3 elementC, 2 elementD)

    Returns:
        iconf: The configuration after the last iteration.
    """
    iteration_nr = 1
    iconf = new_iconf()

    iterations = int(input("Enter the number of iterations: "))
    input_list = []

    for _ in range(iterations):
        input_str = input("Enter the number of elements for each type (- for skip): ")
        input_list.append(input_str)

    for input_str in input_list:
        if input_str.lower() == 'q':
            continue
        
        element_counts = input_str.split()

        for i, count_str in enumerate(element_counts):
            if count_str != "-":
                elements = int(count_str)
                element_type = f"element{chr(ord('A') + i)}"
                for _ in range(elements):
                    e = iconf.new_object(element_type)

        print("Iteration " + str(iteration_nr) + ":")
        found = iconf.extend_incrementally(overshoot=True)
        iconf.select_found_configuration()
        print(iconf._time_grounding + iconf._time_solving)

        found.save_png()
        iteration_nr += 1
    return iconf


def incremental_input_in_steps():
    """
    Perform an incremental configuration benchmark based on user input.

    This function allows the user to perform multiple iterations by entering the number of elements 
    in each step. It continues to prompt the user until 'q' is entered to quit. After each step, it 
    prints information about the iteration and saves the final configuration as a PNG image.
    The console input follows as for example:   5 - 3 2 
    (creates 5 elementA, 0 elementB, 3 elementC, 2 elementD)
    
    Returns:
        iconf: The configuration after the last iteration.
    """
    iteration_nr = 1
    iconf = new_iconf()

    while True:
        input_str = input("Enter the number of elements for each type (- for skip) or 'q' to quit: ")

        if input_str.lower() == 'q':
            break

        element_counts = input_str.split()

        for i, count_str in enumerate(element_counts):
            if count_str != "-":
                elements = int(count_str)
                element_type = f"element{chr(ord('A') + i)}"
                for _ in range(elements):
                    e = iconf.new_object(element_type)

        print("Iteration " + str(iteration_nr) + ":")
        found = iconf.extend_incrementally(overshoot=True)
        iconf.select_found_configuration()
        print(iconf._time_grounding + iconf._time_solving)

        found.save_png()
        iteration_nr += 1
    return iconf

def run_incremental_benchmark_instance(iconf:InteractiveConfigurator, run_in_seconds):
    """
    Run an incremental benchmark instance with a specified timeout.

    This function runs the `extend_incrementally` method of a configuration using a wrapper method
    in a separate thread for a specified duration. If the method execution exceeds the
    given time limit, it terminates the thread and reports a timeout.

    Args:
        iconf (InteractiveConfigurator): An instance of the InteractiveConfigurator class.
        run_in_seconds (int): The maximum duration (in seconds) to run the benchmark.

    """
    thread = threading.Thread(target=extend_incrementally_wrapper, args=(iconf,))
    
    thread.start()
    thread.join(run_in_seconds)

    if thread.is_alive():
        threading.Event().set()
        print("The extend_incrementally method timed out after", run_in_seconds, "seconds. \n")
        return

    iconf.select_found_configuration()
    print(str(iconf._time_grounding + iconf._time_solving) + "\n")

def run_incremental_benchmarks(run_in_seconds: int):
    """
    Run a series of incremental benchmarks with varying element counts.

    This function performs a series of incremental benchmarks with different combinations of
    elementAs, elementBs, elementCs, and elementDs. It execute benchmarks with single, double, 
    and triple iterations, recording and printing the configuration details and execution 
    times for each benchmark.

    Args:
        run_in_seconds (int): The maximum duration (in seconds) to run each benchmark before a timeout occurs.
    """

    count = 0
    countsingle=1
    #single iteration benchmarks
    for num_as in range(0, 22, 7):
        for num_bs in range(3, 7, 3):
            for num_cs in range(0, 7, 3):
                for num_ds in range(3, 7, 3):
                    print(f"-----{num_as} elemA, {num_bs} elemB, {num_cs} elemC, {num_ds} elemD-----")
                    iconf = setup_bm_instance(num_as, num_bs, num_cs, num_ds)
                    run_incremental_benchmark_instance(iconf, run_in_seconds)
                    count+=1
                    countsingle +=1

    #two iteration benchmarks
    countdouble=0
    num_cs = 0
    for num_as in [7, 14, 21]:
        for num_bs in [0, 3, 6]:
            for num_ds in [0, 3, 6]:
                print(f"-----{num_as} elemA, {num_bs} elemB, {num_cs} elemC, {num_ds} elemD-----")
                iconf = setup_bm_instance(num_as, num_bs, 0, num_ds)
                run_incremental_benchmark_instance(iconf, run_in_seconds)
            
                print(f"Adding elements to the previous configuration: {num_as} elemA, {num_bs} elemB, {num_cs} elemC, {num_ds} elemD")
                add_elements("elementA", num_as, iconf)
                add_elements("elementB", num_bs, iconf)
                add_elements("elementD", num_ds, iconf)
                count+=1
                countdouble+=1
                run_incremental_benchmark_instance(iconf, run_in_seconds)

    #three iteration benchmarks
    counttriple=0
    num_cs = 0
    for num_as in [7, 21]:
        for num_bs in [0, 3]:
            for num_ds in [0, 6]:
                print(f"\n-----CURRENT CONFIGURATION: {num_as} As, {num_bs} Bs, {0} Cs, {num_ds} Ds-----")
                print(f"Adding to configuration: {num_as} As, {num_bs} Bs, {0} Cs, {num_ds} Ds")
                iconf = setup_bm_instance(num_as, num_bs, 0, num_ds)
                run_incremental_benchmark_instance(iconf, run_in_seconds)

                add_elements("elementA", num_as, iconf)
                add_elements("elementB", num_bs, iconf)
                add_elements("elementD", num_ds, iconf)
                run_incremental_benchmark_instance(iconf, run_in_seconds)

                for num_additional_as in [7, 14]:
                    for num_additional_bs in [6]:
                        for num_additional_ds in [3]:
                            print(f"Adding furhter elements to the previous configuration: {num_additional_as} As + {num_additional_bs} Bs + {num_additional_ds} Ds")

                            add_elements("elementA", num_additional_as, iconf)
                            add_elements("elementB", num_additional_bs, iconf)
                            add_elements("elementD", num_additional_ds, iconf)
                            count+=1
                            counttriple+=1
                            run_incremental_benchmark_instance(iconf, run_in_seconds)
    print("DONE" + " " + str(count) + "TOTAL - " + str(countsingle) + "SINGLE - " + str(countdouble) + "DOUBLE - " + str(counttriple) + "TRIPLE")

def case_should_create_rackDouble_does_not_terminate():
    """
    Run a benchmark case with 21 'elementA's that does not terminate.

    This function sets up a benchmark instance with 21 elementAs and tries to solve it.
    It's a (currently) faulty case that does not terminate as expected.
    """
    print("-----21 As-----")
    iconf = setup_bm_instance(21, 0, 0, 0)
    found = iconf.extend_incrementally(overshoot=False)

    iconf.select_found_configuration()
    print(iconf._time_grounding + iconf._time_solving)
    found.save_png("benchmarks/results", "-incrementalRackDouble")

# --------- Running benchmarks

def run(n_runs,fun,elements,name = "extend_solve"):
    """Main function called to run a benchmark

    Args:
        n_runs: Number of types to run the function
        fun: function to benchmark
        elements: the elements used for each run
        name (str, optional): The benchmark name used for saving
    """
    n_runs = 3
    results = []
    for e in elements:
        results.append(BM(n_runs,e,fun,ne=e))

    save_results(results,name)

#run_incremental_benchmarks(10)
#incremental_input_before()
#incremental_input_in_steps()
#case_should_create_rackDouble_does_not_terminate()