from ClaimCheck.llms import qwen

def question_generation(claim, metadata):
    """
    Generates fact-checking questions for a reformulated claim.
    """

    prompt = f"""
    # Instructions
    You are a fact-checker verifying a claim. Your task is to generate clear, specific, and relevant fact-checking questions that help assess the accuracy of the claim.

    **Guidelines:**
    - Focus on the essential details of the claim. The questions should help find direct evidence to confirm or refute it.
    - Only use metadata (such as date, speaker, or source) when it is necessary for verification (e.g., when time-sensitive or quote verification is in question).
    - Each question should be concise and directly related to the claim.
    - Format each question using backticks like `this`.
    - Do not repeat questions already addressed in prior fact-checking records.

    **Examples:**
    Claim: "New Zealand's new Food Bill bans gardening."
    Questions:
    1. `Does New Zealand's Food Bill ban home gardening?`
    2. `What are the key regulations in the New Zealand Food Bill related to gardening?`
    3. `Has the New Zealand government enforced any gardening restrictions under this bill?`

    Claim: "Video of a man blowing vape smoke through various face masks shows that they do not help prevent the spread of coronavirus."
    Questions:
    1. `How does coronavirus spread?`
    2. `Do scientific studies show that face masks reduce the spread of coronavirus?`
    3. `Does the ability of vape smoke to pass through a mask indicate ineffectiveness against viruses?`

    Claim: "The Nigerian government is donating $600 million to Democratic presidential nominee Joe Biden's campaign."
    Questions:
    1. `Is there evidence that the Nigerian government donated $600 million to Joe Biden’s campaign?`
    2. `Are foreign governments legally allowed to donate to U.S. presidential campaigns?`
    3. `Has the Biden campaign reported any donations from Nigeria?`

    # Claim to Verify
    Claim: "{claim}"
    Metadata: {metadata}

    ## Questions:
    """

    questions = qwen(prompt)
    return questions
