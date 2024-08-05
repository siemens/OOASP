# Singleshot benchmarking for OOASP

In this directory is collection of `.lp` files defining ooasp for purposes of singleshot benchmarking, automated python script for running them and resulting outputs of the script.

## Automated Script

The benchmarking is meant to be run using automated script `autorun.py`, which is to be run from the `singleshot_bench` directory.
The script works by automatically rewriting the `assumptions.lp` file and then using the Clingo python API to run solving and log times.

### Domain sizes

As of now, the domain sizes (which need to be specified for singleshot) are only roughly approximated by formula: `n*19`, as the smallest configuration given one element of each type is 19. *Better approximation is to be further developed*.

### Logging

The script currently creates logs of found models in `results/models` and times per iteration in `results/times`.
Outdated `assumptions.lp` files are not logged by default, but this logging can be switch on by changing the `save` flag in `build_assumptions` function to `True`.