#!/usr/bin/python3
import sys
import subprocess
import re
from decimal import Decimal

class Res:
    def __init__(self):
        self.width = None
        self.lines = None
        self.fps = None,
        self.pal = None
        self.overscan_left = 10
        self.overscan_right = 10

def is_ntsc(fps):
    min_f=57
    max_f=62
    return min_f <= fps <= max_f

def is_pal(fps):
    min_f=48
    max_f=52
    return min_f <= fps <=max_f

def is_pal_by_lines(lines):
    min_i = 506
    max_i = 580
    min_p = 253
    max_p = 290
    return (min_i <= lines <= max_i) or (min_p <= lines <= max_p)

def is_interlaced(freq):
    min_pal = 24
    max_pal = 26
    min_ntsc = 28
    max_ntsc = 31
    return (min_pal <= freq <= max_pal) or (min_ntsc <= freq <= max_ntsc)

def apply_chvideo(res):
    if res.width is not None:
        print("Horizontal resolution:", res.width)
        print("Vertical resolution:", res.lines)
        print("FPS:", res.fps)

        chvideo_command = ['chvideo', 
            '--width', str(res.width), 
            '--lines', str(res.lines), 
            '--frequency', str(res.fps),  
            '--overscan-left', str(res.overscan_left), 
            '--overscan-right', str(res.overscan_right)
        ] + (['--pal'] if res.pal else [])
        subprocess.run(chvideo_command)
    else:
        print("Pattern 'Geometry' not found.")

def apply_values_to_res(match):
    res = Res()
    res.width = int(match.group(1))
    res.lines = int(match.group(2))
    fps = Decimal(match.group(3))
    res.fps = fps * 2 if is_interlaced(fps) else fps
    ntsc = is_ntsc(res.fps)
    pal = is_pal(res.fps)
    if not (ntsc or pal):
        pal = is_pal_by_lines(res.lines)
    res.pal = pal
    return res

def search_for_match(command):
    process = subprocess.Popen(command + " --verbose", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        line = process.stdout.readline()
        if not line:
            break
        if b'Geometry' in line:
            match = re.search(r'Geometry: (\d+)x(\d+).*FPS: ([\d.]+)', line.decode())
            if match:
                apply_chvideo(apply_values_to_res(match))
            break
    process.terminate()
    process.wait()

if len(sys.argv) < 2:
    print("Usage: python script.py <command>")
    sys.exit(1)

command = sys.argv[1]
search_for_match(command)