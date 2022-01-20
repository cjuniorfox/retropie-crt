#!/usr/bin/python3
import json, subprocess, os, re, shutil, sys,random, argparse
from subprocess import PIPE,Popen

sys.tracebacklimit = 0

def print_celebrating(award):
    #ANSI Color escape code at https://media.geeksforgeeks.org/wp-content/uploads/20201223013003/colorsandformattingsh.png
    coloredaward = '\33[1;49;92m"%s"\33[0m' % award
    celebs=[\
        'The %s was installed.',
        'Wow! The %s was installed successfully.',
        'Conquered the installation of %s like a champ!',
        'Impressed with myself installing the %s at so graceful way.',
        'Other scripts might be jealous, because I installed %s wonderfully well.',
        'Proud to say that the %s was installed successfully!',
        'Happened to have installed the %s at so graceful way that was made me fells proud of myself.',
        'Guess what! I made it again when I was installing the %s.',
        'Don\'t worry. I made it again, I was successful when I was installing the %s.',
        'I\'m in paradise, because I installed %s well.']
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
    except:
        raise Exception("It's embarrassing to me, but I was unable to properly run '%s'. Sorry." %  cmd[0])

def write_new_file(lines,path,celebrating=True):
    try:
        raw = open(path,"w")
        raw.writelines(lines)
        raw.close()
        if celebrating :
            print_celebrating(path)
    except PermissionError as e:
        if e.errno == 13:
            raise PermissionError('I having a hard time with an annoying permission error trying to write the \33[1;49;31m"%s"\33[0m., witch it\'s very awkward, because I was supposed to be running as root and a root user does all he wants.' % path)
        else:
            raise PermissionError('It\'s very strange, I having some permission error trying to write the file \33[1;49;31m"%s"\33[0m. for some kind I was unable to figure out witch one is. Checks out whats the exception had to say.\n%d - %s' % (path,e.errno,e.strerror))

def install_cfg(config,target_path):
    if isinstance(config,str): #Maybe orig it's the path of configuration file
        with open(config) as file:
            new_config = file.readlines()
    elif isinstance(config,list): #Or maybe it's the data itself inside a list
            new_config = config
    else:
        raise Exception("Well, it's awkward, but feels like there's some scripting error because the kind of \"orig\" field isn't right accordingly with I expected. Sorry.\nAnyway, bye for now...")
    #This outputs something like (properties1|properties2|properties)
    properties = "(%s)" % "|".join(w.split("=")[0] for w in new_config)
    #Now, its time to load the target file. But this time, just matter of read the path at destination variable and load the content into array, but excluding the options who should be updated
    target = []
    i = 0
    #If the file does not exists, it creates then
    if not os.path.isfile(target_path):
        open(target_path,'a').close()
    with open(target_path) as file:
        for line in file:
            if not re.search(properties,line):
                target.append(line)
            elif i < len(new_config): #Try to add the same setting at same place as the one left of
                target.append(new_config[i])
                i+=1
    #If all desired settings were not applyed yet, fill the rest of file with remaining settings
    while i < len(new_config):
        target.append(new_config[i])
        i+=1
    #Now it's time to merge the two configuration arrays into one
    write_new_file(target,target_path)
    
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
    path = os.path.join('boot','config.txt')
    config_path = os.path.join(resources,path)
    target_path = os.path.join('/',path)
    #Configurations to local array
    timings = hdmi_timings('emulationstation')
    config = []
    with open(config_path) as file:
        for line in file:
            config.append(line.replace('%hdmi_timings%',timings))
    install_cfg(config,target_path)

def uninstall_boot_cfg():
    path = os.path.join('boot','config.txt')
    config_path = os.path.join(resources,path)
    target_path = os.path.join('/',path)
    uninstall_cfg(config_path,target_path)

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
            print_celebrating(dest)
        except:
            raise Exception('So sad! I failed miserably installing \33[1;49;31m"%s"\33[0m.\nSorry to dissapointing you!\nBye for now...' % orig)
    print_celebrating(" , ".join(r'%s' % w[0] if isinstance(w,list) else w for w in scripts))

