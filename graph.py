from langgraph.graph import StateGraph,START,END
from state import MedicalState
from nodes import *
builder=StateGraph(MedicalState)
builder.add_node("resolve",resolve_disease)
builder.add_node("wiki",get_disease_info)
builder.add_node("pubmed",get_pubmed)
builder.add_node("news",get_news)
builder.add_node("analysis",generate_analysis)
builder.add_edge(START,"resolve")
builder.add_edge("resolve","wiki")
builder.add_edge("wiki","pubmed")
builder.add_edge("pubmed","news")
builder.add_edge("news","analysis")
builder.add_edge("analysis",END)
graph=builder.compile()