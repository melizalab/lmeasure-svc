# -*- coding: utf-8 -*-
# -*- mode: python -*-
"""Functions for running lmeasure command"""
import re

# the l-measure fns, in order of their identifiers
lm_functions = (
    {'name': 'Soma_Surface', 'index': 0, 'dtype': float, 'units': 'um**2'},
    {'name': 'N_stems', 'index': 1, 'dtype': int, 'units': ''},
    {'name': 'N_bifs', 'index': 2, 'dtype': int, 'units': ''},
    {'name': 'N_branch', 'index': 3, 'dtype': int, 'units': ''},
    {'name': 'N_tips', 'index': 4, 'dtype': int, 'units': ''},
    {'name': 'Width', 'index': 5, 'dtype': float, 'units': 'um'},
    {'name': 'Height', 'index': 6, 'dtype': float, 'units': 'um'},
    {'name': 'Depth', 'index': 7, 'dtype': float, 'units': 'um'},
    {'name': 'Type', 'index': 8, 'dtype': int, 'units': ''},
    {'name': 'Diameter', 'index': 9, 'dtype': float, 'units': 'um'},
    {'name': 'Diameter_pow', 'index': 10, 'dtype': float, 'units': 'um'},
    {'name': 'Length', 'index': 11, 'dtype': float, 'units': 'um'},
    {'name': 'Surface', 'index': 12, 'dtype': float, 'units': 'um**2'},
    {'name': 'SectionArea', 'index': 13, 'dtype': float, 'units': 'um**2'},
    {'name': 'Volume', 'index': 14, 'dtype': float, 'units': 'um**3'},
    {'name': 'EucDistance', 'index': 15, 'dtype': float, 'units': 'um'},
    {'name': 'PathDistance', 'index': 16, 'dtype': float, 'units': 'um'},
    {'name': 'Branch_Order', 'index': 17, 'dtype': int, 'units': ''},
    {'name': 'Terminal_degree', 'index': 18, 'dtype': int, 'units': ''},
    {'name': 'TerminalSegment', 'index': 19, 'dtype': int, 'units': ''},
    {'name': 'Taper_1', 'index': 20, 'dtype': float, 'units': ''},
    {'name': 'Taper_2', 'index': 21, 'dtype': float, 'units': ''},
    {'name': 'Branch_pathlength', 'index': 22, 'dtype': float, 'units': 'um'},
    {'name': 'Contraction', 'index': 23, 'dtype': float, 'units': ''},
    {'name': 'Fragmentation', 'index': 24, 'dtype': float, 'units': ''},
    {'name': 'Daughter_Ratio', 'index': 25, 'dtype': float, 'units': ''},
    {'name': 'Parent_Daughter_Ratio', 'index': 26, 'dtype': float, 'units': ''},
    {'name': 'Partition_asymmetry', 'index': 27, 'dtype': float, 'units': ''},
    {'name': 'Rall_Power', 'index': 28, 'dtype': float, 'units': ''},
    {'name': 'Pk', 'index': 29, 'dtype': float, 'units': ''},
    {'name': 'Pk_classic', 'index': 30, 'dtype': float, 'units': ''},
    {'name': 'Pk_2', 'index': 31, 'dtype': float, 'units': ''},
    {'name': 'Bif_ampl_local', 'index': 32, 'dtype': float, 'units': 'deg'},
    {'name': 'Bif_ampl_remote', 'index': 33, 'dtype': float, 'units': 'deg'},
    {'name': 'Bif_tilt_local', 'index': 34, 'dtype': float, 'units': 'deg'},
    {'name': 'Bif_tilt_remote', 'index': 35, 'dtype': float, 'units': 'deg'},
    {'name': 'Bif_torque_local', 'index': 36, 'dtype': float, 'units': 'deg'},
    {'name': 'Bif_torque_remote', 'index': 37, 'dtype': float, 'units': 'eg'},
    {'name': 'Last_parent_diam', 'index': 38, 'dtype': float, 'units': 'um'},
    {'name': 'Diam_threshold', 'index': 39, 'dtype': float, 'units': 'um'},
    {'name': 'HillmanThreshold', 'index': 40, 'dtype': float, 'units': 'um'},
    {'name': 'Helix', 'index': 42, 'dtype': float, 'units': 'um'},
    {'name': 'Fractal_Dim', 'index': 44, 'dtype': float, 'units': ''},
)

# map function names to numbers
lm_function_map = {x["name"]: x for x in lm_functions}


def measure_arg(name):
    """Convert measure name to an lmeasure CLI argument"""
    return "-f{:d},0,0,10.0".format(lm_function_map[name]['index'])


def make_command(cmd, infile, *fns):
    """Return shell command to perform all the measures in [fns] on infile"""
    fnargs = [measure_arg(fn) for fn in fns]
    return [cmd] + fnargs + [infile]


def run_lmeasure(cmd, data, *fns):
    """Run lmeasure on data and return CompletedProcess

    cmd: path to lmeasure commandline executable
    data: string in a format L-Measure understands. This will be stored in a temporary file in ASCII encoding.
    """
    # TODO: make this function asynchronous
    import subprocess
    from tempfile import NamedTemporaryFile

    # data needs to be placed in a temporary file
    with NamedTemporaryFile(mode="w+t", suffix=".txt", encoding="ascii", delete=False) as fp:
        fp.write(data)
        fp.flush()

        cmd = make_command(cmd, fp.name, *fns)
        # TODO check for hanging process; there will be a message in stderr
        return subprocess.run(cmd, timeout=10, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# error handling
class InvalidFormat(RuntimeError):
    message = "unsupported input format"
    rex = re.compile(b"File type is not supported")


lm_errs = (InvalidFormat,)


def check_errors(stderr):
    """Check stderr output of lmeasure and raise errors if there was a failure"""
    for klass in lm_errs:
        if klass.rex.search(stderr) is not None:
            raise klass


def parse_results(stdout):
    """Parse output of lmeasure into a python data structure

    stdout: byte string with the output of a successful lmeasure run

    Lmeasure returns data in a tabular form, with the fields:
    <cell> <metric> <total> <n_compart> (<n_exclude>) <min> <avg> <max> <sd>

    This function returns a generator that yields dictionaries containing these
    fields except 'cell' and adding 'units'.

    """
    for line in stdout.split(b"\n"):
        fields = line.strip().split()
        if len(fields) == 0:
            continue
        metric = fields[1].decode("ascii")
        info = lm_function_map[metric]
        dtype = info['dtype']
        yield {
            "metric": metric,
            "n_compart": int(fields[3]),
            "n_exclude": int(fields[4].strip(b"()")),
            "total": dtype(fields[2]),
            "min": dtype(fields[5]),
            "avg": float(fields[6]),
            "max": dtype(fields[7]),
            "units": info["units"],
        }


def main(argv=None):
    """ Test script """
    import sys
    import argparse

    p = argparse.ArgumentParser(description="run lmeasure on standard input")
    p.add_argument("--all", "-A", help="run all functions on input", action="store_true")
    p.add_argument("function", nargs="*")

    args = p.parse_args()

    if args.all:
        args.function = [x['name'] for x in lm_functions]

    if len(args.function) < 1:
        print("Error: specify at least one metric or use --all")
        sys.exit(-1)

    data = sys.stdin.read()
    proc = run_lmeasure("/io/lmeasure", data, *args.function)
    try:
        check_errors(proc.stderr)
    except RuntimeError as e:
        print("Error: {}".format(e.message))
    for d in parse_results(proc.stdout):
        print(d)
