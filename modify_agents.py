"""
modify_agents.py

Bulk modifies Oracle Analytics/OBIEE agents by updating run-as user and recipient information via SOAP web services.
Reads a CSV file describing agent modifications, creates optional backups, and applies all requested changes.

DISCLAIMER:
This code is distributed free for demonstrative purposes only.  
It is neither maintained nor supported by Oracle as a licensed product.

Usage:
    python modify_agents.py -H <host> -P <port> -u <username> -p <password> --input-file <path_to_csv> [--ssl] [--no-backup] [--backup-path <dir>] [--log-level <LEVEL>]

Arguments:
    -H, --host           Host address of the Oracle Analytics server
    -P, --port           Port number for the server
    -u, --username       Username for authentication
    -p, --password       Password for authentication
    --ssl                Use SSL (https)
    --input-file         CSV file with columns: path, runAs, specificRecipients, emailRecipients
    --no-backup          Do not create a backup of each agent prior to modification (default is to backup)
    --backup-path        Path for backups (default: current directory)
    --log-level          Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)

Example CSV:
    path,runAs,specificRecipients,emailRecipients
    /shared/MyAgent,myuser1,,john.doe@example.com
    /shared/OtherAgent,myadmin,alice,bob@example.com

Example:
    python modify_agents.py -H myhost.example.com -P 443 -u admin -p secret --ssl --input-file agents_changes.csv --log-level DEBUG

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
import os
import traceback

import xml.etree.ElementTree as ET

from datetime import datetime

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

# Register OAS namespaces
ET.register_namespace('saw', "com.siebel.analytics.web/report/v1.1")
ET.register_namespace('cond', "com.oracle.bi/conditions/v1")
ET.register_namespace('sawx', "com.siebel.analytics.web/expression/v1.1")

client = None

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
    global client
    oaswsdl = f"http{'s' if use_ssl else ''}://{host}:{port}/analytics-ws/saw.dll/wsdl/v12"
    logger.debug(f"WSDL URL: {oaswsdl}")
    settings = Settings(strict=False, xml_huge_tree=True)
    if client is None:
        logger.debug("Creating new Zeep client")
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

def create_backup_directory(backup_path, timestamp):
    """
    Creates the backup directory if it does not exist.

    Args:
        backup_path (str): The directory path to create.
    """
    backup_dir = os.path.join(backup_path, f"backup_{timestamp}")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    return backup_dir

def backup_agent(catalogService, sessionID, agent_path, backup_path):
    """
    Creates a backup of the specified agent (iBot) by exporting its XML to a file.

    Args:
        catalogService: The WebCatalogService SOAP proxy.
        sessionID (str): The current session ID.
        agent_path (str): The catalog path of the agent to back up.
        backup_path (str): The file path to save the backup XML.
    """
    try:
        file_path = backup_path + os.path.dirname(agent_path)
        file_name = os.path.join(file_path, os.path.basename(agent_path) + ".catalog")
        copyResult = catalogService.copyItem2(agent_path, False, True, True, False, None, None, sessionID)
        os.makedirs(file_path, exist_ok=True)
        with open(file_name, 'wb') as backup_file:
            backup_file.write(copyResult)
        logger.info(f"Backup of agent {agent_path} saved to {file_name}")
    except Exception as e:
        logger.error(f"Error backing up agent {agent_path} to {file_name}: {e}")

def getCatalogObject(catalogService, sessionID, agent_path):
    """
    Retrieves the XML definition of the specified agent (iBot).

    Args:
        catalogService: The WebCatalogService SOAP proxy.
        sessionID (str): The current session ID.
        agent_path (str): The catalog path of the agent.

    Returns:
        str: The XML string of the agent definition.
    """
    try:
        agent_object = catalogService.readObjects(agent_path, False, "ErrorCodeAndText", "ObjectAsText", sessionID)
        cat_object = agent_object[0].catalogObject
        return cat_object
    except Exception as e:
        logger.error(f"Error retrieving XML for agent {agent_path}: {e}")
        return None
    
def modify_agent(catalogService, agentService, sessionID, agent_path, runAs, specificRecipients, emailRecipients):
    """
    Modifies the specified agent (iBot) with new run-as user and recipient information.

    Args:
        agentService: The IBotService SOAP proxy.
        sessionID (str): The current session ID.
        agent_path (str): The catalog path of the agent to modify.
        runAs (str, optional): New run-as user. Defaults to None.
        specificRecipients (list, optional): List of new specific recipients. Defaults to None.
        emailRecipients (list, optional): List of new email recipients. Defaults to None.
    """
    global client 
    try:
        None  # Placeholder for modification logic
        #First, retrieve the current agent definition
        cat_object = getCatalogObject(catalogService, sessionID, agent_path)
        if cat_object is None:
            logger.error(f"Cannot modify agent {agent_path} as its XML could not be retrieved.")
            return
        # convert the XML string to an ElementTree object
        agentXML = ET.fromstring(cat_object)
        #Then, modify the XML with the new runAs, specificRecipients, and emailRecipients
        if runAs:
            dataVisibility = agentXML.find('.//{*}dataVisibility')
            if dataVisibility is not None:
                dataVisibility.set('runAs', runAs)
                dataVisibility.set('runAsGuid', runAs)
            else:
                logger.error(f"No Data Visibility found for agent {agent_path} to set runAs.")
        if specificRecipients:
            specificRecipientsElement = agentXML.find('.//{*}recipients/{*}specificRecipients')
            if specificRecipientsElement is not None:
                # Clear existing recipients
                for recipient in list(specificRecipientsElement):
                    specificRecipientsElement.remove(recipient)
                # Add new recipients
                for recipient in specificRecipients.split(','):
                    recipientElement = ET.SubElement(specificRecipientsElement, 'saw:user')
                    recipientElement.set('name', recipient.strip())
                    recipientElement.set('guid', recipient.strip())
            else:
                logger.error(f"No Specific Recipients element found for agent {agent_path} to set recipients.")
        if emailRecipients:
            emailRecipientsElement = agentXML.find('.//{*}emailRecipients')
            if emailRecipientsElement is not None:
                # Clear existing email recipients
                for recipient in list(emailRecipientsElement):
                    emailRecipientsElement.remove(recipient)
                # Add new email recipients
                for recipient in emailRecipients.split(','):
                    recipientElement = ET.SubElement(emailRecipientsElement, 'saw:emailRecipient')
                    recipientElement.set('address', recipient.strip())
                    recipientElement.set('type', 'HTML')
            else:
                logger.error(f"No Email Recipients element found for agent {agent_path} to set email recipients.")
        #Finally, update the agent
        new_catalog_object = client.get_type("ns0:CatalogObject")()
        new_catalog_object.catalogObject = (ET.tostring(agentXML, encoding='unicode'))
        agentService.writeIBot(new_catalog_object, agent_path, False, True, sessionID)
        logger.info(f"Modified agent {agent_path}) successfully.")
    except Exception as e:
        logger.error(f"Error modifying agent {agent_path}: {e}")
        traceback.print_exc()

def main(args):
    """
    Main program execution:
      - Initializes all required Oracle Analytics SOAP services
      - Logs in and obtains a session ID
      - Traverses the analytics catalog to find agent (iBot) objects
      - Optionally retrieves agent details
      - Queries agent status
      - Writes all results and details to the specified CSV file
      - Logs out and handles any exceptions

    Args:
        args (Namespace): Parsed command-line arguments.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logger.info("Starting")
    logger.debug(f"Host: {args.host}, Port: {args.port}, Username: {args.username}")
    #Initialize the session service
    session_service = initialize_service(args.host, args.port, args.ssl, "SAWSessionService")
    #Initialize the catalog service
    catalog_service = initialize_service(args.host, args.port, args.ssl, "WebCatalogService")
    #Initialize the agent service
    agent_service = initialize_service(args.host, args.port, args.ssl, "IBotService")
    # Create backup directory if needed
    if not args.no_backup:
        backup_dir = create_backup_directory(args.backup_path, timestamp)
        logger.debug(f"Backup directory created at: {backup_dir}")
    try:
        #Login and get session ID
        session_id = logon(session_service, args.username, args.password)
        logger.debug(f"Obtained Session ID: {session_id}")
        #Open the provided CSV input file and process agents
        with open(args.input_file, 'r') as file:
            agentsReader = csv.DictReader(file)
            for agent in agentsReader:
                path = agent['path']
                runAs = agent['runAs']
                specificRecipients = agent['specificRecipients']
                emailRecipients = agent['emailRecipients']
                logger.debug(f"Processing agent at path: {path} with runAs: {runAs}, specificRecipients: {specificRecipients}, emailRecipients: {emailRecipients}")
                #Backup agent if needed
                if not args.no_backup:
                    backup_path = args.backup_path
                    backup_agent(catalog_service, session_id, path, backup_dir)
                #Modify agent
                modify_agent(catalog_service, agent_service, session_id, path, runAs, specificRecipients, emailRecipients)
        #Log off 
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
    parser.add_argument("--input-file", type=str, required=False, help="Input file with list of agents to modify")
    parser.add_argument("--no-backup", required=False, action="store_true", help="Do not create backup the modified agents")
    parser.add_argument("--backup-path", type=str, required=False, help="Path to store backup of modified agents", default="./")
    parser.add_argument("--log-level", type=str, 
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], 
                        default="INFO", help="Logging level", required=False)
    args = parser.parse_args()

    logger.setLevel(getattr(logging, args.log_level))
    
    main(args)
