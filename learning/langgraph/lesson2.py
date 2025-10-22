from typing import TypedDict, List
from langgraph.graph import StateGraph
from pathlib import Path

class AgentState(TypedDict):
    name: str
    values: List[int]
    operator: str
    result: str

def proccessor(state: AgentState) -> AgentState:
    total = processing(state["values"], state["operator"])

    state["result"] = f'Hello {state["name"]}, your answer is {total}'
    
    return state

def processing(list_values: List[int], operator: str) -> int:
    len_of_list = len(list_values)
    if(operator == "+"):
        total = 0
        for i in range(len_of_list):
            total = total + list_values[i]
    elif(operator == "*"):
        total = 1
        for i in range(len_of_list):
            total = total * list_values[i]
    return total

graph = StateGraph(AgentState)
graph.add_node("proccessor",proccessor)
graph.set_entry_point("proccessor")
graph.set_finish_point("proccessor")

app = graph.compile()

#Print flow image
file_path_obj = Path(__file__)
flow_image = app.get_graph().draw_mermaid_png()

with open(f"graph/{file_path_obj.stem}.png", "wb") as f:
    f.write(flow_image)

#Answer
answer = app.invoke({"name" : "Linh", "values" : [1,2,3,4], "operator" : "+"})
print(answer["result"])