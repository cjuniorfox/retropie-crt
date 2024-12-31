#!/usr/bin/python3
import json, subprocess, os, re, shutil, sys,random, argparse
from subprocess import PIPE,Popen
from pathlib import Path

sys.tracebacklimit = 0

paths = {
    'retropie-crt': {
        'path': os.path.join('opt','retropie-crt')
    },
    'boot_cfg': {
        'path': os.path.join('boot', 'config.txt')
    },
    'chvideo_consoledisp': {
        'path': os.path.join('opt', 'retropie-crt', 'scripts'),
        'filenames': ['chvideo.py', 'consoledisp.py','chvideocore.py']
    },
    'chvideo_consoledisp_symlinks': {
        'path': os.path.join('usr', 'local', 'bin'),
        'filenames': ['chvideo', 'consoledisp','chvideocore']
    },
    'runcommand': {
        'path': os.path.join('opt', 'retropie', 'configs', 'all'),
        'filenames': ['runcommand-onlaunch.sh', 'runcommand-onend.sh']
    },
    'retroarch_cfg': {
        'path': os.path.join('opt', 'retropie', 'configs'),
        'filename': 'retroarch.cfg'
    },
    'retroarch_core_options': {
        'path': os.path.join('opt', 'retropie', 'configs', 'all'),
        'filename':'retroarch-core-options%s.cfg'
    }
}

class ConfigParser:
    def config_to_dict(self, config):
        settings = {}
        includes = {}
        for l in config:
            if '=' in l and not l.strip().startswith('#'):
                k, v = l.strip().split("=",1)
                settings[k.strip()] = v.strip()
            else:
                if l.strip() != '':
                    if l.strip().startswith('#include'):
                        includes[l.strip()] = ""
                    else:
                        settings[l.strip()] = ""
        return settings,includes

    def dict_to_config(self, dict_list, with_spaces = True):
        conf = []
        for key, val in dict_list.items():
            if val.strip() != '':
                if with_spaces:
                    conf.append(f"{key} = {val}")
                else:
                    conf.append(f"{key}={val}")
            else:
                conf.append(f"{key}")
        return conf
    

def origin_path(path):
    return os.path.join(resources,path)

def target_path(path):
    return os.path.join('/',path)

def print_celebrating(award):
    #ANSI Color escape code at https://media.geeksforgeeks.org/wp-content/uploads/20201223013003/colorsandformattingsh.png
    coloredaward = '\33[1;49;92m"%s"\33[0m' % award
    celebs=[\
        'The %s was installed.',
        'The %s was installed successfully.',
        'Installed the %s with success',
        'The %s was installed gracefully',
        'The %s was installed well.',
        'The %s was proudly installed.',
        'Proudly the %s was installed successfully.',
        'Managed to install the %s ok.',
        'The %s was installed with no worries.',
        'Wonderful, the %s was installed.']
    print(celebs[random.randint(0,len(celebs) - 1)] % coloredaward)

def hdmi_timings(platform):
    cmd = ['consoledisp',platform,'-i']
    if isPal: #If PAL, setup as is
        cmd.append('-P')
    try:
        proc = Popen(cmd,stdout=PIPE)
        proc.wait()
        data,_ = proc.communicate()
        return data.decode('utf-8').replace('hdmi_timings ','').replace('60.0','60').replace('50.0','50')
    except FileNotFoundError:
        raise FileNotFoundError("It's very embarrassing, but I was unable to properly run '%s'. Sorry." %  cmd[0])

def write_new_file(lines,path,celebrating=True):
    merged_lines = '\n'.join(lines)
    try:
        with open(path,"w") as file:
            file.write(merged_lines)
        if celebrating :
            print_celebrating(path)
    except PermissionError as e:
        if e.errno == 13:
            raise PermissionError('I\'m having a hard time with a permission error while trying to write the \33[1;49;31m"%s"\33[0m.' % path)
        else:
            raise PermissionError('I\'m having some permission error while trying to write the file \33[1;49;31m"%s"\33[0m and, I was unable to figure out which one is. Here\'s the exception:\n%d - %s' % (path,e.errno,e.strerror))

