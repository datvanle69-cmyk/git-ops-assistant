from pathlib import Path

from typing import Dict, TypedDict
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    message: str

def chat(state: AgentState) -> AgentState:

    state['message'] = "Hey" + state["message"] + ", how is your day going?"

    return state


graph = StateGraph(AgentState)
graph.add_node("greeter",chat)
graph.set_entry_point("greeter")
graph.set_finish_point("greeter")

app = graph.compile()

#Print flow image
file_path_obj = Path(__file__)
flow_image = app.get_graph().draw_mermaid_png()

with open(f"graph/{file_path_obj.stem}.png", "wb") as f:
    f.write(flow_image)