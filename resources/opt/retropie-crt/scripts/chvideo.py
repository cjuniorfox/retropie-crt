#!/usr/bin/python3
import os, argparse, time, json
from subprocess import Popen, PIPE, DEVNULL

class Specs:
    class Horizontal:
        def __init__(self,is_50hz):
            if is_50hz:
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
        def __init__(self,is_50hz, interlaced):
            if is_50hz:
                self.scanlines = 312.5 if interlaced else 312
                self.lines = 288
                self.back_porch = 18
            else:
                self.scanlines = 262.5 if interlaced else 262
                self.lines = 244
                self.back_porch = 12
            self.resolution = self.lines * 2 if interlaced else self.lines
            self.front_porch = 3
            self.sync_pulse = self.scanlines - self.lines - self.back_porch - self.front_porch

    def __init__(self,is_50hz, interlaced):
        self.vertical = Specs.Vertical(is_50hz, interlaced)
        self.horizontal = Specs.Horizontal(is_50hz)
        

class VerticalClock:
    def __init__(self,vertical,beam):
        self.scanlines = beam / vertical.frequency
        self.image = (self.scanlines * vertical.image)/vertical.scanlines
        self.front_porch = (self.scanlines * vertical.front_porch) / vertical.scanlines
        self.sync_pulse = (self.scanlines * vertical.sync_pulse) / vertical.scanlines
        self.back_porch = (self.scanlines * vertical.back_porch) / vertical.scanlines
        self.blanking_interval = self.front_porch + self.sync_pulse + self.back_porch

class Vertical:
    def __init__(self, frequency, is_50hz, interlaced):
        specs = Specs(is_50hz,interlaced)
        self.scanlines = specs.vertical.scanlines
        self.image = specs.vertical.lines
        self.front_porch = specs.vertical.front_porch
        self.sync_pulse = specs.vertical.sync_pulse
        self.back_porch = specs.vertical.back_porch
        self.blanking_interval = self.back_porch + self.front_porch + self.sync_pulse
        self.frequency = frequency
        self.fps = frequency if not interlaced else frequency / 2

class Overscan:
    def __init__(self,left,right,top,bottom):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

class Horizontal:
    def define_scan_and_rep(self,image,horizontal_clock,overscan,multiply_rep = True):
        max_scanline = 2304
        # Scan consists into image + back porch + front porch
        scanline = (image + overscan.left + overscan.right) * (horizontal_clock.scanline / (horizontal_clock.image))
        self.rep = 1
        self.scanline = scanline
        #Multiply rep until scanline overrates max_scanline
        if multiply_rep:
            while self.scanline < max_scanline:
                self.rep = int(self.rep * max(self.rep,2))
                self.scanline = int(scanline * self.rep)
            #Do one step back
            while self.scanline > max_scanline and (self.scanline / 2) > image:
                self.rep = int(self.rep / 2)
                self.scanline = int(scanline * self.rep)

    def __init__(self,image,horizontal_clock,overscan,rep):
        self.define_scan_and_rep(image,horizontal_clock,overscan,rep)
        self.image = image * self.rep
        #Overscan right at the front porch
        self.front_porch = round(self.scanline * (horizontal_clock.front_porch / horizontal_clock.scanline))
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
    def __init__(self,x_resolution, is_50hz, interlaced, frequency, overscan,rep):
        beam = 1000
        frame_fields = (2 if interlaced else 1)
        self.interlaced = int(interlaced)
        specs = Specs(is_50hz, interlaced)
        self.vertical = Vertical(frequency, is_50hz, interlaced)
        self.horizontal_clock = HorizontalClock(self.vertical,specs,beam)
        self.vertical_clock = VerticalClock(self.vertical,beam)
        self.horizontal = Horizontal(x_resolution,self.horizontal_clock,overscan,rep)
        self.overscan = overscan
        self.x_resolution = x_resolution
        self.y_resolution = (self.vertical.image * frame_fields) - (overscan.top + overscan.bottom)
        self.lines = self.vertical.image * frame_fields
        self.fps = self.vertical.fps
        self.pixel_clock = self.vertical.scanlines * self.horizontal.scanline * frequency
        


