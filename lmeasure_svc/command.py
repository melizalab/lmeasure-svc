# -*- coding: utf-8 -*-
# -*- mode: python -*-
"""Functions for running lmeasure command"""

# the l-measure fns, in order of their identifiers
lm_functions = ["Soma_Surface",
                "N_stems",
                "N_bifs",
                "N_branch",
                "N_tips",
                "Width",
                "Height",
                "Depth",
                "Type",
                "Diameter",
                "Diameter_pow",
                "Length",
                "Surface",
                "SectionArea",
                "Volume",
                "EucDistance",
                "PathDistance",
                "XYZ",
                "Branch_Order",
                "Terminal_degree",
                "TerminalSegment",
                "Taper_1",
                "Taper_2",
                "Branch_pathlength",
                "Contraction",
                "Fragmentation",
                "Daughter_Ratio",
                "Parent_Daughter_Ratio",
                "Partition_asymmetry",
                "Rall_Power",
                "Pk",
                "Pk_classic",
                "Pk_2",
                "Bif_ampl_local",
                "Bif_ampl_remote",
                "Bif_tilt_local",
                "Bif_tilt_remote",
                "Bif_torque_local",
                "Bif_torque_remote",
                "Last_parent_diam",
                "Diam_threshold",
                "HillmanThreshold",
                "Helix",
                "Fractal_Dim"]


# map function names to numbers
lmf_map = {n: i for i, n in enumerate(lm_functions)}


def measure_arg(name):
    """Convert measure name to an lmeasure CLI argument"""
    return "-f{:d},0,0,10.0".format(lmf_map[name])


def make_command(infile, *fns):
    """Return shell command to perform all the measures in [fns] on infile"""
    fnargs = [measure_arg(fn) for fn in fns]
    return ["/io/lmeasure"] + fnargs + [infile]


def run_lmeasure(data, *fns):
    """Run lmeasure on data and return CompletedProcess

    data: string in a format L-Measure understands. This will be stored in a temporary file in ASCII encoding.
    """
    # data needs to be placed in a temporary file
    import subprocess
    from tempfile import NamedTemporaryFile

    with NamedTemporaryFile(mode="w+t", suffix=".txt", encoding="ascii", delete=True) as fp:
        fp.write(data)
        fp.flush()

        cmd = make_command(fp.name, *fns)
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
