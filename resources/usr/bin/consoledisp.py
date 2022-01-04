#!/usr/bin/python3

import argparse
import subprocess

parser = argparse.ArgumentParser(description="Apply settings for desired game console")
parser.add_argument("console",help="Desired game consol")
parser.add_argument("--pal","-P",action='store_true',help="Apply PAL settings")
parser.add_argument("--info","-i",action='store_true',help="Only print without applyng any change")
args = parser.parse_args()
isPal = args.pal
info = args.info

def getcmd(width=348,ntsc_freq=59.975,pal_freq=50.01,oTop=0,oBottom=0,oLeft=0,oRight=0,isProgressive=True) :
    global isPal
    global info
    freq = pal_freq if isPal else ntsc_freq
    cmd = ["chvideo","-w",str(width), "-f", str(freq), "-L",str(oLeft),"-R",str(oRight),"-T",str(oTop),"-B",str(oBottom)]
    if isProgressive :
        cmd.append("-p")
    if isPal :
        cmd.append("-P")
    if info :
        cmd.append("-i")

    return cmd

def megadrive() :
    return getcmd(width=1392,ntsc_freq=59.92)

def mastersystem() :
    return getcmd(width=284,ntsc_freq=59.92)

def tms9918() :
    return getcmd(width=256,ntsc_freq=59.92,oLeft=14,oRight=14,oTop=24,oBottom=24)

def neogeo() :
    return getcmd(width=348,ntsc_freq=59.185)

def nes() :
    return getcmd(width=256,ntsc_freq=60.1,oLeft=10,oRight=10)

def snes() :
    return getcmd(width=542,ntsc_freq=60.1)

def pcengine() :
    return getcmd(width=256,ntsc_freq=59.94,oLeft=10,oRight=10)

def mame_libretro() :
    return getcmd(width=1920,ntsc_freq=59.94,oLeft=25,oRight=25)

def atarilynx() :
    return getcmd(width=348,ntsc_freq=59.94)

def gameboy() :
    return getcmd(width=320,ntsc_freq=59.73,oLeft=10,oRight=10)

def atari2600() :
    return getcmd(width=348,ntsc_freq=59.92,oTop=-8,oBottom=-2)

def atari5200() :
    return getcmd(width=352,ntsc_freq=59.92)

def atari7800() :
    return getcmd(width=348,ntsc_freq=59.92)

def ngp() :
    return getcmd(width=256,ntsc_freq=60,oLeft=10,oRight=10)

def n64() :
    return getcmd(width=696,ntsc_freq=60,oLeft=10,oRight=10)

def x68000() :
    return getcmd(width=1024,oLeft=10,oRight=10,ntsc_freq=55.45)

console={
    'megadrive':megadrive(),
    'genesis': megadrive(),
    'sega32x': megadrive(),
    'segacd' : megadrive(),
    'mastersystem' : mastersystem(),
    'gamegear' : mastersystem(),
    'atarilynx' : atarilynx(),
    'neogeo' : neogeo(),
    'pcengine' : pcengine(),
    'supergrafx' : pcengine(),
    'nes' : nes(),
    'fds' : nes(),
    'snes' : snes(),
    'msx' : tms9918(),
    'x68000' : x68000(),
    'gb': gameboy(),
    'gbc' : gameboy(),
    'gba' :gameboy(),
    'ngp' : ngp(),
    'ngpc' : ngp(),
    'atari2600': atari2600(),
    'atari5200': atari5200(),
    'atari7800': atari7800(),
    'mame-libretro' : mame_libretro(),
    'n64' : n64(),
}

cmd = console.get(args.console)
try: 
    exec = subprocess.Popen(cmd)
    exec.wait()
except FileNotFoundError :
    print("Unable to execute, chvideo was not found. \n",cmd)