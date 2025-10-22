from typing import TypedDict, List, Union
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv(dotenv_path=f'{os.path.dirname(__file__)}/../../.env')

class AgentState(TypedDict):
    message: List[Union[HumanMessage, AIMessage]]

FARM_API_KEY = os.environ["FARM_API_KEY"]

llm = ChatOpenAI(
    model = "gemini-2.0-flash-lite",
    base_url = os.environ["LLM_API_BASE"],
    api_key ="not-needed",
    default_headers = {"genaiplatform-farm-subscription-key": FARM_API_KEY}
)

def process(state: AgentState) -> AgentState:
    response = llm.invoke(state["message"])
    state["message"].append(AIMessage(content=response.content))
    print(f'AI: {response.content}')

    #Learn how it's works
    #print("CURRENT STATE: ", state["message"])
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

conversation_history = []

user_input = input("Enter: ")
while user_input != "exit":
    conversation_history.append(HumanMessage(content=user_input))
    result = app.invoke({"message": conversation_history})
    conversation_history = result["message"]
    user_input = input("Enter: ")


with open('logging.txt', 'w') as file:
    file.write("Your conversation logs: \n")

    for message in conversation_history:
        if isinstance(message, HumanMessage):
            file.write(f"You: {message.content}\n")
        elif isinstance(message, AIMessage):
            file.write(f"AI: {message.content}\n")
    file.write("End of conversation")