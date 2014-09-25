ITM Probe network information flow tool
=======================================

Introduction
------------

[ITM Probe](http://www.ncbi.nlm.nih.gov/CBBresearch/Yu/downloads/itmprobe.html)
 is a tool for calculating information flow in biological networks.
It is part of the [qmbpmn-tools](ftp://ftp.ncbi.nlm.nih.gov/pub/qmbpmn/qmbpmn-tools/)
package from the [NCBI](http://www.ncbi.nlm.nih.gov).

This repository provides a small wrapper script (`infflow.py`) and a virtual
environment to get up and running with ITM Probe quickly. The wrapper inputs and outputs
to the widely used [GML](https://en.wikipedia.org/wiki/Graph_Modelling_Language) format.

Virtual environment with Docker
-------------------------------

ITM Probe has many software dependencies which are difficult and time
consuming to install manually. [Docker](https://www.docker.com/whatisdocker/)
 is a virtual environment which allows you to get up and running quickly
 with ITM Probe. It's like a virtual machine but with less overhead.

First, you'll need to install Docker. See its [documentation](https://docs.docker.com/)
for help with that.

Then you can install the ITM Probe virtual environment using the
[Dockerfile](Dockerfile) supplied here:

`sudo docker build -t itmprobe .`

Once installed, you can run the virtual environment like so:

`sudo docker run -it itmprobe /bin/bash`

Then you can proceed within the virtual environment in the same way as if you'd installed
everything locally.

The ITM Probe wrapper
---------------------

For help and list of command line options:

`python infflow.py --help`

Example using supplied gml file:

`python infflow.py example.gml`
