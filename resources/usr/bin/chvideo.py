#!/usr/bin/python3
import argparse, time,json
from subprocess import Popen, PIPE, DEVNULL

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
        def __init__(self,isPAL, interlace):
            if isPAL:
                self.scanlines = 312.5 if interlace else 312
                self.resolution = 288
                self.back_porch = 18
            else:
                self.scanlines = 262.5 if interlace else 262
                self.resolution = 244
                self.back_porch = 12
            self.front_porch = 3
            self.sync_pulse = self.scanlines - self.resolution - self.back_porch - self.front_porch

    def __init__(self,isPAL, interlace):
        self.vertical = Specs.Vertical(isPAL, interlace)
        self.horizontal = Specs.Horizontal(isPAL)
        

class VerticalClock:
    def __init__(self,vertical,beam):
        self.scanlines = beam / vertical.frequency
        self.image = (self.scanlines * vertical.image)/vertical.scanlines
        self.front_porch = (self.scanlines * vertical.front_porch) / vertical.scanlines
        self.sync_pulse = (self.scanlines * vertical.sync_pulse) / vertical.scanlines
        self.back_porch = (self.scanlines * vertical.back_porch) / vertical.scanlines
        self.blanking_interval = self.front_porch + self.sync_pulse + self.back_porch

class Vertical:
    def __init__(self, frequency, overscan, isPAL, interlace):
        specs = Specs(isPAL,interlace)
        self.scanlines = specs.vertical.scanlines
        self.image = specs.vertical.resolution - overscan.top - overscan.bottom
        self.front_porch = specs.vertical.front_porch + overscan.bottom
        self.sync_pulse = specs.vertical.sync_pulse
        self.back_porch = specs.vertical.back_porch + overscan.top
        self.blanking_interval = self.back_porch + self.front_porch + self.sync_pulse
        self.frequency = frequency
        self.fps = frequency if not interlace else frequency / 2

class Overscan:
    def __init__(self,left,right,top,bottom):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

class Horizontal:
    def defineScanAndRep(self,image,horizontal_clock,overscan):
        max_scanline = 2304
        # Scan consists into image + back porch + front porch
        scanline = (image + overscan.left + overscan.right) * (horizontal_clock.scanline / (horizontal_clock.image))
        self.rep = 1
        self.scanline = scanline
        #Multiply rep until scanline overrates max_scanline
        while self.scanline < max_scanline:
            self.rep = int(self.rep * max(self.rep,2))
            self.scanline = int(scanline * self.rep)
        #Do one step back
        while self.scanline > max_scanline and (self.scanline / 2) > image:
            self.rep = int(self.rep / 2)
            self.scanline = int(scanline * self.rep)

    def __init__(self,image,horizontal_clock,overscan):
        self.defineScanAndRep(image,horizontal_clock,overscan)
        self.image = image * self.rep
        #Overscan right at the front porch
        self.front_porch = round(self.scanline * (horizontal_clock.front_porch / horizontal_clock.scanline) + (overscan.right * self.rep))
        self.sync_pulse = round(self.scanline * (horizontal_clock.sync_pulse / horizontal_clock.scanline)) 
        #Overscan left to the back porch
        #self.back_porch = round(self.scanline * (horizontal_clock.back_porch / horizontal_clock.scanline) + (overscan.left * self.rep))
        self.back_porch = self.scanline - self.image - self.front_porch - self.sync_pulse
        self.blanking_interval = self.front_porch + self.back_porch + self.sync_pulse


class HorizontalClock:
    def __init__(self, vertical, specs, beam):
        self.scanline = (beam / vertical.frequency / vertical.scanlines) * 1000
        self.front_porch = self.scanline * specs.horizontal.front_porch
        self.sync_pulse = self.scanline * specs.horizontal.sync_pulse
        self.back_porch = self.scanline * specs.horizontal.back_porch
        self.blanking_interval = self.scanline * specs.horizontal.blanking_interval
        self.image = self.scanline * specs.horizontal.image

class Scan :
    def __init__(self,x_resolution, isPAL, interlaced, frequency, overscan):
        beam = 1000
        frame_fields = (2 if interlaced else 1)
        self.interlaced = int(interlaced)
        specs = Specs(isPAL, interlaced)
        self.vertical = Vertical(frequency,overscan, isPAL, interlaced)
        self.horizontal_clock = HorizontalClock(self.vertical,specs,beam)
        self.vertical_clock = VerticalClock(self.vertical,beam)
        self.horizontal = Horizontal(x_resolution,self.horizontal_clock,overscan)
        self.x_resolution = x_resolution
        self.y_resolution = self.vertical.image * frame_fields
        self.fps = self.vertical.fps
        self.pixel_clock = self.vertical.scanlines * self.horizontal.scanline * frequency
        


def calc_overscan(left, right, top, bottom, lines, isPal, interlace) :
    specs = Specs(isPal,interlace)
    resolution = specs.vertical.resolution if not interlace else specs.vertical.resolution * 2
    return Overscan(
        left,
        right,
        top if lines == 0 else round((resolution - lines) / 2),
        bottom if lines == 0 else round((resolution - lines) / 2)
    )

