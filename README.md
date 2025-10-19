# oas_webservices

This repository contains examples and sample code related to using [Oracle Analytics Server](https://docs.oracle.com/en/middleware/bi/analytics-server/developer_guide_oas/soap-apis.html) and [Oracle Analytics Cloud](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acsdv/soap-apis.html) Web Services using Python.

All examples utilize [Zeep](https://docs.python-zeep.org/en/master/) as the SOAP client. Please consult the Zeep documentation if you have questions about how to use this library.

First, create a Python virtual environment and then install `requirements.txt`.

```bash
pip install -r requirements.txt
```

THe WSDL for the Oracle Analytics Web Services is `http(s)://<host>:<port>/analytics-ws/saw.dll/wsdl/v12`.  Inspect the WDSL uzing Zeep, it is a good idea to save the output to a file:

```bash
python -mzeep http(s)://<host>:<port>/analytics-ws/saw.dll/wsdl/v12 > oas_ws.wsdl 
```

## Disclaimer

All code and materials in this repository are provided as samples for demonstrative purposes only.  
This repository and its contents are **not supported, maintained, or warranted by Oracle as a licensed product**.  
Use at your own risk.
