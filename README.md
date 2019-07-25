
# lmeasure-svc

An HTTP wrapper for [L-Measure](http://cng.gmu.edu:8080/Lm/), which is a tool for quantifying features of neuronal morphologies, in a containerized web service.

## Starting the service

To start the service running in a container, run:

    docker run --rm -p 5000:5000 melizalab/lmeasure-svc

If you intend to deploy the container behind an nginx proxy:

    docker stack deploy -c docker-compose.yml morpho

## Using the HTTP API

Assuming you have [httpie](https://httpie.org/) installed; use curl instead if you prefer.

Get a list of endpoints:

    http GET http://localhost:5000/

Get a list of supported metrics:

    http OPTIONS http://localhost:5000/lmeasure/

Compute all the supported measures from `file.DAT`

    http POST https://gracula.psyc.virginia.edu/morpho/lmeasure/ data=@file.DAT

You can restrict the output to specific measures like so:

    http POST https://gracula.psyc.virginia.edu/morpho/lmeasure/ data=@file.DAT metrics:='["Fractal_Dim"]'

Convert Neurolucide or other file formats to SWC. You don't have to do this before computing measures; it's just for convenience.

    http POST http://localhost:5000/convert/ data=@file.DAT


## Build the docker image:

`docker build -t melizalab/lmeasure-svc .` Replace `melizalab` with your own docker cloud ID.
