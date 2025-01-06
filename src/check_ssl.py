import socket
import ssl
import datetime

def check_ssl():
    hostname = 'folk2folk.com'
    port = 443
    
    try:
        # Try to get IP
        ip = socket.gethostbyname(hostname)
        print(f"IP address: {ip}")
        
        # Create SSL context
        context = ssl.create_default_context()
        
        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                print(f"\nSSL Version: {ssock.version()}")
                cert = ssock.getpeercert()
                
                # Print certificate details
                print("\nCertificate Details:")
                print(f"Subject: {dict(x[0] for x in cert['subject'])}")
                print(f"Issuer: {dict(x[0] for x in cert['issuer'])}")
                print(f"Valid from: {cert['notBefore']}")
                print(f"Valid until: {cert['notAfter']}")
                
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    check_ssl() 