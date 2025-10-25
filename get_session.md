# get_session.py Documentation

## Overview

`get_session.py` is a utility script for Oracle Analytics/OBIEE environments.
It demonstrates how to connect to an Oracle Analytics server, authenticate using supplied credentials, obtain a session, and close the session, all via the SOAP web services API.  
This script is intended as a minimal use case or for quick connection testing and authentication verification.

---

## Features

- Connects to Oracle Analytics/OBIEE using SOAP web services (`zeep` library).
- Authenticates with provided username/password, supports SSL.
- Obtains a session ID, then logs out immediately.
- Logs connection attempts, session status, and errors.

---

## Requirements

- **Python 3.7+**
- **Required Packages**:  
  - `zeep` (SOAP client)
  - `argparse`, `logging` (bundled with Python standard library)

Install dependency if needed:

```sh
pip install zeep
```

---

## Usage

```sh
python get_session.py -H <host> -P <port> -u <username> -p <password> [--ssl] [--log-level <level>]
```

### Arguments

| Argument              | Required | Description                                   |
|-----------------------|----------|-----------------------------------------------|
| `-H`, `--host`        | Yes      | Host address of the analytics server          |
| `-P`, `--port`        | Yes      | Port number for the server                    |
| `-u`, `--username`    | Yes      | Username for login                            |
| `-p`, `--password`    | Yes      | Password for login                            |
| `--ssl`               | No       | Use SSL for the connection (flag)             |
| `--log-level`         | No       | Logging verbosity (DEBUG, INFO, etc.)         |

### Example

Test a connection over SSL with debug logging:

```sh
python get_session.py -H analytics.example.com -P 9502 -u myuser -p mypass --ssl --log-level DEBUG
```

---

## Output

- The script does **not** produce files or persistent output.
- Logs status information to the console:
  - Session ID obtained on success.
  - Errors encountered during connection or authentication.

---

## Troubleshooting

- Ensure the host/port/credentials are correct and have sufficient permissions.
- The analytics server must be accessible from your machine.
- The `zeep` library is required (`pip install zeep`).
- You may need network/firewall access to the analytics web service endpoint.

---

## License

This script is provided "as-is" for demonstrative purposes and is NOT supported by Oracle as a licensed product.
