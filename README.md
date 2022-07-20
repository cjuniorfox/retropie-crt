# retropie-crt
This project enables Raspberry Pi with Retropie to work outputting with the proper resolution, scanline configuration (progressive or interlaced) and proper pixel aspect ratio, enabling displaying to CRT display as the intended emulated game console and outputting with interlaced resolution when at the Emulationstation.
## Disclaimer

The Raspberry Pi it's an amazing device highly customizable, and the HDMI output it's one of the customizable things.
Bundled with raspbian, the basis of the Retropie distribution, it haves a tool called "vcgencmd" allowing setting up various parameters related to display output. The detailed technical specs like pixel clock and sync pulse parameters can be customizable with that tool.
This scripting was built to drive the "vcgemcmd" tool switching the HDMI output to match it at the closest settings for the original emulated platform as possible. The mode it's switched on the fly. Meaning that when you're browsing over the Emulationstation, the display settings will be optimized for that content, while switching the display mode for the target emulated platform when the emulation starts.
That means, if you're emulating SNES, the display output will output as the desired settings for outputting the 256x224 or 512x240 with the proper aspect ratio, scanline mode and refresh rate. 

I tested with a cheap Chinese HDMI to YPbPr converter brought from Aliexpress. I believe that other converters, like HDMI to VGA or HDMI to SCART will also work as well. Be aware that if you're wanting to use an HDMI to VGA adapter for outputting to a CRT VGA Display, the intended display must be capable of handling the 15Khz signal. In a near future, I can manage to add the 31Khz support. But currently, it's not supported.

The set of scripting basically it's composed of two python scripts. The "chvideo.py" and "consoledisp.py".

### chvideo.py

This script drives the "vcgencmd" for outputting the desired video mode accordingly with the desired specs, like horizontal resolution, scanline mode and refresh rate. It does the calculation needed for the intended video settings.

### consoledisp.py

This one has all the intended modes and manages the customizable settings for the target platform emulated. Driving the "chvideo" script.

## Requiriments

. A Raspberry Pi. Tested at the Raspberry Pi 3. Far as the "vcgemcmd" tool exists, it should work.
. Retropie.
. An HDMI to analog display signal converter. Be aware that it needs to be a simple converter without any video processing. Just search for "HDMI to YPbPr" or "HDMI to VGA"  in any online Chinese store.
![HDMI to Component Adapter](hdmi_to_component.png)
## Initial setup

. Enable the SSH at raspi-config as [described here](https://retropie.org.uk/docs/SSH/).
. From the same network and any command-line tool like Terminal or CMD, copy and paste the commands below.
> ssh pi@retropie 'bash <(curl -s https://raw.githubusercontent.com/cjuniorfox/retropie-crt/main/setup.sh)'
. Type the Raspberry's password if asked. The default password generally it's 'raspberry'.
. The automated tool will install all the files needed. Then finishes, a new option will be available from the Emulationstation's Retropie option menu called 'RETROPIE-CRT'.It isn't, will be needed to restart the Emulationstation.
. A new option will be available from the Emulationstation's Retropie option menu called 'RETROPIE-CRT'. To enable the CRT display settings, go to that option and enable the desired display mode between 625 50Hz (aka PAL), 525 60Hz (aka NTSC) or switch back to HDMI mode choosing HDTV.

Important: Don't plug the Raspberry into the CRT display before applying the configuration unless knowing if your set it's capable to handle HDTV signals, with the risk of harming the set deflection circuitry if you do so.

## Configuring the CRT Television modes.

At the first setup, keep your Raspberry connected to an HDTV-capable display over the HDMI and follow the steps below.

.With the gamepad, navigate to the Retropie Menu and then, choose "RETROPIE-CRT" options menu.
![Retropie-CRT menu](main_menu.png)

Choose the most appropriate option for your needs. You have three options.

- SDTV - 525 60Hz aka NTSC (Americas/Japan) - It's the common option to play most of the systems as if you're emulating an American or Japanese set.
- SDTV - 625 50Hz aka PAL (Europe/Asia/Africa) - Enables the PAL mode, to run at 50 Hz sets.
- HDTV - Unsets the whole configuration and makes the HDMI behave as default. Be aware this option does not uninstall the tool itself but just switches back the configuration of Raspberry's HDMI output.

# CHANGELOG

- Fixes some texting
- Added minimal support for users with composite video mode.