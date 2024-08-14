import os
from ooasp.run import OOASPRacksSolver
import json


def run(args, sf, file_name):
    default_namespace = OOASPRacksSolver.get_parser().parse_args([])

    for key, value in args.items():
        setattr(default_namespace, key, value)
    solver = OOASPRacksSolver(
        default_namespace,
        smart_generation_functions=sf,
    )
    solver.run()
    file_path = os.path.join(
        "benchmarks", "results", "smart-generation", f"{file_name}.json"
    )
    with open(file_path, "w") as f:
        j = solver.stats
        j["args"] = args
        j["smart_functions"] = sf
        print(json.dumps(j, indent=4), file=f)
        print(f"Benchmark saved in {file_path}")


if __name__ == "__main__":

    # TODO Create different benchmarks with different smart generation functions and initial objects
    smart_generation_functions = [
        "lb_at_least",
        "lower_global",
        "upper_filled",
        "association_needed_lb",
    ]
    args = {
        "frame": 17,
    }

    run(args, smart_generation_functions, "17frames")
