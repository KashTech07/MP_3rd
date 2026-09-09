from agent.graph import workflow


query = {
    "query": "What is the groundwater situation in Ghaziabad?",
    "district": "Ghaziabad"
}


result = workflow.invoke(query)

print(result["response"])