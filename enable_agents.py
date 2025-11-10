"""
enable_agents.py

Enables or disables Oracle Analytics (OBIEE) agents in bulk via SOAP web services. 
Reads a CSV listing agent paths and desired enable/disable states, then performs 
the specified action for each agent using Oracle Analytics SOAP APIs.

DISCLAIMER:
This code is distributed free for demonstrative purposes only.  
It is neither maintained nor supported by Oracle as a licensed product.

Usage:
    python enable_agents.py -H <host> -P <port> -u <username> -p <password> --input-file <path_to_csv> [--ssl] [--log-level <LEVEL>]

Arguments:
    -H, --host           Host address of the Oracle Analytics server
    -P, --port           Port number for the server
    -u, --username       Username for authentication
    -p, --password       Password for authentication
    --ssl                Use SSL (https)
    --input-file         CSV file listing agent 'path' and 'agentEnabled' columns
    --log-level          Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)

Example CSV:
    path,agentEnabled
    /shared/MyAgent,True
    /shared/OtherAgent,False

Example:
    python enable_agents.py -H myhost.example.com -P 443 -u admin -p secret --ssl --input-file agents_status.csv

Requires:
    - Python 3.x
    - zeep
"""
## DISCLAIMER:
## This code is distributed free for demonstrative purposes only.  
## It is neither maintained nor supported by Oracle as a licensed product.
##

import argparse
import csv
import logging
import xml.etree.ElementTree as ET

from zeep import Client, Settings

# Set up basic logger for output and error tracking
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def initialize_service(host, port, use_ssl, service):
    """
    Initializes and returns a Zeep SOAP service binding for Oracle Analytics.

    Args:
        host (str): Host address of the analytics server.
        port (int): Port number for the server.
        use_ssl (bool): If True, use HTTPS; otherwise HTTP.
        service (str): Name of the SOAP service to bind.

    Returns:
        zeep.proxy.OperationProxy: The bound SOAP service object.
    """
    oaswsdl = f"http{'s' if use_ssl else ''}://{host}:{port}/analytics-ws/saw.dll/wsdl/v12"
    logger.debug(f"WSDL URL: {oaswsdl}")
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(oaswsdl, settings=settings)    
    service = client.bind(service, f"{service}Soap")
    return service 

def logon(sessionService,username,password):
    """
    Logs in to the session service and retrieves a session ID.

    Args:
        sessionService: The SAWSessionService SOAP proxy.
        username (str): Username credential.
        password (str): Password credential.

    Returns:
        str: The session ID string.
    """
    sessionID = sessionService.logon(username,password)
    return sessionID

def logoff(sessionService, sessionID):
    """
    Logs out from the OBIEE/Oracle Analytics session.

    Args:
        sessionService: The SAWSessionService SOAP proxy.
        sessionID (str): The session ID to terminate.
    """
    sessionID = sessionService.logoff(sessionID)

def process_agent(agentService, sessionID, path, enable):
    """
    Enables or disables an agent based on the provided path.

    Args:
        agentService: The IBotService SOAP proxy.
        sessionID (str): The session ID for authentication.
        path (str): The path of the agent to process.
        enable (bool): If True, enable the agent; if False, disable it.
    """
    try:
        logger.info("{}abling agent at path: {}".format("En" if enable else "Dis", path))
        result = agentService.enableIBot(path, enable, sessionID)
        logger.debug(f"Result: {result}")
    except Exception as e:
        logger.error(f"Error processing agent at path {path}: {type(e)} - {e}")

def main(args):
    """Main routine to process agent enabling/disabling actions."""
    logger.info("Starting")
    logger.debug(f"Host: {args.host}, Port: {args.port}, Username: {args.username}")

    # Initialize required SOAP services
    session_service = initialize_service(args.host, args.port, args.ssl, "SAWSessionService")
    agent_service = initialize_service(args.host, args.port, args.ssl, "IBotService")
    try:
        # Login and get session ID
        session_id = logon(session_service, args.username, args.password)
        logger.debug(f"Obtained Session ID: {session_id}")

        # Open the provided CSV input file and process agents
        with open(args.input_file, 'r') as file:
            agentsReader = csv.DictReader(file)
            for agent in agentsReader:
                agent_path = agent['path']
                enable_flag = agent['agentEnabled'].strip().lower() == 'true'
                process_agent(agent_service, session_id, agent_path, enable_flag)

        # Log off (end session)
        logoff(session_service, session_id)
    except Exception as e:
        logger.error(f"An error occurred: {type(e)} - {e}")
    logger.info("Completed")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", type=str, required=True, help="Host address")
    parser.add_argument("-P", "--port", type=int, required=True, help="Port number")
    parser.add_argument("-u", "--username", type=str, required=True, help="Username")
    parser.add_argument("-p", "--password", type=str, required=True, help="Password")
    parser.add_argument("--ssl", required=False, action="store_true", help="Use SSL for connection")
    parser.add_argument("--input-file", type=str, required=True, help="Input file with list of agents to process")
    parser.add_argument("--log-level", type=str, 
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], 
                        default="INFO", help="Logging level", required=False)
    args = parser.parse_args()

    logger.setLevel(getattr(logging, args.log_level))
    
    main(args)
