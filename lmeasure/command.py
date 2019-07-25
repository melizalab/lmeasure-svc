# -*- coding: utf-8 -*-
# -*- mode: python -*-
"""Functions for running lmeasure command"""
import os
import re
import logging

log = logging.getLogger('lmeasure')   # root logger

lm_cmd = "lmeasure"             # assume l-measure is on the path

err_regex = [{"re": re.compile(b"File type is not supported"),
              "message": "unsupported input format"}]

ver_regex = re.compile(rb"Release ([A-Za-z0-9.]+)")

lm_formats = ["SWC", "Neurolucida V3", "Amaral", "Claiborne", "Eutectic", "Amira"]

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
    {'name': 'Branch_Order', 'index': 18, 'dtype': int, 'units': ''},
    {'name': 'Terminal_degree', 'index': 19, 'dtype': int, 'units': ''},
    {'name': 'TerminalSegment', 'index': 20, 'dtype': int, 'units': ''},
    {'name': 'Taper_1', 'index': 21, 'dtype': float, 'units': ''},
    {'name': 'Taper_2', 'index': 22, 'dtype': float, 'units': ''},
    {'name': 'Branch_pathlength', 'index': 23, 'dtype': float, 'units': 'um'},
    {'name': 'Contraction', 'index': 24, 'dtype': float, 'units': ''},
    {'name': 'Fragmentation', 'index': 25, 'dtype': float, 'units': ''},
    {'name': 'Daughter_Ratio', 'index': 26, 'dtype': float, 'units': ''},
    {'name': 'Parent_Daughter_Ratio', 'index': 27, 'dtype': float, 'units': ''},
    {'name': 'Partition_asymmetry', 'index': 28, 'dtype': float, 'units': ''},
    {'name': 'Rall_Power', 'index': 29, 'dtype': float, 'units': ''},
    {'name': 'Pk', 'index': 30, 'dtype': float, 'units': ''},
    {'name': 'Pk_classic', 'index': 31, 'dtype': float, 'units': ''},
    {'name': 'Pk_2', 'index': 32, 'dtype': float, 'units': ''},
    {'name': 'Bif_ampl_local', 'index': 33, 'dtype': float, 'units': 'deg'},
    {'name': 'Bif_ampl_remote', 'index': 34, 'dtype': float, 'units': 'deg'},
    {'name': 'Bif_tilt_local', 'index': 35, 'dtype': float, 'units': 'deg'},
    {'name': 'Bif_tilt_remote', 'index': 36, 'dtype': float, 'units': 'deg'},
    {'name': 'Bif_torque_local', 'index': 37, 'dtype': float, 'units': 'deg'},
    {'name': 'Bif_torque_remote', 'index': 38, 'dtype': float, 'units': 'eg'},
    {'name': 'Last_parent_diam', 'index': 39, 'dtype': float, 'units': 'um'},
    {'name': 'Diam_threshold', 'index': 40, 'dtype': float, 'units': 'um'},
    {'name': 'HillmanThreshold', 'index': 41, 'dtype': float, 'units': 'um'},
    {'name': 'Helix', 'index': 43, 'dtype': float, 'units': 'um'},
    {'name': 'Fractal_Dim', 'index': 44, 'dtype': float, 'units': ''},
)

# map function names to numbers
lm_function_map = {x["name"]: x for x in lm_functions}
lm_function_names = tuple(x["name"] for x in lm_functions)


def measure_arg(name):
    """Convert measure name to an lmeasure CLI argument"""
    return "-f{:d},0,0,10.0".format(lm_function_map[name]['index'])


def make_command(infile, *fns):
    """Return shell command to perform all the measures in [fns] on infile"""
    fnargs = [measure_arg(fn) for fn in fns]
    return [lm_cmd] + fnargs + [infile]