def calc_timings(x_resolution,pal,interlaced,freq,overscan):
    if interlaced : #If interlaced, divide the vertical resolution
        overscan.top = round(overscan.top/2)
        overscan.bottom = round(overscan.bottom/2)
    timing = Scan(x_resolution, pal, interlaced, freq, overscan)
    return timing
    
def hdmi_timings(timing):
    #If rep equals one, so rep isn't not applyable
    rep = 0 if timing.horizontal.rep == 1 else timing.horizontal.rep

    return 'hdmi_timings {} 1 {} {} {} {} 1 {} {:.0f} {} 0 0 {} {} {} {:.0f} 1'.format(
        timing.horizontal.image,
        timing.horizontal.front_porch,
        timing.horizontal.sync_pulse,
        timing.horizontal.back_porch,
        timing.y_resolution,
        timing.vertical.front_porch,
        timing.vertical.sync_pulse,
        timing.vertical.back_porch,
        rep,
        timing.vertical.frequency,
        1 if timing.interlaced else 0,
        timing.pixel_clock)

def outputjson(timing):
    json_data = json.dumps(timing,default=lambda o: o.__dict__, indent=4)
    return json_data

def modeline(timing):
    fps = timing.fps
    clk = timing.pixel_clock/1000000
    hzn = timing.horizontal.image             #horizontal res
    hfp = hzn + timing.horizontal.front_porch #horizonal front porch
    hsp = hfp + timing.horizontal.sync_pulse  #horizontal sync pulse
    hbp = hsp + timing.horizontal.back_porch  #horizontal back porch
    vrc = timing.y_resolution                 #vertical res
    vfp = vrc + timing.vertical.front_porch   #vertical front porch
    vsp = vfp + timing.vertical.sync_pulse    #vertical sync pulse
    vbp = vsp + timing.vertical.back_porch    #vertical back porch
    if timing.interlaced :
        vfp = vrc + timing.vertical.front_porch * 2
        vsp = vfp + timing.vertical.sync_pulse * 2
        vbp = vsp + timing.vertical.back_porch * 2

    itl = "Interlace" if timing.interlaced else ""

    return " ".join(['"{}x{}_{:.0f}" {:.6f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f}'
                     .format(hzn,vrc,fps, clk, hzn, hfp, hsp, hbp,vrc,vfp,vsp,vbp),itl])

def xrandr_scale(timing):
    vertical = 1 if timing.interlaced and timing.x_resolution >= 512 else 2
    horizontal = 1 if timing.horizontal.rep == 1 else 1 / timing.horizontal.rep
    return str(horizontal)+"x"+str(vertical)

def verbosely(timing,pal, interlace):
    templ_vert = '\t{:<12}: {:>8} lines - {:>6.2f} (nS)'
    templ_horz = '\t{:<12}: {:>8} px - {:>6.2f} (uS)'
    templ_freq = '\t{:<12}: {:>8.0f} Hz'
    print("\nLines per field.", "Interlaced mode. Two fields per frame:" if interlace else ":")
    print(templ_vert.format("Scanlines",timing.vertical.scanlines,timing.vertical_clock.scanlines))
    print(templ_vert.format("Image",timing.vertical.image,timing.vertical_clock.image))
    print(templ_vert.format("Front Porch",timing.vertical.front_porch,timing.vertical_clock.front_porch))
    print(templ_vert.format("Sync Pulse",timing.vertical.sync_pulse,timing.vertical_clock.sync_pulse))
    print(templ_vert.format("Back Porch",timing.vertical.back_porch,timing.vertical_clock.back_porch))
    print(templ_vert.format("Blanking",timing.vertical.blanking_interval,timing.vertical_clock.blanking_interval))
    print(templ_freq.format("Frequency",timing.vertical.frequency))
    print("\nHorizontal")
    print(templ_horz.format("Scanline",timing.horizontal.scanline,timing.horizontal_clock.scanline))
    print(templ_horz.format("Image",timing.horizontal.image,timing.horizontal_clock.image))
    print(templ_horz.format("Front Porch",timing.horizontal.front_porch,timing.horizontal_clock.front_porch))
    print(templ_horz.format("Sync Pulse",timing.horizontal.sync_pulse,timing.horizontal_clock.sync_pulse))
    print(templ_horz.format("Back Porch",timing.horizontal.back_porch,timing.horizontal_clock.back_porch))
    print(templ_horz.format("Total blank",timing.horizontal.blanking_interval,timing.horizontal_clock.blanking_interval))
    print(templ_freq.format("Frequency",timing.vertical.scanlines * timing.vertical.frequency))
    print(templ_freq.format("Pixel Clock",timing.pixel_clock))
    print("\nBroadcast    :","System-M (NTSC/PAL-M)" if not pal else "System-B/D/G/H/I/K/N (PAL-EU/SECAM)")
    print('Resolution   : {}x{}'.format(timing.x_resolution,timing.y_resolution))
    print('Frames       : {:.2f}'.format(timing.fps))
    print("")

def fbset(timings):
    time.sleep(0.5)
    Popen(['fbset','-depth', '32', '-xres',str(timings.x_resolution), '-yres',str(timings.y_resolution)])

