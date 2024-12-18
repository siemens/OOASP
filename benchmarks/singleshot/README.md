# Singleshot benchmarking for OOASP

In this directory is a collection of `.lp` files defining ooasp for the purposes of singleshot benchmarking, automated python script for running them and resulting outputs of the script.

## Automated Script

The benchmarking is meant to be run using the automated script `autorun.py`, which is to be run from the `singleshot_bench` directory.
The script works by automatically rewriting the `assumptions.lp` file and then using the Clingo python API to run solving and log the times.

### Domain sizes

The minimal domain sizes are calculated using a python script provided to team members. For now these should be considered the minimal solvable domain sizes.

### Logging

The script currently creates logs of found models in `results/models` and times per iteration in `results/times`.
Outdated `assumptions.lp` files are not logged by default, but this logging can be switch on by changing the `save` flag in `build_assumptions` function to `True`.