def calc_overscan(left, right, top, bottom, lines, is_50hz, interlaced) :
    specs = Specs(is_50hz,interlaced)
    resolution = specs.vertical.lines if not interlaced else specs.vertical.lines * 2
    return Overscan(
        left,
        right,
        top if lines == 0 else round((resolution - min(LINES_CALC,lines)) / 2),
        bottom if lines == 0 else round((resolution - min(LINES_CALC,lines)) / 2)
    )

def adjust_number_within_range(number, min_value, max_value):
   # Ensure min_value is less than or equal to max_value
    if min_value > max_value:
        min_value, max_value = max_value, min_value
    if number < min_value:
        return min_value
    elif number > max_value:
        return max_value
    else:
        return number

def calc_freq(freq,is_50hz):
    freq = float(freq)
    min_50hz = 49.5
    max_50hz = 50.5
    min_60hz = 58
    max_60hz = 62

    if freq == 0:
        freq = 60 if not is_50hz else 50
    return adjust_number_within_range(freq,min_50hz,max_50hz) if is_50hz else adjust_number_within_range(freq,min_60hz,max_60hz)

def calc_timings(x_resolution,is_50hz,interlaced,freq,overscan,rep):
    timing = Scan(x_resolution, is_50hz, interlaced, calc_freq(freq,is_50hz),overscan,rep)
    return timing
    
