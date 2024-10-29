import os
from dotenv import load_dotenv

load_dotenv(".env.config")
load_dotenv()

import core

core.run()
