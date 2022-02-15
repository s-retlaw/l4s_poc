package l4sutils;

import java.net.InetAddress;
import java.net.MalformedURLException;
import java.net.URL;

import javax.net.ServerSocketFactory;
import javax.net.SocketFactory;
import javax.net.ssl.SSLSocketFactory;

import com.unboundid.ldap.listener.InMemoryDirectoryServer;
import com.unboundid.ldap.listener.InMemoryDirectoryServerConfig;
import com.unboundid.ldap.listener.InMemoryListenerConfig;
import com.unboundid.ldap.listener.interceptor.InMemoryInterceptedSearchResult;
import com.unboundid.ldap.listener.interceptor.InMemoryOperationInterceptor;
import com.unboundid.ldap.sdk.Entry;
import com.unboundid.ldap.sdk.LDAPException;
import com.unboundid.ldap.sdk.LDAPResult;
import com.unboundid.ldap.sdk.ResultCode;


public class LDAPServer {
  private static final String LDAP_BASE = "dc=example,dc=com";

  public static void main ( String[] args ) {
    int port = 1389;
    if ( args.length < 1) {
      System.err.println(LDAPServer.class.getSimpleName() + " <codebase_url> [<port>]");
      System.exit(-1);
    }
    else if ( args.length > 1 ) {
      port = Integer.parseInt(args[ 1 ]);
    }
    run_ldap_server("0.0.0.0", port, args[0]);
 }

 public static void run_ldap_server(String ip, int port, String http_base){
    try {
      InMemoryDirectoryServerConfig config = new InMemoryDirectoryServerConfig(LDAP_BASE);
      config.setListenerConfigs(new InMemoryListenerConfig(
            "my_ldap_server",
            InetAddress.getByName(ip),
            port,
            ServerSocketFactory.getDefault(),
            SocketFactory.getDefault(),
            (SSLSocketFactory) SSLSocketFactory.getDefault()));

      config.addInMemoryOperationInterceptor(new OperationInterceptor(new URL(http_base)));
      InMemoryDirectoryServer ds = new InMemoryDirectoryServer(config);
      System.out.println("LDAP Server about to start on " + ip+ ":" + port);
      ds.startListening();

    }
    catch ( Exception e ) {
      e.printStackTrace();
    }
  }

  private static class OperationInterceptor extends InMemoryOperationInterceptor {
    private URL http_base_url;
    
    public OperationInterceptor ( URL base_url ) {
      this.http_base_url = base_url;
    }

    protected String translateName(String base){
      String name = base.substring(1);
      String[] parts = name.split(":");
      System.out.println("parts len : "+parts.length+" : "+(parts.length ==3) );
      System.out.println("parts[0] : "+parts[0]+" : "+ (parts[0] == "MM"));
      System.out.println("parts[0] : "+parts[0]+" : "+ (parts[0].equals("MM")));

      if( (parts.length == 3) && (parts[0].equals("MM")) ){
        name = parts[0]+"_"+parts[1].replace(".", "_")+"_"+parts[2];
        System.out.println("------------->the translated name is : "+name);
      }else{
        System.out.println("NOT MM -- > "+name);
      }
      return name;
    }

    @Override
    public void processSearchResult ( InMemoryInterceptedSearchResult result ) {
      String baseDN = result.getRequest().getBaseDN();
      Entry e = new Entry(baseDN);
      try {
        System.out.println("Send LDAP reference result for " + baseDN);
        e.addAttribute("javaClassName", "TheClass");
        e.addAttribute("objectClass", "javaNamingReference");
        e.addAttribute("javaCodeBase", this.http_base_url.toString()); 
        e.addAttribute("javaFactory", this.translateName(baseDN));
        result.sendSearchEntry(e);
        result.setResult(new LDAPResult(0, ResultCode.SUCCESS));
      }
      catch ( Exception ex ) {
        ex.printStackTrace();
      }
    }
  }
}
