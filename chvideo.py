#!/usr/bin/python
import math, argparse, subprocess, time

class VerticalTiming:
    def __init__(self,verticalLines,beam):
        self.scan = beam / verticalLines.freq
        self.image = (self.scan * verticalLines.image)/verticalLines.scan
        self.frontPorch = (self.scan * verticalLines.frontPorch) / verticalLines.scan
        self.sync = (self.scan * verticalLines.sync) / verticalLines.scan
        self.backPorch = (self.scan * verticalLines.backPorch) / verticalLines.scan
        self.totalBlank = self.frontPorch + self.sync + self.backPorch

class VerticalLines:
    def __init__(self, scan, image, frontPorch, sync, freq, overscan):
        self.scan = scan
        self.image = image - overscan.top - overscan.bottom
        self.frontPorch = int(frontPorch + overscan.bottom)
        self.sync = int(sync)
        self.backPorch = int(math.ceil(self.scan - self.image - self.frontPorch - self.sync - overscan.bottom + overscan.top))
        self.totalBlank = self.backPorch + self.frontPorch + self.sync
        self.freq = freq
        self.lineFrequency = self.freq * self.scan

class Overscan:
    def __init__(self,left,right,top,bottom):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

class HorizontalPixels:
    def __init__(self,pixels,hTimming,overscan):
        pixelRep = 1280
        self.rep = int(math.ceil(pixelRep/pixels))
        oLeft = overscan.left * self.rep #Overscan left to the back porch
        oRight = overscan.right * self.rep #Overscan right to the front porch
        self.image = pixels * self.rep
        self.scan = (self.image + oLeft + oRight) * (hTimming.scan/ (hTimming.image))
        self.frontPorch = self.scan * (hTimming.frontPorch / hTimming.scan)+oRight
        self.backPorch = self.scan * (hTimming.backPorch / hTimming.scan)+oLeft
        self.sync = self.scan * (hTimming.sync / hTimming.scan)
        self.totalBlank = self.frontPorch + self.backPorch + self.sync


class HorizontalTimming:
    def __init__(self, v, factorfp, factorsp,factorbp,beam):
        self.scan = (beam / v.freq / v.scan) * 1000
        self.frontPorch = self.scan * factorfp
        self.sync = self.scan * factorsp
        self.backPorch = self.scan * factorbp
        self.totalBlank = self.frontPorch + self.backPorch + self.sync
        self.image = self.scan - self.totalBlank

class Scan :
    def __init__(self,hPixels, pal, interlaced, freq, overscan):
        beam = 1000;
        lineFactor = (2 if interlaced else 1)
        self.interlaced = int(interlaced)
        #NTSC
        self.vLines = VerticalLines(262.5, 240, 3, 3, freq,overscan)
        self.hTimming = HorizontalTimming(self.vLines,0.024,0.074,0.074,beam)
        if pal :
            self.vLines = VerticalLines(312.5, 288, 3, 3, freq,overscan)
            self.hTimming = HorizontalTimming(self.vLines,0.025,0.074,0.088,beam)
        self.vTimming = VerticalTiming(self.vLines,beam)
        self.hPixels = HorizontalPixels(hPixels,self.hTimming,overscan)
        self.vertPixels = self.vLines.image * lineFactor
        self.pixelClock = int(round(self.vLines.scan * self.hPixels.scan * freq))
        


def image(width,pal,interlaced,freq,oLeft,oRight,oTop,oBottom,verbose):
    o = Overscan(oLeft,oRight,oTop,oBottom);
    system = Scan(width, pal, interlaced, freq, o)

    if verbose:
        verbosely(system)
    
    strTimmings = str(system.hPixels.image) + " 1 " + \
        str(round(system.hPixels.frontPorch)) + " " + \
        str(round(system.hPixels.sync)) + " " + \
        str(round(system.hPixels.backPorch)) + " " + \
        str(system.vertPixels) + " 1 " + \
        str(system.vLines.frontPorch) + " " +\
        str(system.vLines.sync) + " " + \
        str(system.vLines.backPorch) + " 0 0 " + \
        str(system.hPixels.rep) + " " + \
        str(system.vLines.freq) + " " + \
        str(1 if system.interlaced else 0) + " " + \
        str(system.pixelClock) + " 1"
    
    return ("hdmi_timings " + strTimmings)

