#!/usr/bin/python3
# Скрипт для автоматизации сборки системы
# (C) 2021 Михаил Краснов <linuxoid85@gmail.com>
# Для Calmira LX4 1.1 GNU/Linux
# Версия: print(VERSION)

## TODOS ##
# TODO - Add build time analysis and redirect messages to the log for all build scripts

## Imports ##
import os
import sys
import json
import subprocess

## Base constants ##
VERSION = "0.2"
JSON_FILE = "/etc/makesystem.json"
BuildInstructions = "/usr/src/packages/" # Files with build instructions
LogDir = "/var/log/system_building/packages"
LogFile = "/var/log/system_building/system_building.log"

default_message = "Continue? (y/n) "

## Base functions ##
# Заголовок
def header_msg(message):
    print("\033[1m{}\033[0m".format(message))

# Отправка сообщений в лог
def log_msg(message):   
    f = open(LogFile, 'a')
    message = message + "\n"
    for index in message:
        f.write(index)
    f.write('\n')
    f.close()

# Диалог с пользователем
def dialog_msg(message=default_message, return_code=0):
    print(message, end="")
    run = input()
    
    if run == "y" or run == "Y":
        print("Продолжается сборка...")
    elif run == "n" or run == "N":
        print("Сборка прервана!")
        exit(return_code)
    else:
        print("НЕПРАВИЛЬНОЕ ЗНАЧЕНИЕ ({}). Аварийное завершение работы.".format(run))


## Script body ##

# Check root
GID = os.getgid()
if GID != 0:
    print("\033[31mERROR: you must run this script on root! \033[0m")
    exit(1)

# Check sys.argv[1]
if sys.argv[1] != "systemd" or sys.argv[1] != "sysvinit" or sys.argv[1] != "cpl":
    print("Uknown build mode {}!".format(sys.argv[1]))
    exit(1)

if sys.argv[1] == "cpl":
    cpl_build = True

# Check log dir
if os.path.isdir(LogDir):
    pass
else:
    print("Create directory {}...".format(LogDir))
    os.makedirs(LogDir)

header_msg("Start base system building")
log_msg("START SYSTEM BUILDING")

if os.path.isfile(JSON_FILE):
    pass
else:
    print("Error: file {} not found".format(JSON_FILE))
    exit(1)

with open(JSON_FILE) as f:
    fileData = json.load(f)

# Проверка на существование файлов
errorPkgs = 0
for File in fileData["files"]:
    PackageFile = BuildInstructions + File

    print("Testing file {}...".format(PackageFile), end = " ")
    if os.path.isfile(PackageFile):
        print("\033[32mok\033[0m")
    else:
        print("\033[31mFAIL\033[0m")
        errorPkgs += 1

if errorPkgs > 0:
    print("No {} build scripts found!".format(errorPkgs))
    sys.exit(1)
    
"""
Building a system.

The required script with assembly instructions is launched.

If it returned 0, then the build was successful. If it returned a value
other than zero, then a warning about incorrect building is displayed.

Usage:

`build_package(mode)` - for building base system;
`build_package(init="init")` - for building system init.

Inits:
- sysvinit;
- systemd.
"""
def build_package(mode, init="sysvinit"):
    if mode == "system":
        build_files = fileData["packages"]
        
    elif mode == "init":
        if init == "sysvinit":
            build_files = fileData["systemv-packages"]
            
        elif init == "systemd":
            build_files = fileData["systemd-packages"]
            
        else:
            print("Uknown init system {} for building!".format(init))
            exit(1)
    
    elif mode == "cpl":
        build_files = fileData["cpl-system"]

    else:
        print("Uknown mode for 'build_package()'!")
        exit(1)
            
    for file in build_files:
        print("\033[35mBuilding package\033[0m {}...".format(file))
        
        PackageFile = BuildInstructions + file + "2>&1 | tee " + LogDir + "/" + file
        log_message = "Build package " + file
        
        log_msg(log_message)
        
        result = subprocess.run(PackageFile, shell = True)
        if result.returncode == 0:
            print("\033[1mPackage {} returned 0, which means the build is probally seccessful.".format(file))
        else:
            print("\033[1mPackage {0} returned {1}, which means the assembly is probably WRONG!".format(file, result.returncode))
            dialog_msg(return_code=1)

# Building base system
if cpl_build == True:
    build_package("cpl")
else:
    build_package("system")

# Building system init
build_package("init", init = sys.argv[1])

print("************************************")
print("**** Base system build complete ****")
print("************************************")