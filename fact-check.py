import re
import json
import pandas as pd
from ClaimCheck.averitec import loader
from ClaimCheck.claim_matching import claim_matching, article_check, summarize_article
from ClaimCheck.reformulate_claim import reformulate_claim
from ClaimCheck.questions import question_generation
from ClaimCheck.veracity import veracity_prediction_2, veracity_prediction_finetuned
from ClaimCheck.evidence_retrieval import query_transform, get_evidence, qa_on_question
from ClaimCheck.relevance_check import answer_check, useful_evidence_check
from ClaimCheck.NEI_check import check_fact_checkability_llm, generate_additional_questions_llm

# Paths and configurations
json_path = '' # Your Path to AVeriTeC JSON file
num_records = 5 # Number of claims to run

# Data loader
df = loader(json_path, num_records)

def extract_response(output: str):
    """Extract JSON response from the LLM output."""
    try:
        return json.loads(re.search(r'```json(.*?)```', output, re.DOTALL).group(1).strip())
    except:
        return {'classification': 'error', 'justification': 'failed to extract response'}

# Function for fact-checking
def fact_check(claim, date, speaker=None, claim_url=None, reporting_source=None, location_ISO_code=None):
    metadata = {
        'speaker': speaker,
        'claim_date': date,
        'original_claim_url': claim_url,
        'reporting_source': reporting_source,
        'location_ISO_code' : location_ISO_code
    } 
    reformulated_claim = reformulate_claim(claim, metadata)
    
    # Claim Matching
    evidence_documents = claim_matching(claim, date=date, top_k=3)
    if evidence_documents:
        relevant_documents, link = article_check(reformulated_claim, evidence_documents)
        print(link)
        if relevant_documents:
            relevant_evidence = summarize_article(reformulated_claim, relevant_documents)
            print(relevant_documents, relevant_evidence)
            conclusion = veracity_prediction_2(reformulated_claim, relevant_documents, relevant_evidence, "deepseek-r1:7b")
            print(conclusion)

            extracted_data = extract_response(conclusion)  
            verdict = extracted_data['classification']
            justification = extracted_data['justification']

            print("Claim Matched")

            print(f"Claim: {claim}")
            print(f"Verdict: {verdict}")
            print(f"Justification: {justification}")
            return verdict, justification

    print("Novel Claim Processing")

    queries = []
    answers = []
    useful_evidence_list = []
 
    questions = question_generation(claim, metadata)
    question_list = re.findall(r'\d+\.\s`([^`]+)`', questions)
    for q in question_list:
        query = query_transform(q, reformulated_claim)
        queries.append(query)
        print("Question: ", q)
        print("Query: ", query)
        question_evidence, snippets = get_evidence(query=query, top_k=5, date = date)
        
        answer, useful_evidence = qa_on_question(question_evidence, snippets, q, reformulated_claim)
        answers.append(answer)
        useful_evidence_list.extend(useful_evidence)

    relevant_answers = answer_check(answers, reformulated_claim)
    relevant_evidence = useful_evidence_check(useful_evidence_list, reformulated_claim)

    print(relevant_answers, relevant_evidence)
    conclusion = veracity_prediction_finetuned(reformulated_claim, relevant_answers, relevant_evidence)
    print(conclusion)
    extracted_data = extract_response(conclusion)  
    verdict = extracted_data['classification']
    justification = extracted_data['justification']
    
    # Check if the claim is fact-checkable
    fact_checkability = check_fact_checkability_llm(claim, relevant_answers, verdict, justification)
    if fact_checkability['fact_checkable'] == 'No':
        print("Claim is not fact-checkable based on the provided evidence.")
        return verdict, justification

    print(f"Claim: {claim}")
    print(f"Verdict: {verdict}")
    print(f"Justification: {justification}")
    return verdict, justification

# Process and generate DataFrame for evaluation
results = []
for index, row in df.iterrows():
    claim = row['Claim']
    date = row['Claim Date']
    speaker = row['Speaker']
    claim_url = row['Original Claim URL']
    reporting_source = row['Reporting Source']
    location_ISO_code = row['Location ISO Code']
    verdict, justification = fact_check(claim, date, speaker, claim_url, reporting_source, location_ISO_code)
