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
    merged_lines = ''.join(lines)
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

def install_cfg_file(config_file,new_config_file, uninstall = False):
    with open(config_file, 'r') as file:
        actual_configs = file.readlines()
    
    with open(new_config_file, 'r') as file2:
        new_configs = file2.readlines()
    
    new_configs = uninstall_cfg(actual_configs, new_configs) if uninstall else install_cfg(actual_configs, new_configs)

    write_new_file(new_configs, config_file, celebrating=True)

def install_cfg(actual_configs, new_configs) :
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
    
    return updated_config

def uninstall_cfg(actual_configs, new_configs):
    new_dict = {line.split("=", 1)[0].strip(): line for line in new_configs if "=" in line and not line.startswith("#")}

    updated_config = []

    for line in actual_configs:
        if line.startswith("#"):
            updated_config.append(line)
        elif line.split("=", 1)[0].strip() not in new_dict:
            updated_config.append(new_dict[line.split("=", 1)[0].strip()])
            new_dict.pop(line.split("=", 1)[0].strip())
    
    return updated_config


def install_boot_cfg():
    boot_cfg_file = paths['boot_cfg']['path']
    with open(boot_cfg_file, 'r') as file:
        configs = file.readlines()
    #Configurations to local array
    timings = hdmi_timings('emulationstation')

    new_configs = []
    with open(origin_path(boot_cfg_file)) as file:
        for line in file:
            new_configs.append(line.replace('%hdmi_timings%',timings))
    new_config = install_cfg(configs,new_configs)
    write_new_file(new_config, boot_cfg_file, celebrating=True)

def uninstall_boot_cfg():
    path = paths['boot_cfg']['path']
    install_cfg_file(target_path(path),origin_path(path),uninstall=True)

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
        new_config_file = os.path.join(origin_dir,platform,filename)
        config_file = os.path.join(dest_dir,platform,filename)
        if os.path.isfile(new_config_file) and os.path.isfile(config_file):
            if install:
                new_configs = define_consoledisp_config(new_config_file,platform)
                with open (config_file, 'r') as file:
                    configs = file.readlines()
                merged_configs = install_cfg(configs,new_configs)
                write_new_file(config_file,merged_configs)
            else:
                install_cfg_file(config_file,new_config_file,uninstall=True)

def install_retroarch_core_options(install = True):
    filename = paths['retroarch_core_options']['filename'] % ('-pal' if isPal else '')
    target_filename= paths['retroarch_core_options']['filename'] % ''
    path = paths['retroarch_core_options']['path']
    new_config_file = os.path.join(origin_path(path),filename)
    config_file = os.path.join(target_path(path),target_filename)
    if install:
        install_cfg_file(config_file,new_config_file)
    else:
        install_cfg_file(config_file,new_config_file,uninstall=True)

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
