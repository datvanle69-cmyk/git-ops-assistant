from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import os
from pathlib import Path

load_dotenv(dotenv_path=f'{os.path.dirname(__file__)}/../../.env')
FARM_API_KEY = os.environ["FARM_API_KEY"]


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

@tool
def add(a: int, b: int):
    """This is an additional function that adds 2 numbers together"""
    return a + b

@tool
def subtract(a: int, b: int):
    """Subtraction function"""
    return a - b

@tool
def multiply(a: int, b: int):
    """Multiplication function"""
    return a * b

tools = [add, subtract, multiply]

model = ChatOpenAI(
    model = "gemini-2.0-flash-lite",
    base_url = os.environ["LLM_API_BASE"],
    api_key ="not-needed",
    default_headers = {"genaiplatform-farm-subscription-key": FARM_API_KEY}
).bind_tools(tools)

def model_call(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content=
        "You are my AI assistant, please answer my query to the best of your quality."
    )
    response = model.invoke([system_prompt] + state["messages"])
    return {"messages": [response]}


def should_continue(state: AgentState):
    message = state["messages"]
    last_message = message[-1]

    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"

graph = StateGraph(AgentState)

graph.add_node("our_agent", model_call)

tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)

graph.set_entry_point("our_agent")

graph.add_conditional_edges(
    "our_agent",
    should_continue,
    {
        "continue": "tools",
        "end": END
    }
)
graph.add_edge("tools", "our_agent")

app = graph.compile()

#Print flow image
file_path_obj = Path(__file__)
flow_image = app.get_graph().draw_mermaid_png()

with open(f"{os.path.dirname(__file__)}/graph/{file_path_obj.stem}.png", "wb") as f:
    f.write(flow_image)

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

inputs = {"messages": [("user", "Add 40 + 12 and then multiply the result by 6. Also tell me a joke")]}
###
# Langchain automatically converts these simple (role, content) tuples into the proper message classes (HumanMessage, AIMessage, SystemMessage, etc.)
# There are many ways to define the message:
# inputs = {"messages": [HumanMessage(content="Add 40 + 12 and multiply by 6")]}
###

print_stream(app.stream(inputs, stream_mode="values"))