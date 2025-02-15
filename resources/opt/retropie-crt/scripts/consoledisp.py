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

def getcmd(width=348,ntsc_freq=59.975,pal_freq=50.01,overscan_top=0,overscan_bottom=0,overscan_left=0,overscan_right=0,is_progressive=True) :
    global isPal, info, verbose
    freq = pal_freq if isPal else ntsc_freq
    cmd = [
        "chvideo",
        "-w",str(width),
        "-f", str(freq),
        "-L",str(overscan_left),
        "-R",str(overscan_right),
        "-T",str(overscan_top),
        "-B",str(overscan_bottom)
    ]
    if is_progressive :
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
    return getcmd(width=720,ntsc_freq=60,pal_freq=50,overscan_top=30,overscan_bottom=30,overscan_left=36,overscan_right=36,is_progressive=False)

def megadrive() :
    return getcmd(width=1392,ntsc_freq=59.92)

def mastersystem() :
    return getcmd(width=284,ntsc_freq=59.92)

def tms9918() :
    return getcmd(width=284,ntsc_freq=59.92,overscan_top=24,overscan_bottom=24)

def neogeo() :
    return getcmd(width=340,ntsc_freq=59.185)

def nes() :
    return getcmd(width=282,ntsc_freq=60.1)

def snes() :
    return nes()

def pcengine() :
    return getcmd(width=282,ntsc_freq=59.94)

def psx() :
    return getcmd(width=1280,ntsc_freq=59.94,overscan_left=45,overscan_right=45)

def psx_hires() :
    return getcmd(width=1280,ntsc_freq=59.94,overscan_left=45,overscan_right=45,is_progressive=False)

def mame_libretro() :
    return getcmd(width=1920,ntsc_freq=59.94,overscan_left=25,overscan_right=25)

def atarilynx() :
    return getcmd(width=348,ntsc_freq=59.94)

def gameboy() :
    return getcmd(width=240,ntsc_freq=59.73,overscan_left=10,overscan_right=10)

def gameboyadvanced() :
    return gameboy()

def atari2600() :
    return getcmd(width=348,ntsc_freq=59.92,overscan_top=-9,overscan_bottom=-1)

def atari800() :
    return getcmd(width=336,ntsc_freq=59.922745,overscan_left=16,overscan_right=16)

def atari7800() :
    return getcmd(width=348,ntsc_freq=59.92)

def ngp() :
    return getcmd(width=160,ntsc_freq=60,overscan_left=8,overscan_right=8,overscan_top=8,overscan_bottom=8)

def n64() :
    return getcmd(width=640,ntsc_freq=60,overscan_left=10,overscan_right=10)

def x68000() :
    return getcmd(width=1024,overscan_left=10,overscan_right=10,ntsc_freq=59.94)

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