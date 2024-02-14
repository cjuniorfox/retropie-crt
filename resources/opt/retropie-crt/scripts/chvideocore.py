#!/usr/bin/python3
import sys
import subprocess
import re
from decimal import Decimal
import argparse
import json

class Res:    
    def __init__(self, res_dict=None):
        self._init_empty()
        if res_dict is not None:
            self.from_dict(res_dict)
        
    
    def _init_empty(self):
        self.width = None
        self.lines = None
        self.fps = None,
        self.pal = None
        self.overscan_left = 10
        self.overscan_right = 10
    
    def from_dict(self,res_dict):
        self.width = res_dict.get('width') 
        self.lines = res_dict.get('lines')
        self.fps = res_dict.get('fps')
        self.pal = res_dict.get('pal')
        self.overscan_left = res_dict.get('overscan_left') if res_dict.get('overscan_left') is not None else self.overscan_left
        self.overscan_right = res_dict.get('overscan_right') if res_dict.get('overscan_right') is not None else self.overscan_right
        return self
        
    def to_dict(self):
        return {
        "width": self.width,
        "lines" : self.lines,
        "fps" : str(self.fps),
        "pal" : self.pal,
        "overscan_left" : self.overscan_left,
        "overscan_right" : self.overscan_right
    }


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
        try :
            chvideo_command = ['chvideo', 
                '--width', str(res.width), 
                '--lines', str(res.lines), 
                '--frequency', str(res.fps),  
                '--overscan-left', str(res.overscan_left), 
                '--overscan-right', str(res.overscan_right)
            ] + (['--pal'] if res.pal else [])
            subprocess.run(chvideo_command)
        except FileNotFoundError:
            print("chvideo not found. assuming is just for testing. Follows de 'chvideo' command:\n")
            print(' '.join([" $"] + chvideo_command + ["\n"]))
    else:
        print("Pattern 'Geometry' not found.")

def create_json_file(res,crt_json_path):
    res_dict = res.to_dict()
    with open(crt_json_path, 'w') as json_file:
        json.dump(res_dict, json_file, indent=4)

def read_res_from_json(crt_json_file):
    with open(crt_json_file, 'r') as json_file:
        res_dict = json.load(json_file)
    res = Res(res_dict)
    return res

def geometry_values_from_retroarch(match):
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
                res = geometry_values_from_retroarch(match)
            break
    process.terminate()
    process.wait()
    return res

def __main__(args):
    crt_json_path = re.sub(r'\.\w+$', '-crt.json', args.rom_path) if args.rom_path is not None else None
    res = None
    if crt_json_path is not None:
        try:
            res = read_res_from_json(crt_json_path)
        except FileNotFoundError:
            res = None
        except json.decoder.JSONDecodeError :
            res = None
    if res is None or res.width is None or res.lines is None:
        res = search_for_match(args.command)
        if crt_json_path is not None:
            create_json_file(res,crt_json_path)
    apply_chvideo(res)
    

parser = argparse.ArgumentParser(description="Command the chvideo.py to matches the output display with the game's geometry specs.")
parser.add_argument("--command","-c",type=str, help = "Retroarch command for launching the ROM game",required=True)
parser.add_argument("--rom-path","-r",type=str, help = "Path for the ROM file.", required=False)
args = parser.parse_args()

__main__(args)