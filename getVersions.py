#!/bin/python3

import requests
import json
import time
from lxml import html
import os
from packaging import version
import datetime
import subprocess

current_utc = datetime.datetime.utcnow()
current_utc = current_utc.strftime("%B %d %Y %H:%M UTC")

# Go through and get versions
with open('list.json') as f:
  data = json.load(f)

snap_version = ""
flat_version = ""
ubuntu_version = ""
#debian_version = ""
#mint_version = ""
fedora_version = ""
latest_version = ""

check = 0 
red = "![#red](https://via.placeholder.com/15/f03c15/000000?text=+)"
green = "![#green](https://via.placeholder.com/15/00ff00/000000?text=+)"

####################
# GET SNAP VERSION #
####################

def getSnap(key):
    global snap_version
    try:
        response = requests.get('https://snapcraft.io/'+key)
        tree = html.fromstring(response.content)
        dev = tree.xpath("//*[contains(@class, 'p-tooltip--top-center')]/text()")[0].strip()
        snap_version = tree.xpath("//*[contains(@class, 'p-button--neutral p-snap-install-buttons__versions')]/text()")[0].strip().split(" ")[1]
        #ERROR HANDLING
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6

#######################
# GET FLATPAK VERSION #
#######################

def getFlat(key):
    global flat_version
    try:
        response = requests.get('https://flathub.org/api/v1/apps/'+key)
        r = json.loads(response.text)
        flat_version = r['currentReleaseVersion']
        #ERROR HANDLING
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6

###################
# GET APT VERSION #
###################

def getAPT(key):
    global ubuntu_version
    global debian_version
    global mint_version
    global fedora_version
    global latest_version

    try:
        response = requests.get('https://repology.org/project/'+key+'/versions')
        tree = html.fromstring(response.content)
        try: ubuntu_version = tree.xpath("//*[contains(@id, 'ubuntu_20_04')]/td[3]/span/a/text()")[0] #Ubuntu 20.04
        except:
            try: ubuntu_version = tree.xpath("//*[contains(@id, 'ubuntu_20_04')]/td[3]/span/text()")[0] #Ubuntu 20.04
            except: ubuntu_version = ""

        #try: debian_version = tree.xpath("//*[contains(@id, 'debian_unstable')]/td[3]/span/a/text()")[0] #Debian Stable
        #except: 
        #    try: debian_version = tree.xpath("//*[contains(@id, 'debian_unstable')]/td[3]/span/text()")[0] #Debian Stable
        #    except: debian_version = ""

        #try: mint_version = tree.xpath("//*[contains(@id, 'linux_mint_19_3')]/td[3]/span/a/text()")[0] #Linux Mint 19.3
        #except: 
        #    try: mint_version = tree.xpath("//*[contains(@id, 'linux_mint_19_3')]/td[3]/span/text()")[0] #Linux Mint 19.3
        #    except: mint_version = ""
            
        try: fedora_version = tree.xpath("//*[contains(@id, 'fedora_32')]/td[3]/span/a/text()")[0] #Fedora 32
        except: 
            try: fedora_version = tree.xpath("//*[contains(@id, 'fedora_32')]/td[3]/span/text()")[0] #Fedora 32
            except: fedora_version = ""
        #ERROR HANDLING
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6

    #GET LATEST VERSION
    try:
        response = requests.get('https://repology.org/project/'+key+'/information')
        tree = html.fromstring(response.content)
        latest_version = tree.xpath("//*[contains(@class, 'version version-big version-newest')]/text()")[0]
        #ERROR HANDLING
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6

################
# FIX VERSIONS #
################

def fix(version):
    version=version.split('-')[0]
    version=version.split('+')[0]
    dotcount = version.count(".")
    if(dotcount>2):
        version=version.split('.')
        version=version[0]+"."+version[1]+"."+version[2]
    for letter in 'abcdefghijklmnopqrstuvwxyz':
        version = version.replace(letter, '')
    return version

#################
# MAIN FUNCTION #
#################
try: os.remove("index.md");
except: print("No file")
f = open('index.md','a')
#f.write('## Linux Software Version Check - Across Snap, Flatpak, Apt\n')
f.write('### Last Checked: '+str(current_utc)+" (Updated Every 6 Hours)\n\n")

f.write('|Software|Snap|Flatpak|Ubuntu|Fedora|Latest\n')
f.write('|:-------------|:-------------|:-------------|:-------------|:-------------|:-------------|\n')
# Loop through json
for key in data.keys():
    print(" | "+key, end="", flush=True)
    if(data[key]['Snap']!=""): getSnap(data[key]['Snap']); snap_version = fix(snap_version); # Snap Function
    if(data[key]['Flatpak']!=""): getFlat(data[key]['Flatpak']); flat_version = fix(flat_version); #Flatpak Function

    # APT Function
    if(data[key]['APT']!=""):
        getAPT(data[key]['APT'])
        ubuntu_version = fix(ubuntu_version)
        fedora_version = fix(fedora_version)
        latest_version = fix(latest_version)

    # Write to file
    f.write("|"+data[key]['IMG']+" "+key+"|")
    if(data[key]['Snap']!=""):
        if(version.parse(snap_version) < version.parse(latest_version)): f.write(red+" "+snap_version);
        else: f.write(green+" "+snap_version);
    f.write("|")
    if(data[key]['Flatpak']!=""): 
        if(version.parse(flat_version) < version.parse(latest_version)): f.write(red+" "+flat_version);
        else: f.write(green+" "+flat_version);
    f.write("|")
    if(data[key]['APT']!=""):
        print(ubuntu_version+" / "+fedora_version+" / "+latest_version)
        if(ubuntu_version!=""):
            if(version.parse(ubuntu_version) < version.parse(latest_version)): ubuntu_version_output = red+" "+ubuntu_version;
            else: ubuntu_version_output = green+" "+ubuntu_version;
        if(fedora_version!=""):
            if(version.parse(fedora_version) < version.parse(latest_version)): fedora_version_output = red+" "+fedora_version;
            else: fedora_version_output = green+" "+fedora_version;
        f.write(str(ubuntu_version_output)+"|"+str(fedora_version_output)+"|![#green](https://via.placeholder.com/15/00ff00/000000?text=+) "+str(latest_version)+"|")
    
    ubuntu_version=""
    fedora_version=""
    ubuntu_version_output=""
    fedora_version_output="" 

    print("")
    f.write('\n')

f.write('\n#### Notes\n')
f.write("- Based on stable versions\n")
f.write("- Outdated doesn't necessarily mean vulnerable software\n")
f.write("- Add request in github for another software or distro\n")
f.write("\n#### Sources\n")
f.write("- https://repology.org - Fedora 32, Ubuntu 20.04, Latest Stable Versions Repo\n")
f.write("- https://snapcraft.io - Snap Versions\n")
f.write("- https://flathub.org - Flatpak Verisons\n")
