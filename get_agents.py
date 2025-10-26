##
## DISCLAIMER:
## This code is distributed free for demonstrative purposes only.  
## It is neither maintained nor supported by Oracle as a licensed product.
##

import argparse
import csv
import logging
import xml.etree.ElementTree as ET

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

def traverse_catalog(catalogService, sessionID, folderPath="/shared"):
    """
    Recursively traverses the OBIEE catalog, collecting all agent (iBot) items.

    Args:
        catalogService: The WebCatalogService SOAP proxy.
        sessionID (str): The current session ID.
        folderPath (str): Folder path to start traversal from.

    Returns:
        list: List of agent (iBot) catalog paths.
    """
    agents = []
    try:
        subItems = catalogService.getSubItems(folderPath, "*", False, None, sessionID)
        for item in subItems:
            logger.debug(f"Path: {item.path}, Type: {item.type}, Signature: {item.signature}")
            if item.type == "Folder":
                agents += traverse_catalog(catalogService, sessionID, item.path)
            else:
                if item.signature == "coibot1":
                    logger.info(f"Found Agent: {item.path}")
                    agents.append(item.path)
        return agents
    except Exception as e:
        logger.error(f"Error retrieving sub-items for folder {folderPath}: {e}")

def get_agents_status(agentService, sessionID, agents):
    """
    Retrieves the status for each agent (iBot) in the provided list.

    Args:
        agentService: The IBotService SOAP proxy.
        sessionID (str): The current session ID.
        agents (list): List of agent catalog paths.

    Returns:
        dict: Mapping of agent path to status details returned by IBotService.
    """
    agent_details = {}
    for agent_path in agents:
        try:
            agent_status = agentService.getIBotStatus(agent_path, sessionID)
            agent_details[agent_path] = agent_status
        except Exception as e:
            logger.error(f"Error retrieving info for agent {agent_path}: {e}")
    return agent_details

def get_agents_details(catalogService, sessionID, agents):
    """
    Retrieves additional details from the XML of each agent (iBot), such as run-as user and recipient information.

    Args:
        catalogService: The WebCatalogService SOAP proxy.
        sessionID (str): The current session ID.
        agents (list): List of agent catalog paths.

    Returns:
        dict: Mapping of agent path to a details dictionary
              (including runAs, specificRecipients, emailRecipients, if found).
    """
    agent_details = {}
    for agent_path in agents:
        try:
            agentObject = catalogService.readObjects(agent_path, False, "ErrorCodeAndText", "ObjectAsText", sessionID)
            agentXML = ET.fromstring(agentObject[0].catalogObject)
            logger.debug(f"XML for agent {agent_path}: {ET.tostring(agentXML, encoding='unicode')}")
            dataVisibility = agentXML.find('.//{*}dataVisibility')
            if dataVisibility is not None:
                agent_details[agent_path] = {"runAs": dataVisibility.get('runAs')}
            else:
                logger.error(f"No Data Visibility found for agent {agent_path}")
            # Get specific recipients
            specific_recipients = agentXML.find('.//{*}recipients/{*}specificRecipients')
            recipient_list = []
            if specific_recipients is not None:
                for recipient in specific_recipients:
                    recipient_list.append(recipient.get('name'))
            agent_details[agent_path]["specificRecipients"] = ",".join(recipient_list) if len(recipient_list) > 0 else ""
            # Get email recipients
            email_recipients = agentXML.find('.//{*}emailRecipients')
            recipient_list = []
            if email_recipients is not None:
                for recipient in email_recipients:
                    recipient_list.append(recipient.get('address'))
            agent_details[agent_path]["emailRecipients"] = ",".join(recipient_list) if len(recipient_list) > 0 else ""
        except Exception as e:
            logger.error(f"Error retrieving XML for ssssagent {agent_path}: {e}")
    return agent_details

def write_status_to_csv(agent_status, agent_details, output_file):
    """
    Writes agent status and details information to a CSV file.

    Args:
        agent_status (dict): Map of agent path to status details.
        agent_details (dict): Map of agent path to additional details, such as recipients.
        output_file (str): Path to the CSV output file.
    """
    with open(output_file, mode='w', newline='') as file:
        columns = ['path','lastRun','nextRun','lastRunStatus','priority','agentEnabled','subscribed','specificRecipient']
        if len(agent_details) > 0:
            columns.extend(['runAs','specificRecipients', 'emailRecipients'])
        writer = csv.writer(file)
        writer.writerow(columns)
        for agent_path, status in agent_status.items():
            row = [agent_path, status.lastRun, status.nextRun, status.lastRunStatus, status.priority, status.agentEnabled, status.subscribed, status.specificRecipient ]
            if agent_path in agent_details:
                row.append(agent_details[agent_path]["runAs"])
                row.append(agent_details[agent_path]["specificRecipients"])
                row.append(agent_details[agent_path]["emailRecipients"])
            writer.writerow(row)
    logger.info(f"Agent status written to {output_file}")

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
    logger.info("Starting")
    logger.debug(f"Host: {args.host}, Port: {args.port}, Username: {args.username}")
    #Initialize the session service
    session_service = initialize_service(args.host, args.port, args.ssl, "SAWSessionService")
    #Initialize the catalog service
    catalog_service = initialize_service(args.host, args.port, args.ssl, "WebCatalogService")
    #Initialize the agent service
    agent_service = initialize_service(args.host, args.port, args.ssl, "IBotService")
    try:
        #Login and get session ID
        session_id = logon(session_service, args.username, args.password)
        logger.debug(f"Obtained Session ID: {session_id}")
        #Traverse the catalog
        agents = traverse_catalog(catalog_service, session_id, args.path)
        logger.info(f"Total Agents Found: {len(agents)}")
        logger.debug(f"Agents: {agents}")
        #Get agent details
        agents_status = get_agents_status(agent_service, session_id, agents)
        logger.debug(f"Agents Status: {agents_status}")
        # Get agent details (if needed)
        agents_details = {}
        if args.details:
            agents_details = get_agents_details(catalog_service, session_id, agents)
        logger.debug(f"Agents Details: {agents_details}")
        # agents_xml = get_agents_xml(catalog_service, session_id, agents)
        #Write to CSV
        write_status_to_csv(agents_status, agents_details, output_file=args.output_file)
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
    parser.add_argument("--path", type=str, default="/shared", help="Catalog path to traverse", required=False)
    parser.add_argument("--details", action="store_true", help="Include runas, specificRecipients, and emailRecipients", required=False)
    parser.add_argument("--output-file", type=str, default="agents_status.csv", help="Output CSV file", required=False)
    parser.add_argument("--log-level", type=str, 
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], 
                        default="INFO", help="Logging level", required=False)
    args = parser.parse_args()

    logger.setLevel(getattr(logging, args.log_level))
    
    main(args)
