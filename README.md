
# lmeasure-svc

An HTTP wrapper for [L-Measure](http://cng.gmu.edu:8080/Lm/), which is a tool for quantifying features of neuronal morphologies, in a containerized web service.

## Quick start

To start the service running in a container, run:

    docker run --rm -p 5000:5000 melizalab/lmeasure-svc

If you intend to deploy the container behind an nginx proxy:

    docker stack deploy -c docker-compose.yml morpho

## Build the docker image:

`docker build -t melizalab/lmeasure-svc .` Replace `melizalab` with your own docker cloud ID.
