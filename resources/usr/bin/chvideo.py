#!/usr/bin/python3
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
        self.backPorch = int(math.ceil(self.scan - self.image - self.frontPorch - self.sync))
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
    def __init__(self,width,hTimming,overscan):
        pixelRep = 1920
        rep = int(math.ceil(pixelRep/width))
        self.rep = rep+(rep%2)
        oLeft = max(overscan.left * self.rep,overscan.left) #Overscan left to the back porch
        oRight = max(overscan.right * self.rep,overscan.right) #Overscan right to the front porch
        self.image = max(width * self.rep, width)
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
    def __init__(self,horizPixels, pal, interlaced, freq, overscan):
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
        self.hPixels = HorizontalPixels(horizPixels,self.hTimming,overscan)
        self.horizPixels = horizPixels
        self.vertPixels = self.vLines.image * lineFactor
        self.pixelClock = int(round(self.vLines.scan * self.hPixels.scan * freq))
        


def image(horizPixels,pal,interlaced,freq,oLeft,oRight,oTop,oBottom,verbose):
    o = Overscan(oLeft,oRight,oTop,oBottom);
    timing = Scan(horizPixels, pal, interlaced, freq, o)

    if verbose:
        verbosely(timing)
    
    return timing;
    
def hdmi_timings(timing):
    strTimmings = "hdmi_timings " + str(timing.hPixels.image) + " 1 " + \
        str(round(timing.hPixels.frontPorch)) + " " + \
        str(round(timing.hPixels.sync)) + " " + \
        str(round(timing.hPixels.backPorch)) + " " + \
        str(timing.vertPixels) + " 1 " + \
        str(timing.vLines.frontPorch) + " " +\
        str(timing.vLines.sync) + " " + \
        str(timing.vLines.backPorch) + " 0 0 " + \
        str(timing.hPixels.rep) + " " + \
        str(timing.vLines.freq) + " " + \
        str(1 if timing.interlaced else 0) + " " + \
        str(timing.pixelClock) + " 1"
    return strTimmings;

def verbosely(timing):
    print("Vertical:")
    print("Vert. Res.  :", timing.vertPixels)
    print(" Lines      :", timing.vLines.scan,timing.vTimming.scan,"(nS)")
    print(" Image      :", timing.vertPixels, timing.vTimming.image, "(nS)")
    print(" Sync Pulse :", timing.vLines.sync, timing.vTimming.sync, "(nS)")
    print(" Front Porch:", timing.vLines.frontPorch, timing.vTimming.frontPorch, "(nS)")
    print(" Back Porch :", timing.vLines.backPorch, timing.vTimming.backPorch, "(ns)")
    print(" Total blank:", timing.vLines.totalBlank, timing.vTimming.totalBlank, "(nS)")
    print("Horizontal:")
    print(" Horiz. Res.:", timing.horizPixels)
    print(" Scan       :", timing.hPixels.scan, timing.hTimming.scan,"(uS)")
    print(" Image      :", timing.hPixels.image, timing.hTimming.image,"(uS)")
    print(" Sync Pulse :", timing.hPixels.sync, timing.hTimming.sync, "(uS)")
    print(" Front Porch:", timing.hPixels.frontPorch, timing.hTimming.frontPorch, "(uS)")
    print(" Back Porch :", timing.hPixels.backPorch, timing.hTimming.backPorch, "(us)")
    print(" Total blank:", timing.hPixels.totalBlank, timing.hTimming.totalBlank, "(uS)")
    print(" Frequency  :", timing.vLines.freq, "Hz")
    print("Pixel Clock: ", timing.pixelClock)

def apply(timings):
    print(timings.vertPixels)
    vcgencmd = ['vcgencmd',hdmi_timings(timings)]
    exec=subprocess.Popen(vcgencmd)
    exec.wait()
    exec=subprocess.Popen(["tvservice","-e","DMT 87"])
    exec.wait()
    exec=subprocess.Popen(["tvservice","-e","DMT 88"])
    exec.wait()
    time.sleep(0.5)
    subprocess.Popen(["fbset","-depth", "32", "-xres",str(timings.horizPixels), "-yres",str(timings.vertPixels)])

parser = argparse.ArgumentParser(description="Switch the HDMI output resolution for SDTV friendly modes")
parser.add_argument("--width","-w", metavar = '720',type=int, help = "Width resolution value",default=720)
parser.add_argument("--frequency","-f", metavar= '59.97',type=float, help = "Refresh rate",default=0)
parser.add_argument("--progressive","-p",action='store_true', help="Progressive 240p/288p",default=False)
parser.add_argument("--pal","-P",action='store_true', help="PAL format", default=False)
parser.add_argument("--overscan-left","-L",metavar="0",type=int,help="Overscan left",default=0)
parser.add_argument("--overscan-right","-R",metavar="0",type=int,help="Overscan right",default=0)
parser.add_argument("--overscan-top","-T",metavar="0",type=int,help="Overscan top",default=0)
parser.add_argument("--overscan-bottom","-B",metavar="0",type=int,help="Overscan bottom",default=0)
parser.add_argument("--verbose","-v",action='store_true',help="Print defailed data", default=False)
parser.add_argument("--info","-i",action='store_true',help="Only print without applyng any change",default=False)
args = parser.parse_args()
freq = float(args.frequency)
if freq == 0:
    freq = 59.97 if not args.pal else 50

timings = image(args.width, 
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
    print(hdmi_timings(timings))
else :
    try:
        apply(timings)
    except FileNotFoundError :
        print("Unable to apply the settings because either vcgencmd or tvservice was not found. Are you running on Pi?")
        print("Assuming you're running only just for information, follows below. Try next time using -i --info.")
        print(hdmi_timings(timings))