# get_agents.py Documentation

## Overview

`get_agents.py` is a utility script for Oracle Analytics/OBIEE environments.
It connects to the Oracle Analytics server using SOAP web services, recursively traverses the catalog from a specified folder, identifies all agent (iBot) objects, retrieves their statuses (and optionally more details), and outputs the results as a CSV file.

---

## Features

- Connects to Oracle Analytics/OBIEE using SOAP web services (Zeep Python client).
- Authenticates via username and password (supports SSL).
- Recursively finds all agents (iBots) within a catalog path.
- Fetches status for each detected agent.
- Optionally gathers additional details (run-as user, recipient info) from agent XML.
- Exports agent data and status to a CSV file.

---

## Requirements

- **Python 3.7+**
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
python get_agents.py -H <host> -P <port> -u <username> -p <password> [--ssl] [--path <catalog_path>] [--details] [--output-file <filename>] [--log-level <level>]
```

### Arguments

| Argument               | Required | Description                                                |
|------------------------|----------|------------------------------------------------------------|
| `-H`, `--host`         | Yes      | Host address of the analytics server                       |
| `-P`, `--port`         | Yes      | Port number for the server                                 |
| `-u`, `--username`     | Yes      | Username for login                                         |
| `-p`, `--password`     | Yes      | Password for login                                         |
| `--ssl`                | No       | Use SSL for the connection (flag)                          |
| `--path`               | No       | Root folder to traverse for agents (default: `/shared`)    |
| `--details`            | No       | Include runAs user and recipients for each agent           |
| `--output-file`        | No       | CSV file for output (default: `agents_status.csv`)         |
| `--log-level`          | No       | Logging verbosity (DEBUG, INFO, etc.)                      |

---

### Example

Export all agent statuses (and details) for the `/shared/Finance` folder with debug logging:

```sh
python get_agents.py -H analytics.example.com -P 9502 -u myuser -p mypass --ssl --path "/shared/Finance" --details --output-file finance_agents.csv --log-level DEBUG
```

---

## Output

- **CSV File:**  
  Outputs to `agents_status.csv` by default, or as specified by `--output-file`
- Columns include:
  - `path`, `lastRun`, `nextRun`, `lastRunStatus`, `priority`,
    `agentEnabled`, `subscribed`, `specificRecipient`
  - If `--details` is used: also includes `runAs`, `specificRecipients`, `emailRecipients`

---

## Troubleshooting

- Verify host, port, username, and password are correct and allowed.
- Your user must have access to Oracle Analytics Web Services and the needed catalog paths.
- The `zeep` library is required (`pip install zeep`).
- Network/firewall access to your analytics server is required.

---

## License

This script is provided "as-is" for demonstrative purposes and is NOT supported by Oracle as a licensed product.
