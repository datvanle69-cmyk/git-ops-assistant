from typing import TypedDict, List
from langgraph.graph import StateGraph
from pathlib import Path

class AgentState(TypedDict):
    message: str
    name: str
    age: int
    skills: List


def first_node(state: AgentState) -> AgentState:
    state["message"] = f'Hello {state["name"]}'
    return state

def second_node(state: AgentState) -> AgentState:
    state["message"] += f', you\'re age is {state["age"]}'
    return state

def third_node(state: AgentState) -> AgentState:
    str_skill = ""
    for skill in state["skills"]:
        str_skill += f" {skill}"
    state["message"] += f', you\'re skill is{str_skill}'

    return state

graph = StateGraph(AgentState)
graph.set_entry_point("first_node")
graph.add_node("first_node",first_node)
graph.add_node("second_node",second_node)
graph.add_node("third_node",third_node)
graph.add_edge("first_node", "second_node")
graph.add_edge("second_node", "third_node")
graph.set_finish_point("third_node")

app = graph.compile()

#Print flow image
file_path_obj = Path(__file__)
flow_image = app.get_graph().draw_mermaid_png()

with open(f"graph/{file_path_obj.stem}.png", "wb") as f:
    f.write(flow_image)

#Answer
answer = app.invoke({"name" : "Linh", "age" : 28, "skills" : ["DevOps", "AI"]})
print(answer["message"])