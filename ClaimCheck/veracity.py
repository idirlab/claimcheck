from ClaimCheck.llms import qwen, qwen_finetuned

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

    prompt = f"""# Fact-Checking Analysis Task

## Objective
Analyze the provided evidence and QA pairs to determine the veracity of the claim using the structured methodology below.
Must output the data in the structured JSON format, not just as text. The verdict must be one of the following options: Supported, Refuted, Conflicting Evidence/Cherrypicking, Not Enough Evidence.
---

## Verification Protocol

1. **Evidence Synthesis**  
   - Identify factual anchors in both evidence and QA responses
   - Note contradictions, corroborations, and evidence quality

2. **Verdict Determination**  
   Select ONE of the below verdicts using these strict criteria:

   **Supported**  
   - Evidence conclusively proves claim true  
   - Multiple credible sources align without contradiction

   **Refuted**  
   - Evidence disproves central claim elements  
   - Includes fabricated content/deceptive practices
   - Lack of any credible sources supporting the claim

   **Conflicting Evidence/Cherrypicking**  
   - Reputable sources directly contradict each other  
   - No resolvable consensus after analysis

   **Not Enough Evidence**  
   - No relevant evidence found after exhaustive search  
   - Claim too vague for substantive evaluation  
   *(Last-resort option only)*

   Do not select any other verdicts.

---

## Input Data
**Claim to Evaluate**  
{claim}

**Relevant Evidence**  
{relevant_evidence}

**QA Pair Analysis**  
{qa_text}

---

## Output Requirements

Must output the data in the following JSON format, no exceptions.:

**JSON Structure**  
```json
{{
    "classification": "One of the above verdict options",
    "justification": "Cohesive analysis paragraph of reasoning for the selected verdict"
}}
```
Example Output:

```json
{{
    "classification": "Refuted",
    "justification": "The evidence and answers show that the claim was published on a fake news site, so the claim is refuted."
}}
```
"""


    response = qwen(prompt)
    
    return response



def veracity_prediction_finetuned(claim, qa_pairs, relevant_evidence):
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
### Input: 
Claim: {claim}
{qa_pairs}
{relevant_evidence}
"""

    response = qwen_finetuned(prompt)
    
    return response
