# -*- coding: utf-8 -*-
# -*- mode: python -*-

from nose.tools import raises, assert_equal, assert_true, assert_almost_equal, assert_sequence_equal

from lmeasure import command

lm_metrics = [x["name"] for x in command.lm_functions]


@raises(RuntimeError)
def test_blank_file_rasies_error():
    with open("test/blank.swc", "rt") as fp:
        data = fp.read()
        out, err = command.run_lmeasure(data, lm_metrics[0])
        command.check_errors(err)


@raises(RuntimeError)
def test_garbage_input_raises_error():
    data = "blah blah blah"
    out, err = command.run_lmeasure(data, lm_metrics[0])
    command.check_errors(err)


@raises(ValueError)
def test_no_metrics_raises_error():
    data = "blah blah blah"
    out, err = command.run_lmeasure(data)


def test_swc_format_ok():
    with open("test/neuron.swc", "rt") as fp:
        data = fp.read()
        out, err = command.run_lmeasure(data, lm_metrics[0])
        command.check_errors(err)
        tuple(command.parse_results(out))


def test_neurolucida_format_ok():
    with open("test/neurolucida.asc", "rt") as fp:
        data = fp.read()
        out, err = command.run_lmeasure(data, lm_metrics[0])
        command.check_errors(err)
        tuple(command.parse_results(out))


def test_metric_names_match_list():
    with open("test/neuron.swc", "rt") as fp:
        data = fp.read()
        out, err = command.run_lmeasure(data, *lm_metrics)
        command.check_errors(err)
        result = tuple(command.parse_results(out))
        assert_sequence_equal([x['metric'] for x in result], lm_metrics)
