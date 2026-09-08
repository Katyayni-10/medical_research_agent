from typing import TypedDict
class MedicalState(TypedDict,total=False):
    query:str
    disease:str
    disease_info:str
    pubmed:str
    news:str
    analysis:str