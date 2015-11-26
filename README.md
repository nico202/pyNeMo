pyNeMo
======

Quick &amp; dirty interface for the NeMo python API

Installation:
-------------

It depends on the NeMo python API and on the Image library (`pip2 install Image`\) and on neuronpy (`pip2 install neuronpy`\)

Download it: `git clone https://github.com/nico202/pyNeMo`

cd to the dir: `cd pyNeMo`

Running:
--------

edit the `general_config.py` file to your needs.

Try it: `python2 Runner.py nets/Watts.py`

Show the resulting spikes:

`cat .store/history`  
find the name of the latest generated file

`python2 ShowSpikes.py .store/.HASH_1 + HASH_2`

Hack!
-----

Read the source and do what you want
