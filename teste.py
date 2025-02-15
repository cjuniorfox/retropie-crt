import re


new_config = '''
hdmi_group = 2
hdmi_mode = 87
hdmi_timing = 20212 2323 22221 44 5
'''

actual_config = '''
# Enable audio (loads snd_bcm2835)
dtparam=audio=on

[pi4]
# Enable DRM VC4 V3D driver on top of the dispmanx display stack
#dtoverlay=vc4-fkms-v3d
max_framebuffers = 2

[all]
arm_freq = 1350
hdmi_group=1
core_freq = 500
over_voltage=4
hdmi_mode=6
'''

def read_configs():
    new_configs = new_config.splitlines(keepends=True)
    actual_configs = actual_config.splitlines(keepends=True)
    new_dict = {line.split("=", 1)[0].strip(): line for line in new_configs if "=" in line and not line.startswith("#")}

    updated_config = []

    for line in actual_configs:
        if line.startswith("#"):
            updated_config.append(line)
        elif line.split("=", 1)[0].strip() in new_dict:
            updated_config.append(new_dict[line.split("=", 1)[0].strip()])
            new_dict.pop(line.split("=", 1)[0].strip())
        else:
            updated_config.append(line)


    print(updated_config + list(new_dict.values()))
            

read_configs()