def uninstall_scripts():
    script_list = [
            {
                'path':os.path.join('/','usr','bin'),
                'filenames' : ['chvideo','consoledisp']
            },
            {
                'path':os.path.join('/','opt','retropie','configs','all'),
                'filenames' : ['runcommand-onstart.sh','runcommand-onend.sh']
            }
        ]
    
    for scripts in script_list:
        for filename in scripts['filenames']:
            try:
                path = os.path.join(scripts['path'],filename)
                os.remove(path)
                print('File: \33[1;49;92m"%s"\33[0m uninstalled.' % path)
            except Exception as e:
                print('Error removing the file \33[1;49;31m"%s"\33[0m. %s' % (path,e.strerror))


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
    scripts = [
        ['runcommand-onstart%s.sh' % ('-pal' if isPal else ''),'runcommand-onstart.sh'],
        'runcommand-onend.sh'
    ]
    path = os.path.join('opt','retropie','configs','all')
    origin_path = os.path.join(resources,path)
    dest_path = os.path.join('/',path)
    install_scripts(scripts,origin_path, dest_path)

def get_platform_parameters(platform):
    arguments = ['consoledisp',platform,'-i','-j']
    if(isPal): #If it's PAL, setup as is
        arguments.append('-P')
    try:
        proc = subprocess.Popen(arguments,stdout=PIPE)
        proc.wait()
        data, _ = proc.communicate()
        if proc.returncode is 0:
            jsondata = data.decode('utf-8')
            scandata = json.loads(jsondata)
            return (str(scandata['x_resolution']),str(scandata['y_resolution']),str(scandata['vertical']['fps']))
    except:
        raise Exception("Unfortunely I was unable properly to obtain parameters for the platform " + platform)

def define_consoledisp_config(origin_cfg_path,platform):
    x,y,fps = get_platform_parameters(platform)
    config_file = []
    with open(origin_cfg_path) as file:
        for line in file:
            config_file.append(line.replace('%x_resolution%',x).replace('%y_resolution%',y).replace('%refresh%',fps))
    return config_file
    

def install_retroarch_cfg(install = True):
    path = os.path.join('opt','retropie','configs')
    origin_dir = os.path.join(resources,path)
    dest_dir = os.path.join('/',path)
    for platform in os.listdir(origin_dir):
        config_path = os.path.join(origin_dir,platform,'retroarch.cfg')
        target_path = os.path.join(dest_dir,platform,'retroarch.cfg')
        if os.path.isfile(config_path):
            if install:
                config_orig = define_consoledisp_config(config_path,platform)
                install_cfg(config_orig,target_path)
            else:
                uninstall_cfg(config_path,target_path)

def install_retroarch_core_options(install = True):
    path = os.path.join('opt','retropie','configs','all')
    config_filename = 'retroarch-core-options%s.cfg' % ('-pal' if isPal else '')
    target_filename = 'retroarch-core-options.cfg'
    config_path = os.path.join(resources,path,config_filename)
    target_path = os.path.join('/',path,target_filename)
    if install:
        install_cfg(config_path,target_path)
    else:
        uninstall_cfg(config_path,target_path)

def install():
    print("Welcome to installation script. I'll be you host during this process. So, sit down, make a cup of tea and relax during the entire process.\n")
    install_chvideo_consoledisp()
    install_boot_cfg()
    install_runcommand()
    install_retroarch_cfg()
    install_retroarch_core_options()
    print("\nI finalized all steps needed to configure your Raspberry to work with CRT displays over HDMI. It's recommended turn off you Raspberry and plug then at your CRT display. Enjoy your emulator like you're playining at the original hardware.\n That's all. See ya")

def uninstall():
    print("Starting the uninstallation process.")
    install_retroarch_core_options(False)
    install_retroarch_cfg(False)
    uninstall_boot_cfg()
    uninstall_scripts()
    print("All settings were removed and your HDMI output it's now back to default settings. It's higly recommended turn off your Raspberry and disconnect it from your CRT display with risk of harm the deflection circuitry of your television set or monitor if you don't.")

parser = argparse.ArgumentParser(description="Setup the retropie-crt to made it work with some cheap chinese HDMI to YBpBr adapter")
parser.add_argument("--pal","-P",action='store_true',help="Apply PAL settings")
parser.add_argument("--uninstall",'-u', action='store_true',help="Uninstalls the settings rolling back the output default HDMI behavior")
args = parser.parse_args()
isPal = args.pal

if os.geteuid() != 0:
    raise PermissionError('Excuse-me, but this script must be run under root privileges.\nI appreciate if try again using \'sudo\'.\nBye for now...')
resources = os.path.join(os.getcwd(),'resources')
if args.uninstall:
    uninstall()
else:
    install()