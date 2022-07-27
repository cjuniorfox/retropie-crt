#!/usr/bin/python3

import argparse
import subprocess

parser = argparse.ArgumentParser(description="Apply settings for desired game console")
parser.add_argument("console",help="Desired game consol")
parser.add_argument("--pal","-P",action='store_true',help="Apply 625 50Hz aka PAL settings")
parser.add_argument("--info","-i",action='store_true',help="Only print without applyng any change")
parser.add_argument("--verbose","-v",action='store_true',help="Detailed information")
parser.add_argument("--json","-j",action='store_true',help="Output detailed data as JSON")
args = parser.parse_args()
isPal = args.pal
info = args.info
verbose = args.verbose

def getcmd(width=348,ntsc_freq=59.975,pal_freq=50.01,oTop=0,oBottom=0,oLeft=0,oRight=0,isProgressive=True) :
    global isPal, info, verbose
    freq = pal_freq if isPal else ntsc_freq
    cmd = ["chvideo","-w",str(width), "-f", str(freq), "-L",str(oLeft),"-R",str(oRight),"-T",str(oTop),"-B",str(oBottom)]
    if isProgressive :
        cmd.append("-p")
    if isPal :
        cmd.append("-P")
    if info :
        cmd.append("-i")
    if verbose :
        cmd.append("-v")
    if args.json :
        cmd.append("-j")

    return cmd

def emulationstation() :
    return getcmd(width=720,ntsc_freq=60,pal_freq=50,oTop=8,oBottom=8,oLeft=32,oRight=32,isProgressive=False)

def megadrive() :
    return getcmd(width=1392,ntsc_freq=59.92)

def mastersystem() :
    return getcmd(width=284,ntsc_freq=59.92)

def tms9918() :
    return getcmd(width=284,ntsc_freq=59.92,oTop=24,oBottom=24)

def neogeo() :
    return getcmd(width=340,ntsc_freq=59.185)

def nes() :
    return getcmd(width=282,ntsc_freq=60.1)

def snes() :
    return nes()

def pcengine() :
    return getcmd(width=282,ntsc_freq=59.94)

def psx() :
    return getcmd(width=1280,ntsc_freq=59.94,oLeft=45,oRight=45)

def psx_hires() :
    return getcmd(width=1280,ntsc_freq=59.94,oLeft=45,oRight=45,isProgressive=False)

def mame_libretro() :
    return getcmd(width=1920,ntsc_freq=59.94,oLeft=25,oRight=25)

def atarilynx() :
    return getcmd(width=348,ntsc_freq=59.94)

def gameboy() :
    return getcmd(width=240,ntsc_freq=59.73,oLeft=10,oRight=10)

def gameboyadvanced() :
    return gameboy()

def atari2600() :
    return getcmd(width=348,ntsc_freq=59.92,oTop=-9,oBottom=-1)

def atari800() :
    return getcmd(width=336,ntsc_freq=59.922745,oLeft=16,oRight=16)

def atari7800() :
    return getcmd(width=348,ntsc_freq=59.92)

def ngp() :
    return getcmd(width=160,ntsc_freq=60,oLeft=8,oRight=8,oTop=8,oBottom=8)

def n64() :
    return getcmd(width=640,ntsc_freq=60,oLeft=10,oRight=10)

def x68000() :
    return getcmd(width=1024,oLeft=10,oRight=10,ntsc_freq=59.94)

console={
    'emulationstation' : emulationstation(),
    'arcade':mame_libretro(),
    'fba':mame_libretro(),
    'megadrive':megadrive(),
    'genesis': megadrive(),
    'sega32x': megadrive(),
    'segacd' : megadrive(),
    'mastersystem' : mastersystem(),
    'gamegear' : mastersystem(),
    'sg-1000' : mastersystem(),
    'atarilynx' : atarilynx(),
    'neogeo' : neogeo(),
    'pcengine' : pcengine(),
    'psx' : psx(),
    'psx_hires' : psx_hires(),
    'supergrafx' : pcengine(),
    'nes' : nes(),
    'fds' : nes(),
    'snes' : snes(),
    'msx' : tms9918(),
    'x68000' : x68000(),
    'gb': gameboy(),
    'gbc' : gameboy(),
    'gba' :gameboyadvanced(),
    'ngp' : ngp(),
    'ngpc' : ngp(),
    'atari2600': atari2600(),
    'atari800': atari800(),
    'atari5200': atari800(),
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
except TypeError:
    print("The settings for platform \"{}\" was not found.".format(args.console))