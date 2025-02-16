import json
from googleapiclient.discovery import build
from urllib.parse import urlparse
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import fitz  # PyMuPDF
from datetime import datetime
import timeout_decorator
import requests
from time import sleep
import trafilatura
from trafilatura.meta import reset_caches
from trafilatura.settings import DEFAULT_CONFIG


def get_page(url):
    page = None
    for i in range(3):
        try:
            page = trafilatura.fetch_url(url, config=DEFAULT_CONFIG)
            assert page is not None
            break
        except:
            sleep(3)
    return page

def html2lines(page):
    out_lines = []

    if len(page.strip()) == 0 or page is None:
        return out_lines

    text = trafilatura.extract(page, config=DEFAULT_CONFIG)
    reset_caches()

    if text is None:
        return out_lines

    return text.split("\n")

def url2lines(url):
    page = get_page(url)

    if page is None:
        return []
    
    lines = html2lines(page)
    return lines

# Helper function to extract the domain name from a URL
def get_domain_name(url):
    """Extracts the domain name from a URL."""
    if '://' not in url:
        url = 'http://' + url
    domain = urlparse(url).netloc
    if domain.startswith("www."):
        return domain[4:]
    return domain

# Function to perform a Google search using the Custom Search API
def serper_search(query, top_k, date, **kwargs):
    """
    Fetches search results using the Serper API and extracts URLs and snippets.

    Parameters:
    query (str): The search query.
    date (datetime.date): The date to filter results up to.
    top_k (int): The number of search results to fetch.

    Returns:
    tuple: A tuple containing two lists:
           - List of URLs from the organic results.
           - List of snippets from the organic results (empty string if snippet is missing).
    """
    # Format the date to the required format
    end_date = datetime.strptime(date, "%d-%m-%Y").strftime('%d/%m/%Y')

    # Serper API endpoint
    url = "https://google.serper.dev/search"

    # Prepare the payload
    payload = json.dumps({
        "q": query,
        "num": top_k,
        "tbs": f"cdr:1,cd_min:1/1/1900,cd_max:{end_date}"
    })

    # Headers including the API key
    headers = {
        'X-API-KEY': 'SERPER_API_KEY',  # Replace with your Serper API key
        'Content-Type': 'application/json'
    }

    # Make the POST request to the Serper API
    response = requests.post(url, headers=headers, data=payload)

    # Check if the request was successful
    if response.status_code == 200:
        results = response.json()
        
        # Extract URLs and snippets from the organic results
        urls = []
        snippets = []
        
        for item in results.get("organic", []):
            urls.append(item.get("link", ""))  # Get URL, default to empty string if missing
            snippets.append(item.get("snippet", ""))  # Get snippet, default to empty string if missing
        
        return urls, snippets
    else:
        raise Exception(f"Failed to fetch search results. Status code: {response.status_code}, Response: {response.text}")

# Function to scrape content from a given URL
@timeout_decorator.timeout(20)
def scrape_url_content(url):
    """Scrapes content from a URL. Supports YouTube, PDFs, and web pages."""
    try:
        if 'youtube.com' in url or 'youtu.be' in url:
            video_id = urlparse(url).query.split('v=')[-1]
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return [json.dumps(transcript)]  # Returning YouTube transcript as JSON
        elif url.endswith(".pdf"):
            response = requests.get(url)
            doc = fitz.open(stream=response.content, filetype="pdf")
            return [page.get_text("text") for page in doc]  # Extracting text from PDF
        else:
            return url2lines(url)  # Using `html2lines` for general web pages
    except Exception as e:
        return [f"Error scraping URL: {url}, Error: {str(e)}"]
    except timeout_decorator.timeout_decorator.TimeoutError:
        return [f"Error scraping URL: {url}, Error: {str(e)}"]

# Main function to retrieve search results and scrape their content
def get_search_results(query, date, top_k=5, blacklist=None, blacklist_files=None):
    """Fetches search results from Google Custom Search and scrapes their content."""
    if blacklist is None:
        blacklist = ["jstor.org", "facebook.com", "ftp.cs.princeton.edu", "nlp.cs.princeton.edu", "huggingface.co"]
    if blacklist_files is None:
        blacklist_files = ["/glove.", "ftp://ftp.cs.princeton.edu/pub/cs226/autocomplete/words-333333.txt", "https://web.mit.edu/adamrose/Public/googlelist"]

    results = []
    visited = set()

    # Perform the search
    search_results, snippets = serper_search(query, top_k, date, gl="US")

    if not search_results:
        return results
    for link in search_results:
        if not link:
            continue

        # Skip blacklisted domains or file types
        domain = get_domain_name(link)
        if domain in blacklist or any(file in link for file in blacklist_files):
            continue

        if link in visited or link.endswith((".pdf", ".doc", ".docx")):
            continue

        visited.add(link)
        content = scrape_url_content(link)
        results.append({"url": link, "content": content})

        if len(results) >= top_k:
            break

    return results

def google_search(search_term, api_key, cse_id, **kwargs):
    """Performs a search using Google's Custom Search API."""
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res.get("items", [])

def get_search_results_fc(API_KEY, CSE_ID, query, date, top_k=5):
    """Fetches search results from Google Custom Search, filtered by allowed domains."""
    results = []
    visited = set()

    # Perform the search
    search_results = google_search(query, API_KEY, CSE_ID)

    for result in search_results:
        

        try:
            date_string = result["pagemap"]["metatags"][0]["article:published_time"][:10]
        except:
            continue

        try:
            date_object = datetime.strptime(date_string, "%Y-%m-%d")
        except:
            continue
        end_date = datetime.strptime(date, "%d-%m-%Y")

        # Only include results before the specified date
        if date_object > end_date:
            continue
        
        link = result["link"]

        if not link:
            continue

        if link in visited or link.endswith((".pdf", ".doc", ".docx")):
            continue

        visited.add(link)

        results.append(link)
        #content = scrape_url_content(link)
        #results.append({"url": link, "content": content})

        if len(results) >= top_k:
            break

    return results
