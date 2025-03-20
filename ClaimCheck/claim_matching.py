from ClaimCheck.llms import qwen
from ClaimCheck.search import get_search_results_fc
from ClaimCheck.search import scrape_url_content


def claim_matching(claim, date, top_k=5):
    API_KEY = "GOOGLE_API_KEY"
    CSE_ID = "CSE_ID"

    # Perform Google search
    search_results = get_search_results_fc(API_KEY, CSE_ID, claim, date=date, top_k=top_k)

    return search_results



def article_check(reformulated_claim, evidence_list):
    for link in evidence_list:
        content = scrape_url_content(link)
        evidence_text = " ".join(content) if content else ""
        if not evidence_text:
            continue

        # Construct the new prompt
        prompt = f"""
        Can this fact-checking article provide a complete fact-check for the claim, including a clear verdict and justification with relevant evidence?
        Take into account the claim date and any other information important for fact-checking the claim.

        Possible Verdicts:
        - Supported: The knowledge from the fact-check supports or at least strongly implies the claim. Mere plausibility is not enough for this decision.
        - Refuted: The knowledge from the fact-check clearly refutes the claim. The mere absence or lack of supporting evidence is not enough reason for being refuted (argument from ignorance). This includes fake news and deliberate misinformation. 
        - Conflicting Evidence/Cherrypicking: The knowledge from the fact-check contains conflicting evidence from multiple reliable sources. Even trying to resolve the conflicting sources through additional investigation was not successful.

        Claim: "{reformulated_claim}"
        Article: "{evidence_text}"
        If the article cannot fulfill this requirement, respond with "No answer found." Otherwise, gather the key evidence from the article that can be used for fact checking the claim and summarize them in at most one paragraph.

        """
        response = qwen(prompt)

        if "no answer found" not in response.lower():
            print("Useful Article Found.", link)
            return [evidence_text, link]

    return "No relevant evidence found.", link

def summarize_article(reformulation_claim, article_text):
    prompt = f"""
    This fact-checking article provides a complete fact-check for the claim.
    Gather the key evidence from the article that can be used for fact checking the claim and summarize them in at most one paragraph.
    
    Claim: "{reformulation_claim}".

    Article: \n"{article_text}"
    """
    response = qwen(prompt)
    return response
