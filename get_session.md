# get_session.py

This is the simplest use case, it only connects to the Oracle Analytics Server gets a session and then closes it.

The service is initialized by the `initialize_service` function:

```python
...
from zeep import Client,Settings
...
def initialize_service(host, port, use_ssl, service):
    oaswsdl = f"http{'s' if use_ssl else ''}://{host}:{port}/analytics-ws/saw.dll/wsdl/v12"
    logger.debug(f"WSDL URL: {oaswsdl}")
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(oaswsdl, settings=settings)    
    service = client.bind(service, f"{service}Soap")
    return service 
```

The bind function is used because the OA WSDL provides multiple services, all of them with this:

```xml
<wsdl:service xmlns:xmime="http://www.w3.org/2005/05/xmlmime" name="<servicename>">
    <wsdl:port binding="sawsoap:<servicename>" name="<servicename>Soap">
        <soap:address location="http://<host>:<port>/analytics-ws/saw.dll?SoapImpl=<servicename>"/>
    </wsdl:port>
</wsdl:service>
```
