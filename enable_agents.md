# enable_agents.py Documentation

## Overview

`enable_agents.py` is a utility script for Oracle Analytics/OBIEE environments.
It connects to the Oracle Analytics server using SOAP web services, reads a list of agent (iBot) objects and their desired enabled/disabled state from a CSV file, and enables or disables each agent accordingly.

---

## Features

- Connects to Oracle Analytics/OBIEE using SOAP web services (Zeep Python client).
- Authenticates via username and password (supports SSL).
- Processes a CSV file listing agent paths and desired enabled/disabled state.
- Enables or disables agents in bulk.
- Logs progress, errors, and results to the console.
- Supports adjustable logging verbosity.

---

## Requirements

- **Python 3.x**
- **Required Packages**:  
  - `zeep` (SOAP client)
  - `argparse`, `csv`, `logging`, `xml` (Python standard library)

Install dependencies if needed:

```sh
pip install zeep
```

---

## Usage

```sh
python enable_agents.py -H <host> -P <port> -u <username> -p <password> --input-file <path_to_csv> [--ssl] [--log-level <LEVEL>]
```

### Arguments

| Argument                | Required | Description                                                        |
|-------------------------|----------|--------------------------------------------------------------------|
| `-H`, `--host`          | Yes      | Host address of the analytics server                               |
| `-P`, `--port`          | Yes      | Port number for the server                                         |
| `-u`, `--username`      | Yes      | Username for login                                                 |
| `-p`, `--password`      | Yes      | Password for login                                                 |
| `--input-file`          | Yes      | CSV file listing agent paths and enable state                      |
| `--ssl`                 | No       | Use SSL for the connection (flag)                                  |
| `--log-level`           | No       | Logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL, default: INFO) |

---

### Example

Enable or disable all agents listed in `agents_status.csv` with debug logging:

```sh
python enable_agents.py -H analytics.example.com -P 9502 -u myuser -p mypass --ssl --input-file agents_status.csv --log-level DEBUG
```

Where `agents_status.csv` contains:

```csv
path,agentEnabled
/shared/MyAgent,True
/shared/AnotherAgent,False
```

---

## Output

- **Console output:**  
  Logs progress, errors, and enable/disable actions for each agent processed.
- **Agents are updated** in Oracle Analytics according to the commands in the CSV file.

---

## Troubleshooting

- Verify host, port, username, and password are correct and the user is allowed to access SOAP web services.
- Ensure the CSV file matches the required format (`path`, `agentEnabled` with a header).
- The `zeep` library is required (`pip install zeep`).
- Network/firewall access to your analytics server is required.
- For more detailed output, set `--log-level` to `DEBUG`.

---

## License

This script is provided "as-is" for demonstrative purposes and is NOT supported by Oracle as a licensed product.
