# TestRail Data Export and Import Scripts

This repository contains Python scripts to export and import data from and to TestRail, a test case management tool.

## Overview

- **export_testrail.py**: Exports various data from a TestRail instance to JSON files.
- **import_testrail.py**: Imports data from JSON files into a TestRail instance.

## Prerequisites

- Python 3.x
- `requests` library

Install the required Python packages using:
```bash
pip install requests
```

## Configuration

Both scripts require configuration of the following variables:

- `base_url`: Your TestRail instance URL.
- `username`: Your TestRail email.
- `api_key`: Your TestRail API key.
- `project_id` (for export): The ID of the project you want to export data from.
- `new_project_id` (for import): The ID of the project you want to import data into.

## Usage

### Exporting Data

1. Configure the script by updating the variables mentioned above.
2. Set the `import_config` dictionary to specify which data to export.
3. Run the script:
    ```bash
    python export_testrail.py
    ```
4. The script will save the exported data as JSON files in the same directory.

### Importing Data

1. Ensure the JSON files to be imported are in the same directory as the script.
2. Configure the script by updating the variables mentioned above.
3. Set the `import_config` dictionary to specify which data to import.
4. Run the script:
    ```bash
    python import_testrail.py
    ```

## Logging

Both scripts use Python's logging module to provide information about the process. Logs are printed to the console.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
