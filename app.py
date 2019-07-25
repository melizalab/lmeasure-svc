# -*- coding: utf-8 -*-
# -*- mode: python -*-

from flask import Flask, request, jsonify, url_for
from lmeasure import command, __version__

app = Flask(__name__)

@app.route('/', methods=["GET"])
def index():
    data = {
        "info": url_for('info'),
        "lmeasure": url_for('lmeasure'),
        "convert": url_for('convert')
    }
    return jsonify(data)


@app.route('/info/', methods=["GET"])
def info():
    try:
        version = command.get_version()
    except RuntimeError as e:
        return jsonify({"error": "l-measure failed: {!s}".format(e)}), 400
    return jsonify({
        "lmeasure-version": command.get_version(),
        "lmeasure-svc-version": __version__,
        "lmeasure-svc-docs": "https://github.com/melizalab/lmeasure-svc"
    })


measure_options = {
    "POST": {
        "description": "compute morphometrics from neural reconstructions",
        "parameters": {
            "data": {
                "type": "string",
                "description": "ASCII-encoded reconstruction. Allowed formats: {}".format(", ".join(command.lm_formats)),
                "required": True,
            },
            "metrics": {
                "type": "list",
                "description": "list of metrics to calculate. If not supplied, calculates all",
                "allowed_values": command.lm_function_names,
                "required": False,
            },
        }
    }
}


@app.route('/lmeasure/', methods=["POST", "OPTIONS"])
def lmeasure():
    if request.method == "OPTIONS":
        resp = jsonify(measure_options)
        resp.headers['Allow'] = "POST,OPTIONS"
        return resp
    elif request.method == "POST":
        if request.is_json:
            d = request.get_json()
        else:
            d = request.form
        if "data" not in d:
            return jsonify({"error": "no 'data' field in request"}), 400
        if "metrics" not in d:
            metrics = command.lm_function_names
        elif isinstance(d["metrics"], str):
            metrics = (d["metrics"],)
        elif isinstance(d["metrics"], list):
            metrics = d["metrics"]
        app.logger.debug('requested metrics: %s', metrics)
        try:
            out, err = command.run_lmeasure(d["data"], *metrics)
            app.logger.debug('stdout: %s', out)
            app.logger.debug('stderr: %s', err)
            command.check_errors(err)
            measures = [d for d in command.parse_results(out)]
        except KeyError as e:
            return jsonify({"error": "bad metric '{}' requested".format(e)}), 400
        except RuntimeError as e:
            return jsonify({"error": "l-measure failed: {!s}".format(e)}), 400
        else:
            return jsonify({"error": None, "measures": measures})


convert_options = {
    "POST": {
        "description": "convert reconstruction data to SWC format",
        "parameters": {
            "file": {
                "type": "string",
                "description": "ASCII-encoded reconstruction. Allowed formats: {}".format(", ".join(command.lm_formats)),
                "required": True,
            },
        }
    }
}


@app.route('/convert/', methods=["POST", "OPTIONS"])
def convert():
    if request.method == "OPTIONS":
        resp = jsonify(convert_options)
        resp.headers['Allow'] = "POST,OPTIONS"
        return resp
    elif request.method == "POST":
        if request.is_json:
            d = request.get_json()
        else:
            d = request.form
        if "data" not in d:
            return jsonify({"error": "no 'data' field in request"}), 400
        try:
            swc = command.run_convert(d["data"])
        except RuntimeError as e:
            return jsonify({"error": "l-measure failed: {!s}".format(e)}), 400
        else:
            return jsonify({"error": None, "data": swc})


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
