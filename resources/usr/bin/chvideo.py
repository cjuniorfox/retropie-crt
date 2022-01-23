#!/usr/bin/python3
import math, argparse, time,json
from subprocess import Popen, PIPE

class Specs:
    class Horizontal:
        def __init__(self,isPAL):
            if isPAL:
                self.front_porch = 0.025
                self.sync_pulse = 0.074
                self.back_porch = 0.088
            else:
                self.front_porch = 0.024
                self.sync_pulse = 0.074
                self.back_porch = 0.075 
            self.blanking_interval = self.front_porch + self.back_porch + self.sync_pulse
            self.image = 1.000 - self.blanking_interval
    class Vertical:
        def __init__(self,isPAL):
            if isPAL:
                self.scanlines = 312.5
                self.resolution = 288
                self.front_porch = 3
                self.sync_pulse = 3
            else:
                self.scanlines = 262.5
                self.resolution = 240
                self.front_porch = 3
                self.sync_pulse = 3
        def back_porch(self):
            return int(math.ceil(self.scanlines - self.resolution - self.front_porch - self.sync_pulse))
    def __init__(self,isPAL):
        self.vertical = Specs.Vertical(isPAL)
        self.horizontal = Specs.Horizontal(isPAL)
        

class VerticalClock:
    def __init__(self,vertical,beam):
        self.scanlines = beam / vertical.fps
        self.image = (self.scanlines * vertical.image)/vertical.scanlines
        self.front_porch = (self.scanlines * vertical.front_porch) / vertical.scanlines
        self.sync_pulse = (self.scanlines * vertical.sync_pulse) / vertical.scanlines
        self.back_porch = (self.scanlines * vertical.back_porch) / vertical.scanlines
        self.blanking_interval = self.front_porch + self.sync_pulse + self.back_porch

class Vertical:
    def __init__(self, specs, fps, overscan):
        self.scanlines = specs.vertical.scanlines
        self.image = specs.vertical.resolution - overscan.top - overscan.bottom
        self.front_porch = int(specs.vertical.front_porch + overscan.bottom)
        self.sync_pulse = int(specs.vertical.sync_pulse)
        self.back_porch = int(math.ceil(self.scanlines - self.image - self.front_porch - self.sync_pulse))
        self.blanking_interval = self.back_porch + self.front_porch + self.sync_pulse
        self.fps = fps
        self.frequency = self.fps * self.scanlines

class Overscan:
    def __init__(self,left,right,top,bottom):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

class Horizontal:
    def defineScanAndRep(self,image,horizontal_clock,overscan):
        max_scanline = 2048
        # Scan consists into image + back porch + front porch
        scanline = (image + overscan.left + overscan.right) * (horizontal_clock.scanline/ (horizontal_clock.image))
        self.rep = 1
        self.scanline = scanline
        #Multiply rep until scanline superates max_scanline
        while self.scanline < max_scanline:
            self.rep = int(self.rep * max(self.rep,2))
            self.scanline = int(scanline * self.rep)
        #Do one step below
        while self.scanline > max_scanline and (self.scanline / 2) > image:
            self.rep = int(self.rep / 2)
            self.scanline = int(scanline * self.rep)

    def __init__(self,image,horizontal_clock,overscan):
        self.defineScanAndRep(image,horizontal_clock,overscan)
        self.image = image * self.rep
        #Overscan right at the front porch
        self.front_porch = self.scanline * (horizontal_clock.front_porch / horizontal_clock.scanline)+(overscan.right * self.rep) 
        #Overscan left to the back porch
        self.back_porch = self.scanline * (horizontal_clock.back_porch / horizontal_clock.scanline)+ (overscan.left * self.rep)  
        self.sync_pulse = self.scanline * (horizontal_clock.sync_pulse / horizontal_clock.scanline)
        self.blanking_interval = self.front_porch + self.back_porch + self.sync_pulse


class HorizontalClock:
    def __init__(self, vertical, specs, beam):
        self.scanline = (beam / vertical.fps / vertical.scanlines) * 1000
        self.front_porch = self.scanline * specs.horizontal.front_porch
        self.sync_pulse = self.scanline * specs.horizontal.sync_pulse
        self.back_porch = self.scanline * specs.horizontal.back_porch
        self.blanking_interval = self.scanline * specs.horizontal.blanking_interval
        self.image = self.scanline * specs.horizontal.image

class Scan :
    def __init__(self,x_resolution, isPAL, interlaced, fps, overscan):
        beam = 1000
        y_factor = (2 if interlaced else 1)
        self.interlaced = int(interlaced)
        specs = Specs(isPAL)
        #NTSC
        #self.vertical = Vertical(262.5, 240, 3, 3, freq,overscan)
        self.vertical = Vertical(specs,fps,overscan)
        self.horizontal_clock = HorizontalClock(self.vertical,specs,beam)
        self.vertical_clock = VerticalClock(self.vertical,beam)
        self.horizontal = Horizontal(x_resolution,self.horizontal_clock,overscan)
        self.x_resolution = x_resolution
        self.y_resolution = self.vertical.image * y_factor
        self.pixel_clock = int(round(self.vertical.scanlines * self.horizontal.scanline * freq))
        


