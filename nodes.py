from langchain_groq import ChatGroq
from tools import *
llm=ChatGroq(model="qwen/qwen3.6-27b",reasoning_effort="none",max_tokens=900)

def resolve_disease(state):
    prompt=f"""Find the disease or medical condition in the sentence.
    Return only
    DISEASE: <disease>
    Sentence: {state["query"]}
    """
    text=llm.invoke(prompt).content
    disease=text.split(":")[1].strip()
    return {"disease":disease}

def get_disease_info(state):
    return{
        "disease_info":wiki_disease(state["disease"])
    }

def get_pubmed(state):
    return{
        "pubmed":pubmed_search(state["disease"])
    }

def get_news(state):
    return{
        "news":medical_news(state["disease"])
    }

def generate_analysis(state):
    prompt=f"""You are an experienced medical researcher. Using only the following information, prepare a structured report.
    Disease: {state["disease"]}
    Wikipedia {state["disease_info"]}
    Research Papers {state["pubmed"]}
    Medical News {state["news"]}
    Generate
    1 Overview
    2 Symptoms
    3 Causes
    4 Treatments
    5 Recent Research
    6 Latest News
    7 Lifestyle Advice
    8 Disclaimer
    """
    return{
        "analysis":llm.invoke(prompt).content
    }