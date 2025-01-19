import json
import pandas as pd

def loader(json_path, num_records):
    """
    Converts a JSON file into a Pandas DataFrame for processing.
    """
    label_mapping = {
        "Supported": 0,
        "Refuted": 1,
        "Not Enough Evidence": 2,
        "Conflicting Evidence/Cherrypicking": 3
    }
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    records = []
    for item in data[:num_records]:
        record = {
            "Claim": item.get("claim"),
            "Label": label_mapping.get(item.get("label"), -1),
            "Justification": item.get("justification"),
            "Claim Date": item.get("claim_date"),
            "Speaker": item.get("speaker"),
            "Original Claim URL": item.get("original_claim_url"),
            "Fact Checking Article": item.get("fact_checking_article"),
            "Reporting Source": item.get("reporting_source"),
            "Location ISO Code": item.get("location_ISO_code"),
            "Cached Original Claim URL": item.get("cached_original_claim_url"),
            "Claim Types": item.get("claim_types", []),
            "Fact Checking Strategies": item.get("fact_checking_strategies", [])
        }
        records.append(record)
    
    return pd.DataFrame(records)