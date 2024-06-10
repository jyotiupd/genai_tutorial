import openai
from dotenv import load_dotenv, find_dotenv
import os
import json
_ = load_dotenv('./api_keys.env')

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_TYPE = os.getenv("OPENAI_API_TYPE")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")

openai.api_key= OPENAI_API_KEY
openai.api_type = OPENAI_API_TYPE
openai.api_base = OPENAI_API_BASE
openai.api_version = OPENAI_API_VERSION

model_config = open("./model_config.json")
model_json = json.load(model_config)
deployment_id = model_json["deployment_id"]
model = model_json["model"]