def hdmi_timings(timing):
    #If rep equals one, so rep isn't not applyable
    rep = 0 if timing.horizontal.rep == 1 else timing.horizontal.rep

    return 'hdmi_timings {} 1 {} {} {} {} 1 {} {:.0f} {} 0 0 {} {} {} {:.0f} 1'.format(
        timing.horizontal.image + timing.overscan.left + timing.overscan.right,
        timing.horizontal.front_porch,
        timing.horizontal.sync_pulse,
        timing.horizontal.back_porch,
        timing.lines,
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
    hzn = timing.horizontal.image + timing.overscan.left + timing.overscan.right #horizontal res
    hfp = hzn + timing.horizontal.front_porch #horizonal front porch
    hsp = hfp + timing.horizontal.sync_pulse  #horizontal sync pulse
    hbp = hsp + timing.horizontal.back_porch  #horizontal back porch
    vrc = timing.lines                        #vertical res
    vfp = vrc + timing.vertical.front_porch   #vertical front porch
    vsp = vfp + timing.vertical.sync_pulse    #vertical sync pulse
    vbp = vsp + timing.vertical.back_porch    #vertical back porch
    if timing.interlaced :
        vfp = vrc + timing.vertical.front_porch * 2
        vsp = vfp + timing.vertical.sync_pulse * 2
        vbp = vsp + timing.vertical.back_porch * 2
    hsy = "+HSync"
    vsy = "-VSync"
    itl = "Interlace" if timing.interlaced else ""

    return " ".join(['"{}x{}_{:.0f}" {:.6f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f}'
                     .format(hzn,vrc,fps, clk, hzn, hfp, hsp, hbp,vrc,vfp,vsp,vbp),hsy,vsy,itl])

#TODO: Revise xrand
def xrandr_scale(timing):
    vertical = 1 if timing.interlaced and timing.x_resolution >= 512 else 2
    horizontal = 1 if timing.horizontal.rep == 1 else 1 / timing.horizontal.rep
    return str(horizontal)+"x"+str(vertical)

def verbosely(timing,is_50hz, interlaced):
    templ_vert = '\t{:<12}: {:>8} lines - {:>6.2f} (nS)'
    templ_horz = '\t{:<12}: {:>8} px - {:>6.2f} (uS)'
    templ_freq = '\t{:<12}: {:>8.0f} Hz'
    print("\nLines per field.", "Interlaced mode. Two fields per frame:" if interlaced else ":")
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
    print("\nBroadcast    :","System-M (NTSC/PAL-M)" if not is_50hz else "System-B/D/G/H/I/K/N (PAL-EU/SECAM)")
    print('Resolution   : {}x{}'.format(timing.x_resolution,timing.y_resolution))
    print('Frames       : {:.2f}'.format(timing.fps))
    print("")

def fbset(timings):
    time.sleep(0.5)
    Popen([
        'fbset',
        '-depth', '32', 
        '-xres',str(timings.x_resolution), 
        '-yres',str(timings.y_resolution),
        '-left',str(timings.overscan.left),
        '-right',str(timings.overscan.right),
        '-upper',str(timings.overscan.top),
        '-lower',str(timings.overscan.bottom)
    ])

def apply_vcgencmd(timings):
    vcgencmd = [os.path.join('/','usr','bin','vcgencmd'),hdmi_timings(timings)]
    _exec=Popen(vcgencmd)
    _exec.wait()
    _exec=Popen([tvservice,'-e','DMT 87'])
    _exec.wait()
    _exec=Popen([tvservice,'-e','DMT 88'])
    _exec.wait()
    fbset(timings)

def apply_xrandr(timings, output, options):
    modeln = modeline(timings)
    modename = modeln.split(" ",1)[0]
    xrandr = os.path.join('/','usr','bin','xrandr')
    try :
        _exec=Popen([xrandr,'--delmode',output,modename],stdout=PIPE, stderr=DEVNULL)
        _exec.wait()
        _exec=Popen([xrandr,'--rmmode',modename],stdout=PIPE, stderr=DEVNULL)
        _exec.wait()
    finally :
        _exec=Popen([xrandr,'--newmode']+modeln.split(" "))
        _exec.wait()
        _exec=Popen([xrandr,'--addmode',output,modename])
        _exec.wait()
        output = [xrandr,'--output',output,'--mode',modename,'--scale',xrandr_scale(timings)]
        if isinstance(options, str):
            output = output + options.split(" ")
        _exec=Popen(output)

def set_composite_mode(timings,is_50hz,is_progressive):
    system = 'PAL' if is_50hz else 'NTSC'
    progressive = 'P' if is_progressive else ''
    argument = '%s 4:3 %s' % (system, progressive)
    _exec = Popen([tvservice,'-c',argument])
    _exec.wait()
    fbset(timings)

def is_hdmi_connected():
    return 'HDMI' in str(Popen([tvservice,'-l'],stdout=PIPE).communicate()[0])

def calc_lines(lines,is_50hz,interlaced) :
    specs = Specs(is_50hz,interlaced)
    if lines == 0 : 
        return specs.vertical.resolution
    return adjust_number_within_range(lines,80,specs.vertical.resolution)

def set_interlaced_by_resolution(lines,is_50hz) :
    specs = Specs(is_50hz,True)
    # If lines are above to progressive max resolution, set as interlaced (true) otherwise set as progressive (false).
    return lines > specs.vertical.lines + specs.vertical.back_porch 

tvservice = os.path.join('/','usr','bin','tvservice')
parser = argparse.ArgumentParser(description="Switch the HDMI output resolution for SDTV friendly modes")
parser.add_argument("--width","-w", metavar = '720',type=int, help = "Width resolution value",default=720)
parser.add_argument("--lines", "-l", metavar = '480', type=int, help = "Height resolution value. (supress the -p value)", default=0)
parser.add_argument("--frequency","-f", metavar= '60',type=float, help = "Refresh rate",default=0)
parser.add_argument("--progressive","-p",action='store_true', help="Progressive 240p/288p. (supressed if --height is defined)",default=False)
parser.add_argument("--no-rep","-r",action='store_true', help="Disables Rep. Rep Multiplies pixel clock for fine-tuning the back porch and front porch")
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
interlaced = not args.progressive
#If lines value its defined, supress the definition of -p parameter and automatically defines if its progressive or not and calculate the overscan
if args.lines > 0 : 
    interlaced = set_interlaced_by_resolution(args.lines, args.pal)

LINES_CALC = calc_lines(int(args.lines),args.pal,interlaced)

overscan = calc_overscan(args.overscan_left, args.overscan_right, args.overscan_top, args.overscan_bottom, args.lines, args.pal, interlaced)

timings = calc_timings(args.width, 
    args.pal, 
    interlaced,
    args.frequency,
    overscan,
    not args.no_rep
)
if args.json :
    print(outputjson(timings))
elif args.verbose :
    verbosely(timings, args.pal, interlaced)



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
            apply_vcgencmd(timings) if is_hdmi_connected() else set_composite_mode(timings,args.pal, args.progressive)
    except FileNotFoundError :
        print("Unable to apply the settings because either vcgencmd or tvservice was not found. Are you running on Pi?")
        print("Assuming you're running only just for information, follows below. Try next time using -i --info.")
        if args.x11_modeline :
            print(modeline(timings))
        else :
            print(hdmi_timings(timings))
