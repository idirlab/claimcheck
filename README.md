# ClaimCheck

## Overview
ClaimCheck is a fact-checking system that processes claims and verifies their veracity using various modules and models.

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/akshithputta/ClaimCheck.git
    cd ClaimCheck
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
To run the fact-checking system from the command line, use the `fact-check.py` script. It takes two arguments: the path to the JSON file containing the claims and the number of records to process.

### Command Line Arguments:
- `json_path`: Path to the AVeriTeC JSON file.
- `num_records`: Number of claims to run.

### Example:
```bash
python fact-check.py /path/to/json/file.json 5
