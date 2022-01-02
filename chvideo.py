#!/bin/python
class VerticalTiming:
    def __init__(self,verticalLines,beam):
        self.scan = beam / verticalLines.freq;
        self.image = (self.scan * verticalLines.image)/verticalLines.scan
        self.frontPorch = (self.scan * verticalLines.frontPorch) / verticalLines.scan
        self.sync = (self.scan * verticalLines.sync) / verticalLines.scan
        self.backPorch = (self.scan * verticalLines.backPorch) / verticalLines.scan
        self.totalBlank = self.frontPorch + self.sync + self.backPorch

class VerticalLines:
    def __init__(self, scan, image, frontPorch, sync, freq):
        self.scan = scan
        self.image = image
        self.frontPorch = frontPorch
        self.sync = sync
        self.backPorch = self.scan - self.image- self.frontPorch - self.sync
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
    def __init__(self,pixels,hTimming):
        pixelRep = 1280
        self.rep = int(round(pixelRep/pixels,0))
        self.image = pixels * self.rep
        self.scan = int(round(self.image * (hTimming.scan/ hTimming.image),0))
        self.frontPorch = int(round(self.scan * (hTimming.frontPorch / hTimming.scan),0))
        self.backPorch = int(round(self.scan * (hTimming.backPorch / hTimming.scan),0))
        self.sync = int(round(self.scan * (hTimming.sync / hTimming.scan),0))
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
    def __init__(self,hPixels, tvSystem, freq, interlaced, overscan):
        if tvSystem not in "PAL NTSC" :
            print("The tv system need to be either PAL or NTSC")
            exit(1)
        beam = 1000;
        lineFactor = (2 if interlaced else 1);
        #NTSC
        self.vLines = VerticalLines(262.5, 240, 3, 3, freq)
        self.hTimming = HorizontalTimming(self.vLines,0.024,0.074,0.074,beam)
        if tvSystem == "PAL" :
            self.vLines = VerticalLines(312.5, 288, 3, 3, freq)
            self.hTimming = HorizontalTimming(self.vLines,0.025,0.074,0.088,beam)
        self.vTimming = VerticalTiming(self.vLines,beam)
        self.hPixels = HorizontalPixels(hPixels,self.hTimming)
        self.vertPixels = self.vLines.image * lineFactor
        self.pixelClock = int(round(self.vLines.scan * self.hPixels.scan * freq,0))
        

def ntsc(hPixels,interlaced,overscan) :
    NTSC = Scan(hPixels,"NTSC",59.94,interlaced, overscan)
    return NTSC

def pal(hPixels,interlaced,overscan) :
    PAL = Scan(hPixels,"PAL",50,interlaced, overscan)
    return PAL

def image(freq):
    o = Overscan(32,32,16,16);
    system = ntsc(720,True,o);
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
    print("Pixel Clock: ", system.pixelClock);
image(50)
