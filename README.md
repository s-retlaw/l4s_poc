# l4s_poc
Log4Shell (Cve-2021-44228) Proof Of Concept

This is a personal project that runs a simple POC that will host an LDAP
server and an HTTP server for the Log4Shell exploit.  

The minimet.py will setup a stripped down meterpreter client that will call
back to the Metasploit instance passed on the command line.  This will run
the meterpreter instance in a thread in the original process that was affected
bu the Log4Shell exploit.

The LDAP server is written in Java and the HTTP server is hosted in python and
will server from a newly created wwwroot directory.  This does require java,
javc and mvn to build the exploits, and host the LDAP server.  

Python3 is also expected.
