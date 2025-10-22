from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from pathlib import Path
import random

class AgentState(TypedDict):
    name: str
    guess: List[int]
    random_number: int
    lower_bound: int
    upper_bound: int


def setup(state: AgentState) -> AgentState:
    print(f'Hello {state["name"]}, please guess the number')
    state["random_number"] = (random.randrange(state["lower_bound"], state["upper_bound"]))
    return state

def guess(state: AgentState) -> AgentState:
    def get_number(start_number, end_number):
        duplicate = True
        while duplicate:
            guess_number = random.randrange(start_number, end_number)
            if guess_number not in state["guess"]:
                state["guess"].append(guess_number)
                break

    if len(state["guess"]) == 0:
        state["guess"].append(random.randrange(state["lower_bound"], state["upper_bound"]))
    else:
        if state["guess"][-1] > state["random_number"]:
            get_number(state["lower_bound"], state["guess"][-1])
        elif state["guess"][-1] < state["random_number"]:
            get_number(state["guess"][-1], state["upper_bound"])


    print("Guessing: " + str(state["guess"][-1]))
    return state 

def should_continue(state: AgentState) -> AgentState:
    if state["guess"][-1] == state["random_number"]:
        print("Bingo, correct number: " + str(state["guess"][-1]))
        return "exit"

    if len(state["guess"]) < 7:
        return "loop"
    else:
        print(f'You\'re lose !!! Random number: {state["random_number"]}')
        return "exit"

graph = StateGraph(AgentState)

graph.set_entry_point("setup")
graph.add_node("setup", setup)
graph.add_node("guess", guess)
graph.add_edge("setup", "guess")


graph.add_conditional_edges(
    "guess",
    should_continue,
    {
        "loop": "guess",
        "exit": END
    }
)

app = graph.compile()

#Print flow image
file_path_obj = Path(__file__)
flow_image = app.get_graph().draw_mermaid_png()

with open(f"graph/{file_path_obj.stem}.png", "wb") as f:
    f.write(flow_image)

#Answer
answer = app.invoke({"name" : "Linh", "guess" : [], "lower_bound" : 1, "upper_bound" : 50})