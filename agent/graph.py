from langgraph.graph import StateGraph, START, END

from agent.state import GroundwaterState
from agent.nodes import retrieve_data, analyze_data , generate_response


graph = StateGraph(GroundwaterState)

graph.add_node("retrieve_data", retrieve_data)
graph.add_node("analyze_data", analyze_data)
graph.add_node("generate_response" , generate_response)

graph.add_edge(START, "retrieve_data")
graph.add_edge("retrieve_data", "analyze_data")
graph.add_edge("analyze_data" , "generate_response")
graph.add_edge("generate_response", END)

workflow = graph.compile()