def apply_vcgencmd(timings):
    vcgencmd = ['vcgencmd',hdmi_timings(timings)]
    exec=Popen(vcgencmd)
    exec.wait()
    exec=Popen(['tvservice','-e','DMT 87'])
    exec.wait()
    exec=Popen(['tvservice','-e','DMT 88'])
    exec.wait()
    fbset(timings)

def apply_xrandr(timings, output, options):
    modeln = modeline(timings)
    modename = modeln.split(" ",1)[0]
    try :
        exec=Popen(['xrandr','--delmode',output,modename],stdout=PIPE, stderr=DEVNULL)
        exec.wait()
        exec=Popen(['xrandr','--rmmode',modename],stdout=PIPE, stderr=DEVNULL)
        exec.wait()
    finally :
        exec=Popen(['xrandr','--newmode']+modeln.split(" "))
        exec.wait()
        exec=Popen(['xrandr','--addmode',output,modename])
        exec.wait()
        exec=Popen(['xrandr','--output',output,'--mode',modename,'--scale',xrandr_scale(timings)] + options.split(" "))

def set_composite_mode(timings,isPAL,isProgressive):
    system = 'PAL' if isPAL else 'NTSC'
    progressive = 'P' if isProgressive else ''
    argument = '%s 4:3 %s' % (system, progressive)
    exec = Popen(['tvservice','-c',argument])
    exec.wait()
    fbset(timings)

def is_HDMI_connected():
    return 'HDMI' in str(Popen(['tvservice','-l'],stdout=PIPE).communicate()[0])

def set_interlace_by_resolution(lines,pal) :
    specs = Specs(pal,True)
    if lines > (specs.vertical.resolution + specs.vertical.back_porch) * 2:
        raise( ValueError('Unable to set vertical resolution above {} lines'.format(lines)))
    return args.lines > specs.vertical.resolution + specs.vertical.back_porch #Check for specs assuming interlaced as default

parser = argparse.ArgumentParser(description="Switch the HDMI output resolution for SDTV friendly modes")
parser.add_argument("--width","-w", metavar = '720',type=int, help = "Width resolution value",default=720)
parser.add_argument("--lines", "-l", metavar = '480', type=int, help = "Height resolution value. (supress the -p value)", default=0)
parser.add_argument("--frequency","-f", metavar= '60',type=float, help = "Refresh rate",default=0)
parser.add_argument("--progressive","-p",action='store_true', help="Progressive 240p/288p. (supressed if --height is defined)",default=False)
parser.add_argument("--pal","-P",action='store_true', help="625 lines 50hz PAL-EU/SECAM like", default=False)
parser.add_argument("--overscan-left","-L",metavar="0",type=int,help="Overscan left",default=0)
parser.add_argument("--overscan-right","-R",metavar="0",type=int,help="Overscan right",default=0)
parser.add_argument("--overscan-top","-T",type=int,help="Overscan top",default=0)
parser.add_argument("--overscan-bottom","-B",type=int,help="Overscan bottom",default=0)
parser.add_argument("--verbose","-v",action='store_true',help="Print defailed data", default=False)
parser.add_argument("--json","-j",action='store_true',help="Print detailed data as JSON", default=False)
parser.add_argument("--info","-i",action='store_true',help="Only print without applyng any change",default=False)
parser.add_argument("--x11-modeline","-m",action='store_true',help='Output X.org like modeline')
parser.add_argument("--output","-o",type=str,help="Output device (only required for xrandr)",default=False)
parser.add_argument("--x11-options","-t",type=str,help="Output options for xrandr",default=False)
args = parser.parse_args()
freq = float(args.frequency)
if freq == 0:
    freq = 60 if not args.pal else 50


interlace = not args.progressive
#If lines value its defined, supress the definition of -p parameter and automatically defines if its progressive or not and calculate the overscan
if args.lines > 0 : 
    interlace = set_interlace_by_resolution(args.lines, args.pal)

overscan = calc_overscan(args.overscan_left, args.overscan_right, args.overscan_top, args.overscan_bottom, args.lines, args.pal, interlace)

timings = calc_timings(args.width, 
    args.pal, 
    interlace,
    freq,
    overscan
)
if args.json :
    print(outputjson(timings))
elif args.verbose :
    verbosely(timings, args.pal, interlace)



if args.info : 
    if args.x11_modeline :
        print(modeline(timings))
    elif not args.json:
        print(hdmi_timings(timings))
else :
    try:
        if args.x11_modeline :
            if args.output == "":
                print("For x11-modeline switchmode, --output parameter its needed.")
            else :
                apply_xrandr(timings, args.output, args.x11_options)
        else :
            apply_vcgencmd(timings) if is_HDMI_connected() else set_composite_mode(timings,args.pal, args.progressive)
    except FileNotFoundError :
        print("Unable to apply the settings because either vcgencmd or tvservice was not found. Are you running on Pi?")
        print("Assuming you're running only just for information, follows below. Try next time using -i --info.")
        if args.x11_modeline :
            print(modeline(timings))
        else :
            print(hdmi_timings(timings))