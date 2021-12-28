import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;


public class Log4jCmdLine {
    private static final Logger logger = LogManager.getLogger(Log4jCmdLine.class);

    public static void main(String[] args) {
        System.out.println("The is used to trigger the Log4Shell exploit.  The 1st param passed in will be logged as an error.");
        //The default trusturlcodebase of the higher version JDK is false
        System.setProperty("com.sun.jndi.ldap.object.trustURLCodebase","true");
        logger.error(args[0]);
    }
}
