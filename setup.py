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
        return data.decode('utf-8').replace('hdmi_timings ','').replace('60.0','60').replace('50.0','50').replace('\n','')
    except:
        raise Exception("It's embarrassing to me, but I was unable to properly run '%s'. Sorry." %  cmd[0])

def install_cfg(orig,dest):
    if isinstance(orig,str): #Maybe orig it's the path of configuration file
        with open(orig) as file:
            config_orig = file.readlines()
    elif isinstance(orig,list): #Or maybe it's the data itself inside a list
            config_orig = orig
    else:
        raise Exception("Well, it's awkward, but feels like there's some scripting error because the kind of \"orig\" field isn't right accordingly with I expected. Sorry.\nAnyway, bye for now...")
    #This outputs something like (properties1|properties2|properties)
    properties = "(%s)" % "|".join(w.split("=")[0] for w in config_orig)
    #Now, its time to load the target file. But this time, just matter of read the path at destination variable and load the content into array, but excluding the options who should be updated
    config_dest = []
    #If the file does not exists, it creates then
    if not os.path.isfile(dest):
        open(dest,'a').close()
    with open(dest) as file:
        for line in file:
            if not re.search(properties,line):
                config_dest.append(line)
    #Now it's time to merge the two configuration arrays into one
    target =  config_dest + config_orig
    try:
        raw = open(dest,"w")
        raw.writelines(target)
        raw.close()
        print_celebrating(dest)
    except PermissionError as e:
        if e.errno == 13:
            raise PermissionError("I having a hard time with an annoying permission error trying to write the %s, witch it's very awkward, because I was supposed to be running as root and a root user does all he wants." % dest)
        else:
            raise PermissionError("It's very strange, I having some permission error trying to write the file %s for some kind I was unable to figure out witch one is. Checks out whats the exception had to say.\n%d - %s" % (dest,e.errno,e.strerror))

def install_boot_cfg():
    path = os.path.join('boot','config.txt')
    orig = os.path.join(resources,path)
    dest = os.path.join('/',path)
    #Configurations to local array
    timings = hdmi_timings('emulationstation')
    config_orig = []
    with open(orig) as file:
        for line in file:
            config_orig.append(line.replace('%hdmi_timings%',timings))
    install_cfg(config_orig,dest)

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
            raise Exception('So sad! I failed miserably installing "%s".\nSorry to dissapointing you!\nBye for now...' % orig)
    print_celebrating(" , ".join(r'%s' % w[0] if isinstance(w,list) else w for w in scripts))

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
        ['runcommand-onstart%s.sh' % '-pal' if isPal else '','runcommand-onstart.sh'],
        'runcommand-onend.sh']
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
    

def install_retroarch_cfg():
    path = os.path.join('opt','retropie','configs')
    origin_dir = os.path.join(resources,path)
    dest_dir = os.path.join('/',path)
    for platform in os.listdir(origin_dir):
        orig = os.path.join(origin_dir,platform,'retroarch.cfg')
        dest = os.path.join(dest_dir,platform,'retroarch.cfg')
        if os.path.isfile(orig):
            config_orig = define_consoledisp_config(orig,platform)
            install_cfg(config_orig,dest)

def install_retroarch_core_options():
    path = os.path.join('opt','retropie','configs','all','retroarch-core-options.cfg')
    orig = os.path.join(resources,path)
    dest = os.path.join('/',path)
    install_cfg(orig,dest)

parser = argparse.ArgumentParser(description="Setup the retropie-crt to made it work with some cheap chinese HDMI to YBpBr adapter")
parser.add_argument("--pal","-P",action='store_true',help="Apply PAL settings")
args = parser.parse_args()
isPal = args.pal

if os.geteuid() != 0:
    raise PermissionError('Excuse-me, but this script must be run under root privileges.\nI appreciate if try again using \'sudo\'.\nBye for now...')

resources = os.path.join(os.getcwd(),'resources')

print("Welcome to installation script. I'll be you host during this process. So, sit down, make a cup of tea and relax during the entire process.\n")
install_chvideo_consoledisp()
install_boot_cfg()
install_runcommand()
install_retroarch_cfg()
install_retroarch_core_options()

