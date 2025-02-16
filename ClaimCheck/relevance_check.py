from ClaimCheck.llms import qwen

def answer_check(answers, claim):
    relevant_answers = []
    for answer in answers:
        prompt = f"""
        Instructions
        You are a fact-checker. Your overall motivation is to verify a given Claim. You already did part of the fact-check, documented under "Record". In order to find evidence that helps the fact-checking work, you just ran a web search which yielded a Search Result. Your task right now is to determine if the Answer is useful to fact-checking the Claim. Adhere to the following rules:
        An answer is useful even when it doesn't directly answer the question, if it provides highly relevant information for fact-checking. It just has to be somewhat related to the Claim.
        If the Answer is useful to fact-checking the Claim, respond only with "Yes".
        If the Answer is not useful to fact-checking the Claim, respond only with "No".

        Record
        Claim: "{claim}"

        Question and Answer: "{answer}"

        """
        response = qwen(prompt)
        if "no" in response.lower():
            print(answer, response)
        if "yes" in response.lower():
            relevant_answers.append(answer)
            print("Relevant answer found.", answer)
    return relevant_answers

def useful_evidence_check(evidence_list, claim):
    relevant_evidence = []
    for evidence in evidence_list:
        prompt = f"""
        Instructions
        You are a fact-checker. Your overall motivation is to verify a given Claim. You already did part of the fact-check, documented under "Record". In order to find evidence that helps the fact-checking work, you just ran a web search which yielded possibly useful evidence. Your task right now is to determine if the evidence is relevant to fact-checking the Claim. Adhere to the following rules:
        If the evidence is relevant to fact-checking the Claim, respond with a short summary of the evidence, particularly the parts relevant to the claim.
        If the evidence is not at all relevant to fact-checking the Claim, respond only with "No".

        Record
        Claim: "{claim}"

        Evidence: "{evidence}"

        """
        response = qwen(prompt)
        print(response)
        if "no" in response.lower() and len(response) < 20:
            relevant_evidence.append(evidence)
            print("Relevant evidence found.", evidence)
    return relevant_evidence
