#!/usr/bin/python3
import json, subprocess, os, re, shutil
from subprocess import PIPE

def install_boot_cfg():
    config_path=os.path.join('/','boot','config.txt')
    config=[]
    with open(config_path) as config_file:
        original_config = config_file.readlines()
    #Find for the parameter to be added, removing them from the new config file array
    new_config = []
    properties='(hdmi_timings|overscan_scale|hdmi_group|hdmi_mode)'
    for line in original_config:
        if not re.search(properties,line):
            new_config.append(line.replace('\n',''))
    #Get new hdmi timming parameters for the desired configuration
    chvideo = ['chvideo','-T','8','-B','8','-L','32','-R','32','-f','60','-i']
    try:
        proc = subprocess.Popen(chvideo,stdout=PIPE)
        proc.wait()
        data, err = proc.communicate()
        hdmi_timings = data.decode('utf-8').replace('timings ','timings=').replace('60.0','60').replace('\n','')
        new_config.append(hdmi_timings)
        new_config.append('overscan_scale=0')
        new_config.append('hdmi_groud=2')
        new_config.append('hdmi_mode=87')
        print('The config.txt was configured successfully!')
    except:
        print('Personally, It\'s embarrassing for me, but I was unable to properly run '+chvideo[0]+'. Sorry.')
        quit()

def install_scripts(scripts, origin_path, dest_path):   
    for script in scripts:
        if isinstance(script,str):
            orig = os.path.join(origin_path,script)
            dest = os.path.join(dest_path,script)
        elif isinstance(script,list) and isinstance(script[0],str) and isinstance(script[1],str):
            orig = os.path.join(origin_path,script[0])
            dest = os.path.join(dest_path,script[1])
        else:
            raise Exception('There\'s some error on script.')
        try:
            shutil.copyfile(orig,dest)
            os.chmod(dest,0o0755)
            print('Installed '+ dest + 'successfully!')
        except:
            print('It\'s sad to say, but I failed installing \"'+ orig + '\".\nSorry to dissapointing you!\nBye for now...')
            quit()
    print("I\'m proudly say the scripts: "+ " , ".join(r'%s' % w[0] if isinstance(w,list) else w for w in scripts) +" for this step was installed successfully!")

def install_chvideo_consoledisp():
    scripts = [
        ['chvideo.py','chvideo'],
        ['consoledisp.py','consoledisp']
    ]
    path = os.path.join('usr','bin')
    origin_path = os.path.join(resources,path)
    dest_path = os.path.join('/',path)
    install_scripts(scripts,origin_path,dest_path)

def install_runcommand():
    scripts = ['runcommand-onstart.sh','runcommand-onend.sh']
    path = os.path.join('opt','retropie','configs','all')
    origin_path = os.path.join(resources,path)
    dest_path = os.path.join('/',path)
    install_scripts(scripts,origin_path, dest_path)

def get_platform_parameters(platform):
    arguments = ['consoledisp',platform,'-i','-j']
    try:
        proc = subprocess.Popen(arguments,stdout=PIPE)
        proc.wait()
        data, err = proc.communicate()
        if proc.returncode is 0:
            jsondata = data.decode('utf-8')
            scandata = json.loads(jsondata)
            return (str(scandata['x_resolution']),str(scandata['y_resolution']),str(scandata['vertical']['fps']))
    except:
        raise("Unfortunely I was unable properly to obtain parameters for the platform " + platform)

def define_consoledisp_config(origin_cfg_path,platform):
    print("Processing data for platform: "+platform)
    x,y,fps = get_platform_parameters(platform)
    config_file = []
    with open(origin_cfg_path) as file:
        for line in file:
            config_file.append(line.replace('%x_resolution%',x).replace('%y_resolution%',y).replace('%refresh%',fps))
    return config_file
    

def install_retroarch_cfg():
    path = os.path.join('opt','retropie','configs')
    origin_path = os.path.join(resources,path)
    dest_path = os.path.join('/',path)
    for platform in os.listdir(origin_path):
        origin_cfg_path = os.path.join(origin_path,platform,'retroarch.cfg')
        if os.path.isfile(origin_cfg_path):
            config = define_consoledisp_config(origin_cfg_path,platform)
            


if os.geteuid() != 0:
    print('Excuse-me, but this script must be run under root privileges.\nI appreciate if try again using \'sudo\'.\nBye for now...')
    quit()

resources = os.path.join(os.getcwd(),'resources')

install_chvideo_consoledisp()
install_boot_cfg()
install_runcommand()
install_retroarch_cfg()