def image(x_resolution,pal,interlaced,freq,oLeft,oRight,oTop,oBottom):
    o = Overscan(oLeft,oRight,oTop,oBottom)
    timing = Scan(x_resolution, pal, interlaced, freq, o)
    return timing
    
def hdmi_timings(timing):
    #If rep equals one, so rep isn't not applyable
    rep = 0 if timing.horizontal.rep == 1 else timing.horizontal.rep 

    strTimmings = "hdmi_timings " + str(timing.horizontal.image) + " 1 " + \
        str(round(timing.horizontal.front_porch)) + " " + \
        str(round(timing.horizontal.sync_pulse)) + " " + \
        str(round(timing.horizontal.back_porch)) + " " + \
        str(timing.y_resolution) + " 1 " + \
        str(timing.vertical.front_porch) + " " +\
        str(timing.vertical.sync_pulse) + " " + \
        str(timing.vertical.back_porch) + " 0 0 " + \
        str(rep) + " " + \
        str(timing.vertical.fps) + " " + \
        str(1 if timing.interlaced else 0) + " " + \
        str(timing.pixel_clock) + " 1"
    return strTimmings

def outputjson(timming):
    json_data = json.dumps(timming,default=lambda o: o.__dict__, indent=4)
    return json_data

def verbosely(timing):
    print("Vertical:")
    print("Vert. Res.  :", timing.y_resolution)
    print(" Lines      :", timing.vertical.scanlines,timing.vertical_clock.scanlines,"(nS)")
    print(" Image      :", timing.y_resolution, timing.vertical_clock.image, "(nS)")
    print(" Sync Pulse :", timing.vertical.sync_pulse, timing.vertical_clock.sync_pulse, "(nS)")
    print(" Front Porch:", timing.vertical.front_porch, timing.vertical_clock.front_porch, "(nS)")
    print(" Back Porch :", timing.vertical.back_porch, timing.vertical_clock.back_porch, "(ns)")
    print(" Total blank:", timing.vertical.blanking_interval, timing.vertical_clock.blanking_interval, "(nS)")
    print("Horizontal:")
    print(" Horiz. Res.:", timing.x_resolution)
    print(" Scan       :", timing.horizontal.scanline, timing.horizontal_clock.scanline,"(uS)")
    print(" Image      :", timing.horizontal.image, timing.horizontal_clock.image,"(uS)")
    print(" Sync Pulse :", timing.horizontal.sync_pulse, timing.horizontal_clock.sync_pulse, "(uS)")
    print(" Front Porch:", timing.horizontal.front_porch, timing.horizontal_clock.front_porch, "(uS)")
    print(" Back Porch :", timing.horizontal.back_porch, timing.horizontal_clock.back_porch, "(us)")
    print(" Total blank:", timing.horizontal.blanking_interval, timing.horizontal_clock.blanking_interval, "(uS)")
    print(" Frequency  :", timing.vertical.fps, "Hz")
    print("Pixel Clock: ", timing.pixel_clock)

def fbset(timings):
    time.sleep(0.5)
    Popen(['fbset','-depth', '32', '-xres',str(timings.x_resolution), '-yres',str(timings.y_resolution)])

def apply(timings):
    vcgencmd = ['vcgencmd',hdmi_timings(timings)]
    exec=Popen(vcgencmd)
    exec.wait()
    exec=Popen(['tvservice','-e','DMT 87'])
    exec.wait()
    exec=Popen(['tvservice','-e','DMT 88'])
    exec.wait()
    fbset(timings)

def set_composite_mode(timings,isPAL,isProgressive):
    system = 'PAL' if isPAL else 'NTSC'
    progressive = 'P' if isProgressive else ''
    argument = '%s 4:3 %s' % (system, progressive)
    exec = Popen(['tvservice','-c',argument])
    exec.wait()
    fbset(timings)

def is_HDMI_connected():
    return 'HDMI' in str(Popen(['tvservice','-l'],stdout=PIPE).communicate()[0])

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
parser.add_argument("--json","-j",action='store_true',help="Print detailed data as JSON", default=False)
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
    args.overscan_bottom
)
if args.json :
    print(outputjson(timings))
elif args.verbose :
    verbosely(timings)

if args.info : 
    if not args.json:
        print(hdmi_timings(timings))
else :
    try:
        apply(timings) if is_HDMI_connected() else set_composite_mode(timings,args.pal, args.progressive)
    except FileNotFoundError :
        print("Unable to apply the settings because either vcgencmd or tvservice was not found. Are you running on Pi?")
        print("Assuming you're running only just for information, follows below. Try next time using -i --info.")
        print(hdmi_timings(timings))