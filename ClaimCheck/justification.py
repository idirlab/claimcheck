from ClaimCheck.llms import llama3_1

def justification_production(claim, qa_pairs, verdict):
    """
    Justify the verdict based on the QA pairs.

    Args:
    - qa_pairs (list of str): Each string is a formatted question-answer pair in the format 
      "Question: Answer".
    - verdict (str): The verdict for the claim.

    Returns:
    - str: A formatted justification for the verdict.
    """
    # Join QA pairs as input for the LLM
    qa_text = str(qa_pairs)
    
    # Construct the new prompt
    prompt = f"""Instructions
You are provided with the record of a fact-check. It contains
the Claim to be verified and documentation of all the factchecking work along with the gathered evidence. Your task
is to summarize the fact-check. That is, you provide a
concise, one-paragraph justification for the final VERDICT
based on the knowledge from the Record. Note:
* Be truthful, brief, and do not add any additional information besides the information given in the Record.
* Link key sources in your summary. Use Markdown notation for that. You may link them in-line.
* Don't state the Claim again. Rather focus on the key insights of the fact-check.
* Simply print just the summary.
* Enclose the final Justification in backticks like this: `Justification`.

[Record]
{qa_text}
[Verdict]
{verdict}
Justification:

"""
    response = llama3_1(prompt)

    return response