import openai # type: ignore
from dotenv import load_dotenv # type: ignore
import os
_ = load_dotenv('./api_keys.env')

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_TYPE = os.getenv("OPENAI_API_TYPE")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
DEPLOYMENT = os.getenv("deployment")
MODEL = os.getenv("model")

openai.api_key= OPENAI_API_KEY
openai.api_type = OPENAI_API_TYPE
openai.api_base = OPENAI_API_BASE
openai.api_version = OPENAI_API_VERSION

