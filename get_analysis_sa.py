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
    Initializes and returns a Zeep SOAP service binding for a specified OBIEE/Oracle Analytics service.

    Args:
        host (str): Host address of the analytics web service.
        port (int): Port number to connect.
        use_ssl (bool): If True, uses HTTPS; otherwise HTTP.
        service (str): The SOAP service name to bind (e.g., 'WebCatalogService').

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

def get_subject_area(catalogService, sessionID, analysisPath):
    """
    Retrieves the subject area name of a specific analysis by parsing its XML.

    Args:
        catalogService: The WebCatalogService SOAP proxy.
        sessionID (str): The current session ID.
        analysisPath (str): The catalog path to the analysis.

    Returns:
        str: Name of the subject area, or 'N/A' if not found.
    """
    result = "N/A"
    analysisObject = catalogService.readObjects(analysisPath, False, "ErrorCodeAndText", "ObjectAsText", sessionID)
    analysisXML = ET.fromstring(analysisObject[0].catalogObject)
    criteria = analysisXML.find('.//{*}criteria')
    if criteria is not None and 'subjectArea' in criteria.attrib:
        result = criteria.attrib['subjectArea']
    return result

def traverse_catalog(catalogService, sessionID, folderPath):
    """
    Recursively traverses the OBIEE catalog, collecting all analysis items and their subject areas.

    Args:
        catalogService: The WebCatalogService SOAP proxy.
        sessionID (str): The current session ID.
        folderPath (str): Folder path to start traversal from.

    Returns:
        list: List of [analysis path, subject area] pairs.
    """
    analyses = []
    try:
        subItems = catalogService.getSubItems(folderPath, "*", False, None, sessionID)
        for item in subItems:
            logger.debug(f"Path: {item.path}, Type: {item.type}, Signature: {item.signature}")
            if item.type == "Folder":
                analyses += traverse_catalog(catalogService, sessionID, item.path)
            else:
                if item.signature == "queryitem1":
                    logger.info(f"Found Analysis: {item.path}")
                    analyses.append([item.path,get_subject_area(catalogService, sessionID, item.path)])
        return analyses
    except Exception as e:
        logger.error(f"Error retrieving sub-items for folder {folderPath}: {e}")


def write_to_csv(analyses, output_file):
    """
    Writes the list of analyses and their subject areas to a CSV file.

    Args:
        analyses (list): List of [analysis path, subject area] pairs.
        output_file (str): Output CSV file path.
    """
    header = ["Analysis","Subject Area"]
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(analyses)
    logger.info(f"Data written to {output_file}")   

def main(args):
    """
    Main program execution:
      - Sets up the session and catalog services
      - Logs in and obtains a session ID
      - Traverses the catalog to gather analyses
      - Writes results to CSV
      - Logs out and handles exceptions

    Args:
        args (Namespace): Parsed command-line arguments.
    """
    logger.info("Starting")
    logger.debug(f"Host: {args.host}, Port: {args.port}, Username: {args.username}")
    #Initialize the session service
    session_service = initialize_service(args.host, args.port, args.ssl, "SAWSessionService")
    #Initialize the catalog service
    catalog_service = initialize_service(args.host, args.port, args.ssl, "WebCatalogService")
    try:
        #Login and get session ID
        session_id = logon(session_service, args.username, args.password)
        logger.debug(f"Obtained Session ID: {session_id}")
        #Traverse the catalog
        analyses = traverse_catalog(catalog_service, session_id, args.path)
        logger.info(f"Found {len(analyses)} analyses.")
        #Write to CSV
        write_to_csv(analyses)
        #Log off 
        logoff(session_service, session_id)
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
    parser.add_argument("--path", type=str, required=False, default="/shared", help="Catalog path to traverse")
    parser.add_argument("--output-file", type=str, required=False, default="analyses_subject_areas.csv", help="Output filename")
    parser.add_argument("--log-level", type=str, 
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], 
                        default="INFO", help="Logging level", required=False)
    args = parser.parse_args()

    logger.setLevel(getattr(logging, args.log_level))
    
    main(args)
