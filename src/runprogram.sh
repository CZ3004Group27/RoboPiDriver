#!/bin/bash
sudo hciconfig hci0 piscan
libcamerify --framerate 0 —exposure long python3 ./main.py
