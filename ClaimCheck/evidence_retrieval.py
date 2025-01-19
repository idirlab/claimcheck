import re
from ClaimCheck.llms import llama3_2, llama3_1
from ClaimCheck.search import serper_search, scrape_url_content

def query_transform(question, claim):
    try:
        prompt = f"""
        # Instructions
        You are a fact-checker. Your overall motivation is to verify a given Claim. To this end, you asked a Question. Your task right now is to **rewrite the question for web search** that aims to retrieve evidence that answers the Question. Additionally, follow these rules:
        * The main task is to make the search query make sense in the context of the Question. Add question-specific context if necessary.
        * You must format your proposed search query question by putting the query string into backticks like `this`.
        * Be brief, do not justify your proposed actions.

        ## Question
        {question}

        ## Claim
        {claim}

        ## Query
        """
        response = llama3_2(prompt)
        query = re.search(r'`([^`]+)`', response).group(1)
        query = query.replace('"', '')
        if "OR" in query:
            query = query.split("OR")[0]

        return query
    except Exception as e:
        print(f"An error occurred: {e}. Retrying...")
        return query_transform(question, claim)


def get_evidence(query, date, top_k=5):
    """
    Retrieve the most relevant evidence documents for a list of queries using embeddings and 5-NN search.
    """
    # Define API key and CSE ID
    API_KEY = "AIzaSyAGENP28MzRDJ4LZdLpLaluuwLNBKHYl0Q"
    CSE_ID = "52bd9e51448204e94"

    search_results, snippets = serper_search(query, top_k=top_k, date=date)

    return search_results, snippets

def qa_on_question(urls, question, claim):
    """
    Answer a question based on the evidence retrieved.
    """
    answers = []
    useful_evidence = []

    answer_found = False
    for link in urls:
        content = scrape_url_content(link)

        evidence_text = " ".join(content) if content else ""
        if not evidence_text:
            continue
            
            # Construct the prompt
        prompt = f"""
            Instructions
            You are a fact-checker. Your overall motivation is to verify a given Claim. You already did part of the fact-check, documented under "Record". In order to find evidence that helps the fact-checking work, you just ran a web search which yielded a Search Result. Your task right now is to answer the Question given below. Adhere to the following rules:

            The length of your Answer should be between one sentence and one paragraph.
            If applicable and useful, you may directly cite relevant excerpts from the source. In that case, put the citation into quotation marks.
            If the search result does not contain sufficient information to answer the Question or is unrelated to the question completely, respond simply with NONE.
            If the evidence does not answer the question, but can otherwise be highly useful for the fact-check, you must respond with "The evidence is useful, but does not answer the question." This is a very rare case.


            Record
            Claim: "{claim}"

            Question
            {question}

            Search Result
            {evidence_text}

            Your Answer
            """

        response = llama3_1(prompt)
        

        if "the evidence is useful" in response.lower():
            useful_evidence.append(evidence_text)

        if "none" not in response.lower():
            answers.append(f"{question}: {response}")
            answer_found = True
            break  # Stop searching for this question if an answer is found
        
    if not answer_found:
        answers.append(f"{question}: No answer found")
    
    return answers, useful_evidence