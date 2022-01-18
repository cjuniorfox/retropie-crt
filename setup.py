#!/usr/bin/python3
import json, subprocess

arguments = ['consoledisp','mastersystem','-i','-j']


proc = subprocess.Popen(arguments,stdout=subprocess.PIPE)
proc.wait()
data, err = proc.communicate()
if proc.returncode is 0:
    jsondata = data.decode('utf-8')
    scandata = json.loads(jsondata)
    print(scandata['x_resolution'],scandata['y_resolution'],scandata['vertical']['fps'])