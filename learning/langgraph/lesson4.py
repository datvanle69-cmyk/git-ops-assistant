from typing import TypedDict, List
from langgraph.graph import StateGraph
from pathlib import Path

class AgentState(TypedDict):
    number1: int
    number2: int
    operator1: str
    operator2: str
    message: str

def add(state: AgentState) -> AgentState:
    result = state["number1"]+state["number2"]

    state["message"] = f'First math: {state["number1"]}+{state["number2"]}={result}\n'

    return state

def substration(state: AgentState) -> AgentState:
    result = state["number1"]/state["number2"]

    state["message"] = f'First math: {state["number1"]}/{state["number2"]}={result}\n'

    return state

def minus(state: AgentState) -> AgentState:
    result = state["number1"]-state["number2"]

    state["message"] += f'Second math: {state["number1"]}-{state["number2"]}={result}'

    return state

def multiply(state: AgentState) -> AgentState:
    result = state["number1"]*state["number2"]

    state["message"] += f'Second math: {state["number1"]}*{state["number2"]}={result}'

    return state

def decide_next_node1(state: AgentState) -> AgentState:
    if state["operator1"] == "+":
        return "add_operation"
    elif state["operator1"] == "/":
        return "substration_operation"


def decide_next_node2(state: AgentState) -> AgentState:
    if state["operator2"] == "-":
        return "minus_operation"
    elif state["operator2"] == "*":
        return "multiply_operation"

graph = StateGraph(AgentState)

graph.add_node("add_node",add)
graph.add_node("substration_node",substration)
graph.add_node("minus_node",minus)
graph.add_node("multiply_node",multiply)
graph.add_node("router1",lambda state:state)  #passthrough function 
graph.add_node("router2",lambda state:state)

graph.set_entry_point("router1")

graph.add_conditional_edges(
    "router1",
    decide_next_node1,
    {
        "add_operation": "add_node",
        "substration_operation": "substration_node"
    }
)

graph.add_edge("add_node", "router2")
graph.add_edge("substration_node", "router2")

graph.add_conditional_edges(
    "router2",
    decide_next_node2,
    {
        "minus_operation": "minus_node",
        "multiply_operation": "multiply_node"
    }
)

graph.set_finish_point("minus_node")
graph.set_finish_point("multiply_node")

app = graph.compile()

#Print flow image
file_path_obj = Path(__file__)
flow_image = app.get_graph().draw_mermaid_png()

with open(f"graph/{file_path_obj.stem}.png", "wb") as f:
    f.write(flow_image)

#Answer
answer = app.invoke({"number1" : 52, "number2" : 32, "operator1" : "+", "operator2" : "-"})
print(answer["message"])