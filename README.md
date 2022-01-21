# retropie-crt
Some scripting to enable retropie to run as 240p with some HDMI to analog adapter

## Disclaimer

The Raspberry Pi it's an amazing device highled customizable, and the HDMI output it's one the customizable things.
Bundled with raspbian, the basis distribuition of retropie, haves one tool called "vcgencmd" allowing setup various settings related to display output. The detailed tecnical things like pixel clock, front porch timing, back porch timing, sync pulse and goes on.
The scripting found on this repository was writed to drive the vcgemcmd tool to switching the HDMI output mathing it to the closest settings found at the original emulated video game console. The modes can be switched on the fly. That's mean when you're navegating over the emulationstation, the contend will be displayerd at 480i. When you select an game, the device will switch the display output to match the emulated video game console specs.
That's mean, if you would like to play SNES, the display output will switch on the fly to 256x224 or 512x240 and setting the pixel aspect ratio to match the original hardware. No shimmering or weard artifacts. Switching to another video game console, the display settings switch to outputs 320x224 just like the original console. 

So, with some cheap HDMI to Component converter, you'll will be able plug in your Raspberry at CRT television set, PVM monitor or any display device with Component input.
It's also possible using an cheaper HDMI to VGA Adapter. If it, with some simple adapter or soldering skill, you'll be able to plug your Raspberry to any SCART enabled display. 

The set os scripting it's composed of two major tools "chvideo.py" and "consoledisp.py".

### chvideo.py

This Python script drives the "vcgemcmd" to outputs the SDTV accordingly with the specs, like horizontal resolution, scanning type and blanking interval. It makes the whole calculation needed.

### consoledisp.py

This one encharge to manage all custom settings for the video game console or home computing emulated for the Raspberry PI. It drives the chvideo to switch the display mode.

## Requiriments

. Raspberry PI (Any model compatible with Retropie)
. Retropie flashed into Pi's SDCard
. HDMI to YPbPr or HDMI to VGA converter. Be aware it needs to be an simple converter without any video processing. Just search for "HDMI to Component" or "HDMI to VGA" at your favorite chinese marketplace.
![HDMI to Component Adapter](hdmi_to_component.png)
## Initial setup

. Enable the SSH at raspi-config as [described here](https://retropie.org.uk/docs/SSH/).

. At the same network and at any command line tool like Terminal or CMD, copy and paste the command below.
> ssh pi@retropie 'bash <(curl -s https://raw.githubusercontent.com/cjuniorfox/retropie-crt/main/setup.sh)'

. Type raspberry's password if asked.

After that, you're ready to configure your Raspberry to work with your CRT Display.

Attention: Don't run the Raspberry at the CRT television before applying the configuration with risk of harming the television's deflection circuitry if you do.

## Configuring the CRT Television mode.

The configuration it's very straightfoward. With your Raspberry still conected to your HDTV, navegate to the Retropie Menu and there, you're found an new option named "RETROPIE-CRT".
Open that option and an Menu will shown as below.
![Retropie-CRT menu](main_menu.png)

Choose the most appropriate option for your needs. You have three options.

- SDTV - NTSC/PAL-M It's the most common option to play most of systens as if you're running an American or Japan video game console.
- SDTV - PAL-EU Enable PAL mode, to run at some European television set and like an European console or 8-bit computer.
- HDTV - Unsets the script to make the HDMI output back to default HDMI behavior, as the emulators settings.