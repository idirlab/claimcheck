from ClaimCheck.llms import qwen

def reformulate_claim(claim, metadata):
    """
    Reformulates a claim using metadata for additional context.
    """
    prompt = f"""
    # Instructions
    You are presented with some raw Content, optionally with additional metadata like Content date or author. **Your task right now is to interpret the Content.** That is, identify the author's core message and write down the main point(s) using your own words. Do not ask any questions. Be concise and write only one paragraph.

    # Content
    Original Claim: "{claim}"
    Metadata:
        - Speaker: {metadata.get('speaker', 'Unknown')}
        - Date: {metadata.get('claim_date', 'Unknown')}
        - Origin URL: {metadata.get('original_claim_url', 'Unknown')}
        - Reporting Source: {metadata.get('reporting_source', 'Unknown')}
        - Location ISO Code: {metadata.get('location_ISO_code', 'Unknown')}

    # Interpretation
    """
    reformulated_claim = qwen(prompt)
    return reformulated_claim
