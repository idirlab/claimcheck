from ClaimCheck.llms import llama3_2

def question_generation(reformulated_claim):
    """
    Generates fact-checking questions for a reformulated claim.
    """

    prompt = f"""
    # Instructions
    You are a fact-checker. Your overall motivation is to verify a given Claim. You are in the middle of the fact-check, documented under "Record". **Your task right now is to pose questions.** That is,
    1. Analyze what information is missing. Write one or two paragraphs for this.
    2. Finally, state a complete and enumerated list of Questions: The Questions are supposed to guide the fact-check. Answering them should help to verify the Claim.

    IMPORTANT: Follow these rules:
    * Enclose each single question with backticks like `this`.
    * Do not repeat questions already contained in the Record. Only state substantially new questions.
    * Include context from the claim itself to make the questions claim-specific. If the question is web searched, it should return information that is relevant to the claim, not general information.

    Tips:
    * Ask one question to unveil more about the Claim's origin. For example, where did the Claim first occur? If the Claim contains a quote, ask where the quote was first published. If the Claim's speaker is unknown, ask who the speaker is.
    * You may base your new questions on previously found evidence (if available) to dive deeper into the matter, if helpful.
    * Try to ask diverse questions. Avoid repeating the wording from previous questions.
    * Remain brief.

    # Examples
    Claim: "New Zealand's new Food Bill bans gardening."
    Questions:
    1. `Did New Zealand's government pass a food bill that restricted gardening for its citizen?`
    2. `When was the Food Bill in New Zealand passed?`
    3. `Which Food Bill in New Zealand does the claim refer to?`
    4. `Does the blog post imply that this Food Bill in New Zealand is already legislation?`

    Claim: "Video of a man blowing vape smoke through various face masks shows that they do not help prevent the spread of coronavirus."
    Questions:
    1. `How does coronavirus spread?`
    2. `Do face masks help in the prevention of coronavirus?`

    Claim: "The Nigerian government is donating $600 million to Democratic presidential nominee Joe Biden's campaign."
    Questions:
    1. `Where was this claim about the Nigerian government donating $600 Million to Biden's campaign published?`
    2. `Who in the Nigerian government is attributed to have made this donation?`
    3. `Is Nigeria or Lai Mohammed on the FEC list of donors to the Biden campaign?`
    4. `Are donations to US presidential campaigns from foreign countries/nationals allowed?`

    # Record
    Claim: "{reformulated_claim}"

    ## Analysis
    """

    questions = llama3_2(prompt)
    return questions