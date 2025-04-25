from termcolor import colored
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langchain_core.runnables.config import RunnableConfig

from tools import list_files, create_folder, copy_folder
from constants import WellKnownRoles
from config import Config, ConfigKeys
from assistant import Assistant


def print_message(message: BaseMessage):
    color_for_role = {
        WellKnownRoles.SYSTEM: "blue",
        WellKnownRoles.USER: "white",
        WellKnownRoles.ASSISTANT: "yellow",
        WellKnownRoles.TOOL: "green",
    }

    role = message.type
    output_color = color_for_role[role]

    print(colored(f"{role}: {message.content}\n", output_color))


def get_system_prompt(config) -> SystemMessage:
    with open("calendar.prompt", "r") as file:
        calendar_prompt = file.read()
    with open("system.prompt", "r") as file:
        system_prompt = file.read()

    system_message = system_prompt.format(calendar=calendar_prompt)
    return SystemMessage(content=system_message)


def run(config=Config):
    assistant = Assistant(config)
    tools_node = ToolNode([list_files, create_folder, copy_folder])

    workflow = StateGraph(MessagesState)
    workflow.add_node("assistant", assistant.call)
    workflow.add_node("tools", tools_node)
    workflow.add_edge(START, "assistant")
    workflow.add_conditional_edges("assistant", tools_condition)
    workflow.add_edge("tools", "assistant")

    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)

    config = RunnableConfig(recursion_limit=10, configurable={
        "thread_id": "1",
        ConfigKeys.student_root: config.student_root,
        ConfigKeys.source_root: config.source_root
    })

    system_message = get_system_prompt(config)

    # initialize the agent with the system prompt
    app.update_state(config, {"messages": [system_message]}, as_node="assistant")

    while True:
        user_input = input(">> ")
        if user_input.lower().strip() == "done":
            break

        result = app.invoke({"messages": [HumanMessage(content=user_input)]},
                            config,
                            stream_mode="values")

        print_message(result["messages"][-1])
