from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv(dotenv_path=f'{os.path.dirname(__file__)}/../../.env')

class AgentState(TypedDict):
    message: List[HumanMessage]

FARM_API_KEY = os.environ["FARM_API_KEY"]

llm = ChatOpenAI(
    model = "gemini-2.0-flash-lite",
    base_url = os.environ["LLM_API_BASE"],
    api_key = "not-needed",
    default_headers = {"genaiplatform-farm-subscription-key": FARM_API_KEY}
)

def process(state: AgentState) -> AgentState:
    response = llm.invoke(state["message"])
    print(f'AI: {response.content}')
    return state

graph = StateGraph(AgentState)

graph.add_node("process", process)

graph.add_edge(START, "process")
graph.add_edge("process", END)

app = graph.compile()

#Print flow image
file_path_obj = Path(__file__)
flow_image = app.get_graph().draw_mermaid_png()

with open(f"{os.path.dirname(__file__)}/graph/{file_path_obj.stem}.png", "wb") as f:
    f.write(flow_image)

user_input = input("Enter: ")
while user_input != "exit":
    app.invoke({"message": [HumanMessage(content=user_input)]})
    user_input = input("Enter: ")