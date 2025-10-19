import argparse
import logging

from zeep import Client,Settings

# Create the logger object
logger = logging.getLogger(__name__)

# Set the logging level
logger.setLevel(logging.INFO)

# Create console handler and set level to info
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Create formatter, add it to the console handler, and add the handler to logger
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def initialize_service(host, port, use_ssl, service):
    oaswsdl = f"http{'s' if use_ssl else ''}://{host}:{port}/analytics-ws/saw.dll/wsdl/v12"
    logger.debug(f"WSDL URL: {oaswsdl}")
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(oaswsdl, settings=settings)    
    service = client.bind(service, f"{service}Soap")
    return service 
                          
def main(args):
    logger.info("Starting")
    logger.debug(f"Host: {args.host}, Port: {args.port}, Username: {args.username}")
    #Initialize the session service
    session_service = initialize_service(args.host, args.port, args.ssl, "SAWSessionService")
    try:
        #Login and get session ID
        session_id = session_service.logon(name=args.username, password=args.password)
        logger.info(f"Session ID: {session_id}")
        #Log off 
        session_service.logoff(sessionID=session_id)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    logger.info("Completed")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", type=str, required=True, help="Host address")
    parser.add_argument("-P", "--port", type=int, required=True, help="Port number")
    parser.add_argument("-u", "--username", type=str, required=True, help="Username")
    parser.add_argument("-p", "--password", type=str, required=True, help="Password")
    parser.add_argument("--ssl", required=False, action="store_true", help="Use SSL for connection")
    parser.add_argument("--log-level", type=str, 
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], 
                        default="INFO", help="Logging level", required=False)
    args = parser.parse_args()

    logger.setLevel(getattr(logging, args.log_level))
    
    main(args)
