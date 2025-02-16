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
IS_50HZ = args.pal
info = args.info
verbose = args.verbose

def getcmd(width=348,lines_60hz=240,lines_50hz=288,freq_60hz=59.975,freq_50hz=50.01,overscan_left=0,overscan_right=0) :
    global IS_50HZ, info, verbose
    freq = freq_50hz if IS_50HZ else freq_60hz
    cmd = [
        "chvideo",
        "-w",str(width),
        "-f", str(freq),
        "-L",str(overscan_left),
        "-R",str(overscan_right),
        "-l",str(lines_50hz if IS_50HZ else lines_60hz),
    ]
    if IS_50HZ :
        cmd.append("-P")
    if info :
        cmd.append("-i")
    if verbose :
        cmd.append("-v")
    if args.json :
        cmd.append("-j")

    return cmd

def emulationstation() :
    return getcmd(width=720,lines_60hz=448,lines_50hz=536,freq_60hz=60,freq_50hz=50,overscan_left=36,overscan_right=36)

def megadrive() :
    return getcmd(width=1392,freq_60hz=59.92)

def mastersystem() :
    return getcmd(width=284,freq_60hz=59.92)

def tms9918() :
    return getcmd(width=284,freq_60hz=59.92, lines_50hz=192, lines_60hz=192)

def neogeo() :
    return getcmd(width=340, lines_60hz=224, lines_50hz=224, freq_60hz=59.185)

def nes() :
    return getcmd(width=282,freq_60hz=60.1)

def snes() :
    return nes()

def pcengine() :
    return getcmd(width=282,freq_60hz=59.94)

def psx() :
    return getcmd(width=1280,freq_60hz=59.94,overscan_left=45,overscan_right=45)

def psx_hires() :
    return getcmd(width=1280,freq_60hz=59.94,lines_60hz=480,lines_50hz=576,overscan_left=45,overscan_right=45)

def mame_libretro() :
    return getcmd(width=1920,freq_60hz=59.94,overscan_left=25,overscan_right=25)

def atarilynx() :
    return getcmd(width=348,freq_60hz=59.94)

def gameboy() :
    return getcmd(width=240,freq_60hz=59.73,overscan_left=10,overscan_right=10)

def gameboyadvanced() :
    return gameboy()

def atari2600() :
    return getcmd(width=348,freq_60hz=59.92)

def atari800() :
    return getcmd(width=336,freq_60hz=59.922745,overscan_left=16,overscan_right=16)

def atari7800() :
    return getcmd(width=348,freq_60hz=59.92)

def ngp() :
    return getcmd(width=160,lines_50hz=224, lines_60hz=224, freq_60hz=60,overscan_left=8,overscan_right=8)

def n64() :
    return getcmd(width=640,freq_60hz=60,overscan_left=10,overscan_right=10)

def x68000() :
    return getcmd(width=1024,overscan_left=10,overscan_right=10,freq_60hz=59.94)

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