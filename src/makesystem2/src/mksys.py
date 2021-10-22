#!/usr/bin/python3

import os
import sys
import subprocess
import json
import argparse

## BASE CONSTANTS ##
SETTINGS_DIR       = "./settings" # Settings directory
SETTINGS_FILE      = SETTINGS_DIR + "/makesystem.json"    # Program settings
CPL_FILE           = SETTINGS_DIR + "/make-cpl.json"      # Building the CPL
POST_CPL_FILE      = SETTINGS_DIR + "/make-post-cpl.json" # Building the post-CPL
POST_CPL_SYSV_FILE = SETTINGS_DIR + "/make-sysvinit.json" # Building the post-CPL with sysvinit
POST_CPL_SYSD_FILE = SETTINGS_DIR + "/make-systemd.json"  # Building the port-CPL with systemd
BUILD_INSTRUCTIONS = "./packages/base"                    # Directory with packages build instructions
LOG_FILE           = "/var/log/system_building.log"       # Log file
DEFAULT_MESSAGE    = "Continue? (y/n)"                    # For dialog_msg()

## BASE FUNCTIONS ##
def log_msg(message):
    f = open(LOG_FILE, "a")
    message = message + "\n"
    for index in message:
        f.write(index)
    f.close()

# Dialog
def dialog_msg(message=DEFAULT_MESSAGE, return_code=0):
    print(message, end=" ")
    run = input()

    if run == "y" or run == "Y":
        print("Continue building...")
    elif run == "n" or run == "N":
        print("Aborted!")
        exit(return_code)
    else:
        print("Uknown input! Aborted.")
        exit(1)

# System building
def build_packages(mode="post-cpl", init="sysvinit"):
    if mode == "post-cpl":
        match init:
            case "sysvinit":
                f = open(POST_CPL_SYSV_FILE, "r")
                packageData = json.load(f)
            case "systemd":
                f = open(POST_CPL_SYSD_FILE, "r")
                packageData = json.load(f)
            default:
                print("Init choosing error!")
                exit(1)
    elif mode == "cpl":
        f = open(CPL_FILE, "r")
        packageData = json.load(f)
    else:
        print("Building mode choosing error!")
        exit(1)
    
    for package in packageData["package-sequence"]:
        if packageData["packages"][package]["multilib"] == "true":
            files = packageData["packages"][package]["multilib_build_files"]
            
        elif packageData["packages"][package]["cldirs"] == "true":
            files = packageData["packages"][package]["cldirs_build_files"]
        
        else:
            files = packageData["packages"][package]["build_files"]
        
        for build_file in files:
            run = subprocess.run(build_file, shell=True)
            
            if run == 0:
                print("Package {} build OK".format(package))
            else:
                print("Package {} build FAIL".format(package))