def verbosely(system):
    print("Vertical:")
    print(" Lines      :", system.vLines.scan,system.vTimming.scan,"(nS)")
    print(" Image      :", system.vertPixels, system.vTimming.image, "(nS)")
    print(" Sync Pulse :", system.vLines.sync, system.vTimming.sync, "(nS)")
    print(" Front Porch:", system.vLines.frontPorch, system.vTimming.frontPorch, "(nS)")
    print(" Back Porch :", system.vLines.backPorch, system.vTimming.backPorch, "(ns)")
    print(" Total blank:", system.vLines.totalBlank, system.vTimming.totalBlank, "(nS)")
    print("Horizontal:")
    print(" Scan       :", system.hPixels.scan, system.hTimming.scan,"(uS)")
    print(" Image      :", system.hPixels.image, system.hTimming.image,"(uS)")
    print(" Sync Pulse :", system.hPixels.sync, system.hTimming.sync, "(uS)")
    print(" Front Porch:", system.hPixels.frontPorch, system.hTimming.frontPorch, "(uS)")
    print(" Back Porch :", system.hPixels.backPorch, system.hTimming.backPorch, "(us)")
    print(" Total blank:", system.hPixels.totalBlank, system.hTimming.totalBlank, "(uS)")
    print(" Frequency  :", system.vLines.freq, "Hz")
    print("Pixel Clock: ", system.pixelClock);

def apply(hdmi_timings):
    vcgencmd = ['vcgencmd',hdmi_timings]
    exec=subprocess.Popen(vcgencmd)
    exec.wait()
    time.sleep(1)
    exec=subprocess.Popen(["tvservice","-e","DMT 87"])
    exec.wait()
    time.sleep(1)
    exec.subprocess.Open(["tvservice","-e","DMT 88"])

parser = argparse.ArgumentParser(description="Switch the HDMI output resolution for SDTV friendly modes")
parser.add_argument("--width","-w", metavar = '720',type=int, help = "Width resolution value",default=720)
parser.add_argument("--frequency","-f", metavar= '59.97',type=float, help = "Refresh rate",default=0)
parser.add_argument("--progressive","-p",action=argparse.BooleanOptionalAction, help="Progressive 240p/288p",default=False)
parser.add_argument("--pal","-P",action=argparse.BooleanOptionalAction, help="PAL format", default=False)
parser.add_argument("--overscan-left","-L",metavar="0",type=int,help="Overscan left",default=0)
parser.add_argument("--overscan-right","-R",metavar="0",type=int,help="Overscan right",default=0)
parser.add_argument("--overscan-top","-T",metavar="0",type=int,help="Overscan top",default=0)
parser.add_argument("--overscan-bottom","-B",metavar="0",type=int,help="Overscan bottom",default=0)
parser.add_argument("--verbose","-v",action=argparse.BooleanOptionalAction,help="Print defailed data", default=False)
parser.add_argument("--info","-i",action=argparse.BooleanOptionalAction,help="Only print without applyng any change",default=False)
args = parser.parse_args()
freq = float(args.frequency)
if freq == 0:
    freq = 59.97 if not args.pal else 50

hdmi_timings = image(args.width, 
    args.pal, 
    not args.progressive,
    freq,
    args.overscan_left, 
    args.overscan_right, 
    args.overscan_top, 
    args.overscan_bottom,
    args.verbose
)
if args.info : 
    print(hdmi_timings)
else :
    apply(hdmi_timings)