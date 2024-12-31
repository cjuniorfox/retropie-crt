#!/usr/bin/python3
import sys
import subprocess
import re
from decimal import Decimal
import argparse
import json
import logging
import time

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

def setup_logging(level=logging.INFO):
    logging.basicConfig(
        format='[%(levelname)s] %(message)s',
        level=level
    )


def is_ntsc(fps):
    min_f=57
    max_f=62
    logging.debug("Checking if is NTSC by FPS. If FPS is between {} and {}: {}".format( min_f, max_f, fps))
    return min_f <= fps <= max_f

def is_pal(fps):
    min_f=48
    max_f=52
    logging.debug("Checking if is PAL by FPS. If FPS is between {} and {}: {}".format( min_f, max_f, fps))
    return min_f <= fps <=max_f

def is_pal_by_lines(lines):
    min_i = 506
    max_i = 580
    min_p = 253
    max_p = 290
    logging.debug("Checking if is PAL by vertical resolution (lines). If lines is between {} and {} (progressive), or {} and {} (interlaced)  {}".format( min_i, max_i, min_p, max_p, lines))
    return (min_i <= lines <= max_i) or (min_p <= lines <= max_p)

def is_interlaced(freq):
    min_pal = 24
    max_pal = 26
    min_ntsc = 28
    max_ntsc = 31
    logging.debug("Checking if is interlaced or progressive by FPS. Between {} and {} for progressive PAL, or between {} and {} for progressive NTSC: {}".format( min_pal, max_pal, min_ntsc, max_ntsc, freq))
    return (min_pal <= freq <= max_pal) or (min_ntsc <= freq <= max_ntsc)

def apply_chvideo(res):
    logging.debug("Setting up the television specs with the chvideo utility.")
    if res.width is not None:
        logging.debug("Horizontal resolution: %s" % res.width)
        logging.debug("Vertical resolution: %s" % res.lines)
        logging.debug("Frames per second: %s" % res.fps)
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
            logging.warning("chvideo not found. assuming is just for testing. Follows de 'chvideo' command:\n")
            print(' '.join([" $"] + chvideo_command + ["\n"]))
    else:
        logging.error("Pattern 'Geometry' not found.")

def create_json_file(res,crt_json_path):
    logging.debug("Creating the JSON file in the following path: \"%s\"" % crt_json_path)
    res_dict = res.to_dict()
    with open(crt_json_path, 'w') as json_file:
        json.dump(res_dict, json_file, indent=4)

def read_res_from_json(crt_json_file):
    logging.debug("Trying to read the JSON file from the following path: \"%s\"", crt_json_file)
    with open(crt_json_file, 'r') as json_file:
        res_dict = json.load(json_file)
    res = Res(res_dict)
    return res

def geometry_values_from_retroarch(match):
    logging.debug("Extracting the geometry values from Retroarch's logging output")
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
    logging.debug("Executing Retroarch and searching for matches in the Retroarch logging output to extract the geometry values.")
    timeout = 60 
    process = subprocess.Popen(command + " --verbose", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    start_time = time.time()
    res = None
    while True:
        line = process.stdout.readline()
        if not line:
            break
        if b'Geometry' in line:
            logging.debug("Found line in the Retroarch's logging about geometry.")
            match = re.search(r'Geometry: (\d+)x(\d+).*FPS: ([\d.]+)', line.decode())
            if match:
                logging.debug("Geometry values found in the Retroarch's logging.")
                res = geometry_values_from_retroarch(match)
            break
        if time.time() - start_time >= timeout:
            logging.critical("Timeout reached. Geometry value not found.")
            raise TimeoutError("Timeout looking for Geometry value while executing \"%s\"." % command)
    process.terminate()
    process.wait()
    if res is None:
        raise ValueError("Unable to obtain the Geometry values executing \"%s\"." % command)
    return res

def main(args): 
    logging_level = args.logging_level
    setup_logging(logging_level)
    has_json_file = args.rom_file is not None
    crt_json_path = re.sub(r'\.\w+$', '-crt.json', args.rom_file) if has_json_file else None
    res = None
    if crt_json_path is not None:
        logging.debug("Path for reading the JSON file defined. Will try to read the existing JSON file (if any and is valid) or create a new one.")
        try:
            res = read_res_from_json(crt_json_path)
            logging.debug("Geometry values from JSON file loaded. If the values are correct, there's no need for executing Retroarch.")
            has_json_file = False
        except FileNotFoundError:
            logging.debug("JSON file not found. Will be created a new one.")
            res = None
        except json.decoder.JSONDecodeError :
            logging.debug("Unable to decode de JSON file, will be created a new one")
            res = None
    if res is None or res.width is None or res.lines is None:
        logging.debug("Currently don't having any geometry settings. I'll load the game and try to extract the geometry specs.")
        res = search_for_match(args.command)
        if has_json_file:
            create_json_file(res,crt_json_path)
    apply_chvideo(res)
    

parser = argparse.ArgumentParser(description="Command the chvideo.py to matches the output display with the game's geometry specs.")
parser.add_argument("--command","-c",type=str, help = "Retroarch command for launching the ROM game",required=True)
parser.add_argument("--rom-file","-r",type=str, help = "Path for the ROM file.", required=False)
parser.add_argument('--logging-level', dest='logging_level', default='INFO',choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],help='Set the logging level')
args = parser.parse_args()

main(args)