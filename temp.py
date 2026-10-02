from agent.graph import workflow

result = workflow.invoke({
    "query": "analyze ground level water of agra?"
})

print(result["response"])