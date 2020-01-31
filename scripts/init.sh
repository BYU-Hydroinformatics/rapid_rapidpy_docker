#!/bin/bash

ServiceToUse="${SERVICE:-aws}"
echo "Running Init script"
python /home/scripts/download_$ServiceToUse.py
echo "Downloading of input weight files complete"
python /home/run_script.py