def install_cfg(config,target_path, with_spaces = True):
    if isinstance(config,str):
        with open(config) as file:
            new, new_inc = ConfigParser().config_to_dict(file.readlines())
    elif isinstance(config,list): 
            new, new_inc = ConfigParser().config_to_dict(config)
    with open(target_path) as file:
        old,old_inc = ConfigParser().config_to_dict(file.readlines())
    #The _inc is the includes. To be placed at the end of the file
    merged = {**old, **new, **old_inc, **new_inc}
    merged_config = ConfigParser().dict_to_config(merged,with_spaces)
    write_new_file(merged_config,target_path)
    
def uninstall_cfg(config_path,target_path):
    with open(config_path) as file:
        config = file.readlines()
    #This outputs something like (properties1|properties2|properties)
    properties = "(%s)" % "|".join(w.split("=")[0] for w in config)
    target = []
    with open(target_path) as file:
        for line in file:
            if not re.search(properties,line):
                target.append(line)
    write_new_file(target,target_path,False)
    print('Uninstalled settings for \33[1;49;92m"%s"\33[0m as asked.' % target_path)

def install_boot_cfg():
    path = paths['boot_cfg']['path']
    #Configurations to local array
    timings = hdmi_timings('emulationstation')
    config = []
    with open(origin_path(path)) as file:
        for line in file:
            config.append(line.replace('%hdmi_timings%',timings))
    install_cfg(config,target_path(path),with_spaces=False)

def uninstall_boot_cfg():
    path = paths['boot_cfg']['path']
    uninstall_cfg(origin_path(path),target_path(path))

def install_scripts(scripts, origin_path, dest_path):   
    for script in scripts:
        directory = Path(dest_path)
        if not directory.exists():
            directory.mkdir(parents=True)
        if isinstance(script,str):
            orig = os.path.join(origin_path,script)
            dest = os.path.join(dest_path,script)
        elif isinstance(script,list) and isinstance(script[0],str) and isinstance(script[1],str):
            orig = os.path.join(origin_path,script[0])
            dest = os.path.join(dest_path,script[1])
        try:
            shutil.copyfile(orig,dest)
            os.chmod(dest,0o0755)
            print_celebrating(dest)
        except FileNotFoundError:
            raise FileNotFoundError('So sad! I failed miserably installing \33[1;49;31m"%s"\33[0m.\nSorry to disappointing you!' % orig)
    print_celebrating(" , ".join(r'%s' % w[0] if isinstance(w,list) else w for w in scripts))

def uninstall_directory():
    shutil.rmtree(os.path.join(target_path(paths['retropie-crt']['path'])))

def uninstall_scripts():
    script_list = [
            paths['chvideo_consoledisp'],
            paths['chvideo_consoledisp_symlinks'],
            paths['runcommand']
        ]
    
    for script in script_list:
        for filename in script['filenames']:
            try:
                path = os.path.join(target_path(script['path']),filename)
                os.remove(path)
                print('File: \33[1;49;92m"%s"\33[0m uninstalled.' % path)
            except PermissionError as e:
                raise PermissionError('Permission error when removing \33[1;49;31m"%s"\33[0m. %s' % (path,e.strerror))
            except FileNotFoundError as e:
                raise FileNotFoundError('The file does not exist: \33[1;49;31m"%s"\33[0m. %s' % (path,e.strerror))
    uninstall_directory()


def install_chvideo_consoledisp():
    path = paths['chvideo_consoledisp']['path']
    install_scripts(paths['chvideo_consoledisp']['filenames'],origin_path(path),target_path(path))
    path = paths['chvideo_consoledisp_symlinks']['path']
    install_scripts(paths['chvideo_consoledisp_symlinks']['filenames'],origin_path(path),target_path(path))

