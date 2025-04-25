from tools import list_files, create_folder, copy_folder
from config import Config
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState

class Assistant:
    def __init__(self, config: Config):
        model = ChatOpenAI(model=config.model, temperature=config.temperature)
        self.model = model.bind_tools([list_files, create_folder, copy_folder])

    def call(self, state: MessagesState):
        messages = state["messages"]
        response = self.model.invoke(messages)
        return {"messages": state["messages"] + [response]}
