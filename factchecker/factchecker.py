import re
import os
import json
import concurrent.futures
from modules import planning, evidence_summarization, evidence_synthesis, evaluation
from tools import web_search, web_scraper
from report import report_writer
import fcntl

class FactChecker:
    def __init__(self, claim, date, identifier=None, multimodal=False, image_path=None, max_actions=2):
        self.claim = claim
        self.date = date
        self.multimodal = multimodal if not (multimodal and image_path is None) else False
        self.image_path = image_path
        if identifier is None:
            from datetime import datetime
            identifier = datetime.now().strftime("%m%d%Y%H%M%S")
        self.identifier = identifier
        report_writer.init_report(claim, identifier)
        self.report_path = report_writer.REPORT_PATH
        print(f"Initialized report at: {self.report_path}")
        # Initialize the report dict for web use
        self.report = {
            "claim": self.claim,
            "date": self.date,
            "identifier": self.identifier,
            "actions": {},
            "reasoning": [],
            "judged_verdict": None,
            "verdict": None,
            "justification": None,
            "report_path": self.report_path
        }
        self.max_actions = max_actions

        # Save initial JSON report
        self.save_report_json()

    def save_report_json(self):
        """Save the report dictionary as report.json in the report_path folder"""
        try:
            json_path = os.path.join(os.path.dirname(self.report_path), 'report.json')
            with open(json_path, 'w') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                json.dump(self.report, f, indent=2)
                fcntl.flock(f, fcntl.LOCK_UN)
            print(f"Report JSON saved to: {json_path}")
        except Exception as e:
            print(f"Error saving report JSON: {e}")

    def get_report(self):
        report_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../reports', self.identifier, 'report.md'))
        try:
            with open(report_path, "r") as f:
                return f.read()
        except Exception as e:
            return f"Error reading report: {e}"

    def process_action_line(self, line):
        try:
            m = re.match(r'(\w+)_search\("([^"]+)"\)', line)
            if m:
                action, query = m.groups()
                action_entry = {
                    "action": action + "_search",
                    "query": query,
                    "results": None
                }
                identifier = f'{action}: {query}'
                if identifier in self.report["actions"]:
                    print(f"Skipping duplicate action: {identifier}")
                    return

                if action == 'web':
                    self.report["actions"][identifier] = action_entry
                    urls, snippets = web_search.web_search(query, self.date, top_k=3)

                    # Default with snippets from web_search
                    self.report["actions"][identifier]["results"] = {url: {"snippet": snippet, 'url':url, 'summary': None} for url, snippet in zip(urls, snippets)}
                    self.save_report_json()

                    def process_result(result):
                        scraped_content = web_scraper.scrape_url_content(result)
                        summary = evidence_summarization.summarize(self.claim, scraped_content, result, record=self.get_report())

                        if "NONE" in summary:
                            print(f"Skipping summary for evidence: {result}")
                            return None

                        print(f"Web search result: {result}, Summary: {summary}")
                        report_writer.append_raw(f"web_search('{query}') results: {result}")
                        report_writer.append_evidence(f"web_search('{query}') summary: {summary}")

                        self.report["actions"][identifier]["results"][result]["summary"] = summary
                        self.save_report_json()

                    with concurrent.futures.ThreadPoolExecutor() as result_executor:
                        processed = list(result_executor.map(process_result, urls))
                else:
                    return

        except Exception as e:
            print(f"Error processing action line '{line}': {e}")

    def run(self):
        if self.multimodal == True:
            actions = "All"
        else:
            actions = ["web_search"]#, "image_search"]

        actions = planning.plan(self.claim, record=self.get_report(), actions=actions)
        report_writer.append_iteration_actions(1, actions)
        print(f"Proposed actions for claim '{self.claim}':\n{actions}")

        action_lines = re.findall(r'\s*(.+)', actions)
        print(f"Extracted action lines: {action_lines}")

        # Filter out invalid or empty action lines using regex
        action_lines = [line for line in action_lines if re.match(r'(\w+)_search\("([^"]+)"\)', line)]
        print(f"Filtered valid action lines: {action_lines}")
        print(f"Total action lines: {len(action_lines)}")
        print(f"Max actions allowed: {self.max_actions}")

        if action_lines and len(action_lines) > self.max_actions:
            print(f"Limiting actions to the first {self.max_actions} lines.")
            action_lines = action_lines[:self.max_actions]
        
        print(f"Processing action lines: {action_lines}")

        # block multithreading until everything above is done
        

        with concurrent.futures.ThreadPoolExecutor() as executor:
            list(executor.map(self.process_action_line, action_lines))

        # Save the initial report after planning
        self.save_report_json()

        iterations = 0
        seen_action_lines = set(action_lines)
        while iterations < 1:
            reasoning = evidence_synthesis.develop(record=self.get_report())

            print(f"Developed reasoning:\n{reasoning}")
            report_writer.append_reasoning(reasoning)

            self.report["reasoning"].append(reasoning)
            self.save_report_json()
            reasoning_action_lines = re.findall(r'\s*(.+)', reasoning)

            if not reasoning_action_lines:
                break

            if any(line in seen_action_lines for line in reasoning_action_lines):
                print("Duplicate action line detected. Stopping iterations.")
                break

            seen_action_lines.update(reasoning_action_lines)

            with concurrent.futures.ThreadPoolExecutor() as executor:
                list(executor.map(self.process_action_line, reasoning_action_lines))

            iterations += 1

        allowed_verdicts = {"Supported", "Refuted", "Conflicting Evidence/Cherrypicking", "Not Enough Evidence"}
        max_judge_tries = 3
        judge_tries = 0
        pred_verdict = ''
        rules = """
Supported
- The claim is directly and clearly backed by strong, credible evidence. Minor uncertainty or lack of detail does not disqualify a claim from being Supported if the main point is well-evidenced.
- Use Supported if the overall weight of evidence points to the claim being true, even if there are minor caveats or not every detail is confirmed.

Refuted
- The claim is contradicted by strong, credible evidence, or is shown to be fabricated, deceptive, or false in its main point.
- Use Refuted if the central elements of the claim are disproven, even if some minor details are unclear.
- Lack of any credible sources supporting the claim does not mean "Not Enough Evidence" - it means the claim is Refuted.

Conflicting Evidence/Cherrypicking
- Only use this if there are reputable sources that directly and irreconcilably contradict each other about the main point of the claim, and no clear resolution is possible after careful analysis.
- Do NOT use this for minor disagreements, incomplete evidence, or if most evidence points one way but a few sources disagree.

Not Enough Evidence
- Only use this if there is genuinely no relevant evidence available after a thorough search, or if the claim is too vague or ambiguous to evaluate.
- Do NOT use this if there is some evidence, even if it is weak, or if the claim is mostly clear but not every detail is confirmed.
- This is a last-resort option only.
"""
        while judge_tries < max_judge_tries:
            verdict = evaluation.judge(
                record=self.get_report(),
                decision_options="Supported|Refuted|Conflicting Evidence/Cherrypicking|Not Enough Evidence",
                rules=rules,
                think=None  # Replace with think_judge if defined
            )
            print(f"Judged verdict (try {judge_tries+1}):\n{verdict}")
            extracted_verdict = re.search(r'`(.*?)`', verdict, re.DOTALL)
            pred_verdict = extracted_verdict.group(1).strip() if extracted_verdict else ''
            if pred_verdict in allowed_verdicts:
                break
            judge_tries += 1

        # If extraction failed after max tries, find the most frequent decision option in the verdict text
        if pred_verdict not in allowed_verdicts:
            print("Original extraction failed, falling back to most frequent decision option...")
            option_counts = {}
            for option in allowed_verdicts:
                # Count occurrences of each decision option in the verdict text
                count = verdict.lower().count(option.lower())
                if count > 0:
                    option_counts[option] = count

            if option_counts:
                # Use the most frequent option
                pred_verdict = max(option_counts, key=option_counts.get)
                print(f"Fallback verdict selected: {pred_verdict} (appeared {option_counts[pred_verdict]} times)")
            else:
                # If no options found, use extract_verdict from judge.py
                print("No decision options found in verdict, using extract_verdict from judge.py...")
                try:
                    extracted = evaluation.extract_verdict(verdict, "Supported|Refuted|Conflicting Evidence/Cherrypicking|Not Enough Evidence", rules)
                    extracted_verdict = re.search(r'`(.*?)`', extracted, re.DOTALL)
                    pred_verdict = extracted_verdict.group(1).strip() if extracted_verdict else extracted.strip()
                    print(f"extract_verdict returned: {pred_verdict}")
                except Exception as e:
                    print(f"extract_verdict failed: {e}")
                    pred_verdict = "INVALID VERDICT"
                    print("No decision options found in verdict, defaulting to 'INVALID VERDICT'.")

        report_writer.append_verdict(verdict)
        self.report["judged_verdict"] = verdict
        self.report["verdict"] = pred_verdict
        self.save_report_json()

        return pred_verdict, report_writer.REPORT_PATH

# For backward compatibility, provide a function interface

def factcheck(claim, date, identifier=None, multimodal = False, image_path = None, max_actions=2):
    return FactChecker(claim, date, identifier, multimodal, image_path, max_actions).run()