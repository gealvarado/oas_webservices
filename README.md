# oas_webservices

This repository provides Python sample scripts and examples for working with [Oracle Analytics Server](https://docs.oracle.com/en/middleware/bi/analytics-server/developer_guide_oas/soap-apis.html) and [Oracle Analytics Cloud](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acsdv/soap-apis.html) Web Services.  
All code uses [Zeep](https://docs.python-zeep.org/en/master/) as the SOAP client for interacting with Oracle's SOAP APIs.

---

## Contents

- **get_session.py**  
  Minimal example: Connects to Oracle Analytics, authenticates, retrieves a session ID, and logs out.  
  [Documentation → get_session.md](get_session.md)

- **get_analysis_sa.py**  
  Recursively scans a catalog path for analyses, extracts each analysis's subject area, and outputs the result to CSV.  
  [Documentation → get_analysis_sa.md](get_analysis_sa.md)

- **oas_ws.wsdl**  
  The Oracle Analytics Web Services WSDL, which can be downloaded for local inspection.

---

## Requirements

- Python 3.7+
- The `zeep` library and other dependencies listed in `requirements.txt`.

---

## Setup

Create and activate a Python virtual environment (recommended), then install dependencies:

```bash
pip install -r requirements.txt
```

---

## Downloading the WSDL

The WSDL for Oracle Analytics Web Services is available at:

```sh
http(s)://<host>:<port>/analytics-ws/saw.dll/wsdl/v12
```

To inspect the WSDL using Zeep and save to a file:

```bash
python -m zeep http(s)://<host>:<port>/analytics-ws/saw.dll/wsdl/v12 > oas_ws.wsdl 
```

---

## Example Usage

See the dedicated documentation files for each script for details, required arguments, and usage examples:

- [get_session.md](get_session.md)
- [get_analysis_sa.md](get_analysis_sa.md)

---

## Disclaimer

All code and materials in this repository are provided as samples for demonstrative purposes only.  
This repository and its contents are **not supported, maintained, or warranted by Oracle as a licensed product**.  
Use at your own risk.
