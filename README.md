# ClaimCheck

## Overview
ClaimCheck is a fact-checking system that processes claims and verifies their veracity using various modules and models.

## Pre-requisites
1. Create a new Programmable Search Engine in Google:
   - Go to the [Programmable Search Engine](https://cse.google.com/cse/) and create a new search engine.
   - Note down the CSE ID.
   - Enable the Custom Search JSON API in the [Google Cloud Console](https://console.cloud.google.com/).
   - Note down the API key.

2. Get your API key from [SerpAPI](https://serper.dev/).

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

3. Update the API keys in the code:
   - Open `claim_matching.py` and update the Google Cloud API key and CSE ID.
   - Open `search.py` and update the SerpAPI key.

## Usage
To run the fact-checking system from the command line, use the `fact-check.py` script. It takes two arguments: the path to the JSON file containing the claims and the number of records to process.

### Command Line Arguments:
- `json_path`: Path to the AVeriTeC JSON file.
- `num_records`: Number of claims to run.

### Example:
```bash
python fact-check.py /path/to/json/file.json 5

Replace `/path/to/json/file.json` with the actual path to your AVeriTeC JSON file and `5` with the number of records you want to process. You can find AVeriTeC JSON files [here](https://fever.ai/dataset/averitec.html).

