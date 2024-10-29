# pyTETA - Python Tech Elevator Teaching Assistant

pyTETA is an AI assistant to help manage the daily lecture materials. it is built on top of the OpenAI [Chat API](https://platform.openai.com/docs/api-reference/chat) and makes use of the APIs capability to use [tools](https://platform.openai.com/docs/guides/function-calling).

## OpenAI
An OpenAI Developer Platform account is required in order to use the Chat API. [Create an account](https://platform.openai.com/signup) if you don't already have one.

## Installation
### Python
Make sure that Python 3.8+ is installed. If necessary, the Python installer can be downloaded from [here](https://www.python.org/downloads/).

### Installing Dependencies
Create and activate a virtual environment prior to installing the dependencies. 
```bash
$ python -m venv ./venv
$ source ./venv/Scripts/Activate
```

> Note: The above command are appropriate for bash. Use the commands for your platform. Refer to the [Python docs](https://docs.python.org/3/library/venv.html) for more information

With the virtual environment activated, install the dependencies:
```bash
$ pip install -r requirements.txt
```

## Configuration
The assistant is configured using environment variables. There are a few values that are required:

| variable | description | example | Location |
| -- | -- | -- | -- |
| OPENAI_API_KEY | The OpenAI API key. The key can be created in the Platform's dashboard. It is recommended to create a key for each application. | sk-...1234 | 
| PYTETA_SOURCE_ROOT | The full path to the root of the lecture materials source. | c:/ ... /te-curriculum-full-time-2024.3/java | .env.config
| PYTETA_STUDENT_ROOT | The full path to the root of the instructor repo | c:/.../workspace/instructor-code | .env.config

There are also some optional values:
| variable | description | example | Location |
| -- | -- | -- | -- |
| OPENAI_MODEL | The name of the [OpenAI model](https://platform.openai.com/docs/models) to use | GPT-4o | .env.config |
| PYTETA_SHOW_TOOL_USAGE | report the tool and parameters that the model is requesting | true/false | .env.config |
| PYTETA_SHOW_TOOL_RESPONSE | report the response from tool usage | true/false | .env.config |

### Config locations
The environment variables can be set using whatever mechanism is convenient. Additionally, the assistant uses the [python-dotenv](https://pypi.org/project/python-dotenv/) package so variables can be written to either a `.env` or `.env.config` file. 

> Note: you will have to create the `.env` file if you wish to use it.

#### Location precedence
The precedence of locations is:
- environment (highest)
- `.env` file
- `.env.config` (lowest)

## Using the Assistant
To use the assistant, activate the virtual environment. Then run the agent with the following:
```bash
$ python pyteta
```
The assistant's prompt is `>>`.

### Verify the configuration
Use the following requests to verify the assistants configuration:
1. who are you?
1. can you reach the SOURCE folder?
1. can you reach the STUDENT folder?

Exit the assistant by typing `done` at the prompt.

