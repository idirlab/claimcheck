from ClaimCheck.llms import llama3_1

def veracity_prediction(claim, qa_pairs, relevant_evidence):
    """
    Aggregate QA pairs and let the LLM summarize and justify conclusions using a new prompt style.

    Args:
    - qa_pairs (list of str): Each string is a formatted question-answer pair in the format 
      "Question: Answer".
    - contains_misinfo (bool): Whether the URLs contain misinformation.

    Returns:
    - dict: A dictionary with the keys 'Summary', 'Justification', and 'Conclusion'.
    """
    # Join QA pairs as input for the LLM
    qa_text = str(qa_pairs)
    
    # Construct the new prompt

    prompt = f"""
Instructions
Determine the Claim's veracity by following these steps:

Briefly summarize the key insights from the fact-check (see Record) in at most one paragraph.
Write one paragraph about which one of the Decision Options applies best. You must include the most appropriate decision option at the end and enclose it in backticks like `this`.
Do not discuss why other verdict are not relevant, only talk about the selected verdict. This should be the only one in backticks.

Decision Options
1. Supported: The knowledge from the fact-check supports or at least strongly implies the claim. Mere plausibility is not enough for this decision.
2. Refuted: The knowledge from the fact-check clearly refutes the claim. The mere absence or lack of supporting evidence is not enough reason for being refuted (argument from ignorance). This includes fake news and deliberate misinformation. 
3. Conflicting Evidence/Cherrypicking: The knowledge from the fact-check contains conflicting evidence from multiple reliable sources. Even trying to resolve the conflicting sources through additional investigation was not successful.

Otherwise, if you cannot determine the veracity, and none of the evidence is not at all related to the claim or there is no evidence, respond with "I cannot reach a conclusion due to insufficient data", without any backticks. List the evidence that is missing.

Record
{qa_text}

Highly Useful Evidence:
{relevant_evidence}

Your Judgement
"""

    prompt = f"""
### Input: 
Claim: {claim}
{qa_pairs}

"""

    response = llama3_1(prompt)
    
    return response