import re

from ClaimCheck.averitec import loader
from ClaimCheck.claim_matching import claim_matching, article_check, summarize_article
from ClaimCheck.reformulate_claim import reformulate_claim
from ClaimCheck.questions import question_generation
from ClaimCheck.veracity import veracity_prediction
from ClaimCheck.evidence_retrieval import query_transform, get_evidence, qa_on_question
from ClaimCheck.relevance_check import answer_check, useful_evidence_check
from ClaimCheck.justification import justification_production

json_path = 'YOUR AVERITEC JSON FILE LOCATION'
num_records = 2

df = loader(json_path, num_records)

for i, row in df.iterrows():
    metadata = {
        'speaker': row['Speaker'],
        'claim_date': row['Claim Date'],
        'original_claim_url': row['Original Claim URL'],
        'reporting_source': row['Reporting Source'],
        'location_ISO_code' : row['Location ISO Code']
    } 
    reformulated_claim = reformulate_claim(row['Claim'], metadata)
    
    # Claim Matching
    evidence_documents = claim_matching(row['Claim'], date=row['Claim Date'], top_k=3)
    if evidence_documents:
        relevant_documents = article_check(reformulated_claim, evidence_documents)
        if relevant_documents:
            relevant_evidence = summarize_article(reformulated_claim, relevant_documents)
            print(reformulated_claim, relevant_documents, relevant_evidence)
            verdict = veracity_prediction(reformulated_claim, relevant_documents, relevant_evidence)
            justification = justification_production(reformulated_claim, relevant_evidence, verdict)

            print("Claim Matched")

            print(f"Claim: {row['Claim']}")
            print(f"Verdict: {verdict}")
            print(f"Justification: {justification}")
            continue

    print("Novel Claim Processing")

    queries = []
    answers = []
    useful_evidence_list = []
 
    question = question_generation(reformulated_claim)
    question_list = re.findall(r'\d+\.\s`([^`]+)`', question)
    for q in question_list:
        query = query_transform(q, reformulated_claim)
        queries.append(query)
        question_evidence, snippets = get_evidence(query=query, top_k=5, date = row['Claim Date'])
        print(question_evidence, snippets)
        answer, useful_evidence = qa_on_question(question_evidence, q, reformulated_claim)
        answers.append(answer)
        useful_evidence_list.extend(useful_evidence)

    relevant_answers = answer_check(answers, reformulated_claim)
    relevant_evidence = useful_evidence_check(useful_evidence_list, reformulated_claim)

    print(reformulated_claim, relevant_answers, relevant_evidence)
    verdict = veracity_prediction(reformulated_claim, relevant_answers, relevant_evidence)
    justification = justification_production(reformulated_claim, relevant_answers, verdict)

    print(f"Claim: {row['Claim']}")
    print(f"Verdict: {verdict}")
    print(f"Justification: {justification}")