def install_runcommand():
    scripts = [
        ['runcommand-onlaunch%s.sh' % ('-pal' if isPal else ''),'runcommand-onlaunch.sh'],
        ['runcommand-onend%s.sh' % ('-pal' if isPal else ''),'runcommand-onend.sh']
    ]
    path = paths['runcommand']['path']
    install_scripts(scripts,origin_path(path), target_path(path))

def get_platform_parameters(platform):
    arguments = ['consoledisp',platform,'-i','-j']
    if(isPal): #If it's PAL, setup as is
        arguments.append('-P')
    try:
        proc = subprocess.Popen(arguments,stdout=PIPE)
        proc.wait()
        data, _ = proc.communicate()
        if proc.returncode == 0:
            jsondata = data.decode('utf-8')
            scandata = json.loads(jsondata)
            return (str(scandata['x_resolution']),str(scandata['y_resolution']),str(scandata['vertical']['fps']))
    except FileNotFoundError:
        raise FileNotFoundError("Unfortunately I was unable to properly obtain the parameters for the platform " + platform)

def define_consoledisp_config(origin_cfg_path,platform):
    x,y,fps = get_platform_parameters(platform)
    config_file = []
    with open(origin_cfg_path) as file:
        for line in file:
            config_file.append(line.replace('%x_resolution%',x).replace('%y_resolution%',y).replace('%refresh%',fps))
    return config_file
    

def install_retroarch_cfg(install = True):
    path = paths['retroarch_cfg']['path']
    filename = paths['retroarch_cfg']['filename']
    origin_dir = origin_path(path)
    dest_dir = target_path(path)
    for platform in os.listdir(origin_dir):
        origin = os.path.join(origin_dir,platform,filename)
        target = os.path.join(dest_dir,platform,filename)
        if os.path.isfile(origin) and os.path.isfile(target):
            if install:
                config = define_consoledisp_config(origin,platform)
                install_cfg(config,target)
            else:
                uninstall_cfg(origin,target)

def install_retroarch_core_options(install = True):
    filename = paths['retroarch_core_options']['filename'] % ('-pal' if isPal else '')
    target_filename= paths['retroarch_core_options']['filename'] % ''
    path = paths['retroarch_core_options']['path']
    origin = os.path.join(origin_path(path),filename)
    target = os.path.join(target_path(path),target_filename)
    if install:
        install_cfg(origin,target)
    else:
        uninstall_cfg(origin,target)

def install():
    print("Welcome to the setup script. I'll be your host during this process. Sit down, make a mug of coffee and relax during the installation.\n")
    install_chvideo_consoledisp()
    install_boot_cfg()
    install_runcommand()
    install_retroarch_cfg()
    install_retroarch_core_options()
    print("\nI just finished all the needed steps to configure your Raspberry for working with CRT display over HDMI. It's recommended turn off your Raspberry and plug then into the CRT display. Enjoy your emulator like you're playing at the original hardware.\n That's all. See ya")

def uninstall():
    print("Starting the uninstallation process.")
    install_retroarch_core_options(False)
    install_retroarch_cfg(False)
    uninstall_boot_cfg()
    uninstall_scripts()
    print("All settings were removed and your HDMI output it's now back to the default settings. It's highly recommended to turn off your Raspberry and disconnect it from the CRT display, with a risk of harming the set's deflection circuitry if you don't.")

parser = argparse.ArgumentParser(description="Set up the retropie-crt to make it work with some cheap Chinese HDMI to YPbPr adapter")
parser.add_argument("--pal","-P",action='store_true',help="Apply the 625 50i (aka PAL) settings")
parser.add_argument("--uninstall",'-u', action='store_true',help="Uninstalls all the settings, rolling back the output to default HDMI behaviour")
args = parser.parse_args()
isPal = args.pal

if os.geteuid() != 0:
    raise PermissionError('Excuse me, but this script must be run under root privileges.\nI appreciates it if try again using the \'sudo\' command.')
resources = os.path.join(os.getcwd(),'resources')
if args.uninstall:
    uninstall()
else:
    install()
