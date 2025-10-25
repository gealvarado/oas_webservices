# get_analysis_sa.py Documentation

## Overview

`get_analysis_sa.py` is a utility script for Oracle Analytics/OBIEE environments.  
It connects to an Oracle Analytics web service, recursively traverses the specified catalog folder and its subfolders, identifies all analysis ("query") objects, and extracts their associated Subject Areas.  
The results are saved in a CSV file, with each row containing the path to the analysis and its Subject Area.

---

## Features

- Connects to Oracle Analytics/OBIEE using SOAP web services (zeep library).
- Authenticates via provided credentials and supports SSL.
- Recursively enumerates analyses within a specified catalog folder (default `/shared`).
- Extracts the Subject Area configured for each analysis.
- Outputs results to a CSV file (`analyses_subject_areas.csv`).

---

## Requirements

- **Python 3.7+**
- **Required Packages**:  
  - `zeep` (SOAP client)
  - `argparse`, `csv`, `xml`, `logging` (bundled with Python standard library)

Install dependencies if needed:
```sh
pip install zeep
```

---

## Usage

```sh
python get_analysis_sa.py -H <host> -P <port> -u <username> -p <password> [--ssl] [--path <catalog_path>] [--log-level <level>]
```

### Arguments

| Argument              | Required | Description                                                 |
|-----------------------|----------|-------------------------------------------------------------|
| `-H`, `--host`        | Yes      | Host address of the analytics server                        |
| `-P`, `--port`        | Yes      | Port number for the server                                  |
| `-u`, `--username`    | Yes      | Username for login                                          |
| `-p`, `--password`    | Yes      | Password for login                                          |
| `--ssl`               | No       | Use SSL for the connection (flag)                           |
| `--path`              | No       | Root folder to traverse (default: `/shared`)                |
| `--log-level`         | No       | Logging verbosity (default: `INFO`)                         |
| `--output-file`       | No.      | Output CSV filename (default: `analyses_subject_areas.csv`) |

### Example

Find all analyses under `/shared/Sales` in an Oracle Analytics instance running via SSL:

```sh
python get_analysis_sa.py -H analytics.example.com -P 9502 -u myuser -p mypass --ssl --path "/shared/Sales" --log-level DEBUG
```

---

## Output

- **CSV File:**  
  The script generates `analyses_subject_areas.csv` in the working directory.  
  Each row contains:
  - `Analysis`: Path to the analysis file in the catalog
  - `Subject Area`: The subject area used in the analysis

---

## Troubleshooting

- Ensure the host/port/credentials are correct and have sufficient permissions.
- The analytics server must be accessible from your machine.
- The `zeep` library is required (`pip install zeep`).
- You may need network/firewall access to the analytics web service endpoint.

---

## License

This script is provided "as-is" for demonstrative purposes and is NOT supported by Oracle as a licensed product.