def get_version():
    """Run lmeasure and get the version number from the output"""
    import subprocess
    from tempfile import NamedTemporaryFile
    proc = subprocess.Popen(lm_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        out, stderr = proc.communicate(timeout=15)
    except TimeoutError:
        proc.kill()
        outs, stderr = proc.communicate()
        raise RuntimeError("command timed out")
    else:
        m = ver_regex.search(stderr.split(b'\n')[0])
        if m is None:
            log.debug("unable to parse version from output: %s", stderr)
            raise RuntimeError("unable to determine version from command output")
        else:
            return m.group(1).decode('ascii')


def run_lmeasure(data, *fns):
    """Run lmeasure on data and return CompletedProcess

    data: string in a format L-Measure understands. This will be stored in a temporary file in ASCII encoding.
    """
    # TODO: make this function asynchronous
    import subprocess
    from tempfile import NamedTemporaryFile

    if len(fns) < 1:
        raise ValueError("specify at least one metric")

    # data needs to be placed in a temporary file
    with NamedTemporaryFile(mode="w+t", suffix=".txt", encoding="ascii", delete=True) as fp:
        fp.write(data)
        fp.flush()

        cmd = make_command(fp.name, *fns)
        log.debug("executing: %s", ' '.join(cmd))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            return proc.communicate(timeout=15)
        except TimeoutError:
            proc.kill()
            outs, errs = proc.communicate()
            raise RuntimeError("command timed out")


def run_convert(data):
    """Run lmeasure to convert data to SWC format"""
    import subprocess
    from tempfile import TemporaryDirectory

    # data needs to be placed in a temporary file
    with TemporaryDirectory() as tmpdir:
        tmpfile = os.path.join(tmpdir, "input.txt")
        with open(tmpfile, "w+t", encoding="ascii") as fp:
            fp.write(data)
            fp.flush()
            cmd = [lm_cmd, "-p", tmpfile]
            log.debug("executing: %s", ' '.join(cmd))
            proc = subprocess.Popen(cmd, stderr=subprocess.PIPE)
            try:
                out, errs = proc.communicate(timeout=15)
            except TimeoutError:
                proc.kill()
                outs, errs = proc.communicate()
                raise RuntimeError("command timed out")
            check_errors(errs)
            outfile = tmpfile + ".swc"
            with open(outfile, "rt", encoding="ascii") as ofp:
                return ofp.read()


def check_errors(stderr):
    """Check stderr output of lmeasure and raise errors if there was a failure"""
    for ee in err_regex:
        if ee['re'].search(stderr) is not None:
            raise RuntimeError(ee['message'])


def parse_results(stdout):
    """Parse output of lmeasure into a python data structure

    stdout: byte string with the output of a successful lmeasure run

    Lmeasure returns data in a tabular form, with the fields:
    <cell> <metric> <total> <n_compart> (<n_exclude>) <min> <avg> <max> <sd>

    This function returns a generator that yields dictionaries containing these
    fields except 'cell' and adding 'units'.

    """
    for line in stdout.split(b"\n"):
        log.debug("processing line %s", line)
        fields = line.strip().split()
        if len(fields) != 9:
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
    p.add_argument("--version", "-v", help="show version information", action="store_true")
    p.add_argument("--all", "-A", help="run all functions on input", action="store_true")
    p.add_argument("function", nargs="*")

    args = p.parse_args()

    ch = logging.StreamHandler()
    formatter = logging.Formatter("[%(name)s] %(message)s")
    loglevel = logging.DEBUG
    log.setLevel(loglevel)
    ch.setLevel(loglevel)  # change
    ch.setFormatter(formatter)
    log.addHandler(ch)

    if args.version:
        version = get_version()
        log.info("lmeasure version: %s", version)
        return

    if args.all:
        args.function = [x['name'] for x in lm_functions]

    data = sys.stdin.read()

    try:
        out, err = run_lmeasure(data, *args.function)
        log.debug("stderr: %s", err)
        check_errors(err)
    except Exception as e:
        print("Error: {!s}".format(e))
    else:
        for d in parse_results(out):
            print(d)
