import wikipedia
import requests
import os
import feedparser
from dotenv import load_dotenv
from Bio import Entrez

load_dotenv()
NEWS_API_KEY=os.getenv("NEWS_API_KEY")
Entrez.email=os.getenv("NCBI_EMAIL")

def wiki_disease(disease):
    try:
        return wikipedia.summary(disease,sentences=5)
    except Exception as e:
        return str(e)
    
def pubmed_search(disease):
    try:
        handle=Entrez.esearch(
            db="pubmed",
            term=disease,
            retmax=5
        )

        record=Entrez.read(handle)
        ids=record["IdList"]

        if not ids:
            return"No research paper found."
        
        handle=Entrez.efetch(
            db="pubmed",
            id=",".join(ids),
            rettype="abstract",
            retmode="text"
        )
        return handle.read()
    
    except Exception as e:
        return str(e)
    
def medical_news(disease):
    url="https://newsapi.org/v2/everything"
    params={
        "q":disease,
        "language":"en",
        "pageSize":5,
        "apiKey":NEWS_API_KEY
    }
    
    r=requests.get(url,params=params)
    data=r.json()
    articles=data.get("articles",[])

    if not articles:
        return "No news"
    return "\n".join(
        article["title"]
        for article in articles
    )