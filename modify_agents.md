# modify_agents.py Documentation

## Overview

`modify_agents.py` is a utility script for Oracle Analytics/OBIEE environments.  
It connects to the Oracle Analytics server using SOAP web services, reads a CSV file describing modifications for a set of agents (iBots)—including run-as user and recipient fields, creates backups, and applies the changes in bulk.

---

## Features

- Connects to Oracle Analytics/OBIEE using SOAP web services (Zeep Python client).
- Authenticates via username and password (supports SSL).
- Processes a CSV file specifying path and new values for run-as user and recipients.
- Applies runAs, specificRecipients, emailRecipients modifications to each listed agent.
- Creates a backup of each agent before changes are made.
- Logs progress, errors, and results to the console.
- Supports adjustable logging verbosity.

---

## Requirements

- **Python 3.x**
- **Required Packages**:  
  - `zeep` (SOAP client)
  - `argparse`, `csv`, `logging`, `os`, `xml`, `datetime`, `traceback` (Python standard library)

Install dependencies if needed:

```sh
pip install zeep
```

---

## Usage

```sh
python modify_agents.py -H <host> -P <port> -u <username> -p <password> --input-file <path_to_csv> [--ssl] [--no-backup] [--backup-path <dir>] [--log-level <LEVEL>]
```

### Arguments

| Argument                | Required | Description                                                        |
|-------------------------|----------|--------------------------------------------------------------------|
| `-H`, `--host`          | Yes      | Host address of the analytics server                               |
| `-P`, `--port`          | Yes      | Port number for the server                                         |
| `-u`, `--username`      | Yes      | Username for login                                                 |
| `-p`, `--password`      | Yes      | Password for login                                                 |
| `--input-file`          | Yes      | CSV file with columns: path, runAs, specificRecipients, emailRecipients |
| `--ssl`                 | No       | Use SSL for the connection (flag)                                  |
| `--no-backup`           | No       | Do not create a backup of each agent before modification           |
| `--backup-path`         | No       | Directory to store backups (default: `./`)                         |
| `--log-level`           | No       | Logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL; default: INFO) |

---

### Example

Bulk modify agents as described in `agents_changes.csv`, keeping XML backups in a specific directory:

```sh
python modify_agents.py -H analytics.example.com -P 9502 -u myuser -p mypass --ssl --input-file agents_changes.csv --backup-path ./agent_backups --log-level INFO
```

Where `agents_changes.csv` contains:

```csv
path,runAs,specificRecipients,emailRecipients
/shared/MyAgent,myuser1,,john.doe@example.com
/shared/OtherAgent,myadmin,alice,bob@example.com
```

---

## Output

- **Console output:**  
  Logs progress, errors, actions taken, and backup file creation for each agent processed.
- **Agents are updated** in Oracle Analytics as specified in the CSV, with optional backups created in the given directory.

---

## Troubleshooting

- Check that host, port, username, and password are correct and user is allowed to use SOAP web services.
- Ensure the CSV file format matches requirements, including all necessary columns and a header row.
- The `zeep` library is required (`pip install zeep`).
- Network/firewall access to your analytics server is required.
- To skip automatic backups, use the `--no-backup` flag.
- For more detailed output, set `--log-level` to `DEBUG`.

---

## License

This script is provided "as-is" for demonstrative purposes and is NOT supported by Oracle as a licensed product.
