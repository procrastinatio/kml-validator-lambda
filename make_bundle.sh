#!/bin/bash

export VENV=/home/ec2-user/



zip -9 bundle.zip handler.py

cd _env/lib/python2.7/dist-packages/
zip -r9 ~/kml_validator/bundle.zip *
cd -
cd _env/lib64/python2.7/dist-packages/
zip -r9 ~/kml_validator/bundle.zip *

