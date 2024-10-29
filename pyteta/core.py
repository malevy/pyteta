import json
import os
from openai import OpenAI, BadRequestError
from termcolor import colored
from enum import Enum

from tools import tool_descriptions, list_files, create_folder, copy_folder
from constants import MessageFields, WellKnownRoles
from config import Config


class States(Enum):
    CALL_MODEL = 1
    GET_USER_INPUT = 2
    CALL_FUNCTION = 3
    STOP = 4


conversation = []

def _print_message(message):
    color_for_role = {
        "system": "blue",
        "user": "white",
        "assistant": "yellow",
        "tool": "green",
    }

    role = message[MessageFields.ROLE]
    outputColor = color_for_role[role]
    content = message[MessageFields.CONTENT]

    if role == WellKnownRoles.ASSISTANT and message.get(MessageFields.TOOLCALLID):
        print(colored(f"{role}: {content}\n", outputColor))
    elif role == WellKnownRoles.TOOL:
        toolCallId = message[MessageFields.TOOLCALLID]
        print(colored(f"{role}: {content} tool_call_id: {toolCallId} \n", outputColor))
    else:
        print(colored(f"{role}: {content}\n", outputColor))


def _call_model(client, messages, tools=None, config=Config):

    try:
        response = client.chat.completions.create(
            model=Config.Model, messages=messages, tools=tools, tool_choice="auto"
        )
        return (
            response  # see https://platform.openai.com/docs/api-reference/chat/object
        )
    except BadRequestError as e:
        print(messages)
        raise e


def run(config = Config):
    with open("system.prompt", "r") as file:
        content = file.read()

    conversation.append(
        {MessageFields.ROLE: WellKnownRoles.SYSTEM, MessageFields.CONTENT: content}
    )

    client = OpenAI(api_key=config.ApiKey)

    next_state = States.GET_USER_INPUT
    toolCalls = []
    while True:

        match next_state:
            case States.STOP:
                return

            case States.GET_USER_INPUT:
                user_input = input(">> ")

                if user_input == "done":
                    next_state = States.STOP
                    continue

                conversation_message = {
                    MessageFields.ROLE: WellKnownRoles.USER,
                    MessageFields.CONTENT: user_input,
                    }

                conversation.append(conversation_message)

                next_state = States.CALL_MODEL

            case States.CALL_MODEL:
                conversation_message = {MessageFields.ROLE: WellKnownRoles.ASSISTANT}
                response = _call_model(client, conversation, tool_descriptions)
                modelChoice = response.choices[0]
                modelMessage = modelChoice.message

                if modelChoice.finish_reason == "tool_calls":
                    content = "using\n"
                    toolCalls = []
                    for tc in modelMessage.tool_calls:
                        content += f"\t{tc.function.name}({tc.function.arguments})\n"
                        toolCalls.append(
                            {
                                "id": tc.id,
                                "name": tc.function.name,
                                "arguments": json.loads(tc.function.arguments),
                            }
                        )

                    conversation_message[MessageFields.TOOLCALLS] = (
                        # the model returned a 400 error reporting that the tool_calls property
                        # was required even though the docs have it marked as optional
                        modelMessage.tool_calls
                    )
                    conversation_message[MessageFields.CONTENT] = content

                    if (config.ShowToolUsage):
                        _print_message(conversation_message)

                    next_state = States.CALL_FUNCTION
                else:
                    conversation_message[MessageFields.CONTENT] = modelMessage.content
                    _print_message(conversation_message)
                    next_state = States.GET_USER_INPUT
                    
                conversation.append(conversation_message)

            case States.CALL_FUNCTION:
                for tc in toolCalls:
                    response = None
                    if tc["name"] == "ListFiles":
                        response = list_files(tc["arguments"])
                    elif tc["name"] == "CopyFolder":
                        response = copy_folder(tc["arguments"])
                    elif tc["name"] == "CreateFolder":
                        response = create_folder(tc["arguments"])
                    else:
                        response = {
                            "status": "error",
                            "message": f"unknown tool: {tc["name"]}",
                        }

                    conversation_message = {
                        MessageFields.ROLE : WellKnownRoles.TOOL,
                        MessageFields.TOOLCALLID: tc["id"],
                        MessageFields.CONTENT: str(response)
                        }

                    if config.ShowToolResponses:
                        _print_message(conversation_message) 

                    conversation.append(conversation_message)

                next_state = States.CALL_MODEL
