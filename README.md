# retropie-crt
Some scripting to enable retropie to run as 240p with some HDMI to analog adapter

## Disclaimer

The Raspberry Pi it's an amazing device highled customizable, and the HDMI output it's one the customizable things.
Bundled with raspbian, the basis distribuition of retropie, it have one tool called "vcgencmd" allowing setup various parameters related to display output. The detailed tecnical things like pixel clock and sync pulse.
The scripting at this repository was built to drive the vcgemcmd tool switching the HDMI output mathing it to the closest settings for the original emulated video game console. The mode it's switched over the fly. Meaning when you're navegating over the emulationstation options, the contend will be displayerd at 480i. Now, when you run some game, the device switchs the output matching to the target platform specs.
What's mean, it's if you would play SNES, the display output will switch on the fly to 256x224 or 512x240. The pixel aspect ratio setting also it's changed to match the target platform. Whitout shimmering. 

With just an single cheap HDMI to component video converter, you'll be able run your Raspberry at CRT television set, PVM monitor or any display device with component video input to run emulated platforms at CRT closest possible as the target's original hardware behavior.

It's not tested yet, but may be possible to use with HDMI to VGA adapter or with HDMI to SCART adapter, far as that adapter doesn't do any video processing at all.

The set os scripting it's composed of two major tools "chvideo.py" and "consoledisp.py".

### chvideo.py

This Python script drives the "vcgencmd" to outputs the SDTV accordingly with the desired specs, like horizontal resolution, scanning type and blanking interval. It makes the whole calculation needed to make this possible.

### consoledisp.py

This one takes care to manage all customizable settings for the video game console or home computing emulated at the Raspberry PI. It drives the chvideo to switch the display mode.

## Requiriments

. Raspberry PI (Any model compatible with Retropie).
. Retropie built flashed into Pi's SDCard.
. HDMI to component video or HDMI to VGA converter. Aaware it needs to be simple converter without any video processing at all. Just search for "HDMI to Component" or "HDMI to VGA"  from any online chinese marketplace.
![HDMI to Component Adapter](hdmi_to_component.png)
## Initial setup

. Enable the SSH at raspi-config as [described here](https://retropie.org.uk/docs/SSH/).
. From the same network and from any command line tool like Terminal or CMD, copy and paste the commands below.
> ssh pi@retropie 'bash <(curl -s https://raw.githubusercontent.com/cjuniorfox/retropie-crt/main/setup.sh)'
. Type Raspberry's password if asked. The default password normally is 'raspberry'.
. The automated tool will install all the files needed to switch between HDTV and SDTV modes from the Retropie menu option named  'RETROPIE-CRT'.
. Your device will restart automatically. After that, you're ready to configure your Raspberry to work with your CRT Display.

Attention: Don't plug in the Raspberry into the CRT display before applying the configuration with risk of harming the television's deflection circuitry if you do so.

## Configuring the CRT Television mode.

The configuration it's very easy and straightfoward. If it's the first time you be running the configuration, folow this step with Raspberry still conected to your HDTV. 

.Using the gamepad, navegate to the Retropie Menu and then, you'll found an new option named "RETROPIE-CRT".
.Open that option and one menu will shown as below.
![Retropie-CRT menu](main_menu.png)

Choose the most appropriate option for your needs. You have three options.

- SDTV - NTSC/PAL-M - It's the most common option to play most of systems as if you're running at an American or Japan television set.
- SDTV - PAL-EU - Enables the PAL mode, to run at 50 Hz at European television set.
- HDTV - Unsets the the whole configuration to make the HDMI output back to default HDMI setting. Be aware this option does not uninstall the tool itself, just switch back the configuration to get back te original behavior of Raspberry's HDMI output. When this mode is set , does not plug your Raspberry PI to CRT television set, with risk of damaging the deflection circuitry if you do so.

# CHANGELOG

- Added minimal support for users with composite video mode.