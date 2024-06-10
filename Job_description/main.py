import openai# type: ignore
import uvicorn# type: ignore
import warnings
import json
import os
from fastapi import FastAPI, Request# type: ignore
from fastapi.staticfiles import StaticFiles# type: ignore
from fastapi.templating import Jinja2Templates# type: ignore
from pydantic import BaseModel# type: ignore
from fastapi.middleware.cors import CORSMiddleware# type: ignore
from langchain import LLMChain, PromptTemplate #type:ignore
from langchain.chat_models import AzureChatOpenAI #type:ignore
import openai#type:ignore
from get_env_config import *


origins = [ 
           "http://localhost:8000",
           "http://127.0.0.1:8000"
] 

class Data(BaseModel):
    query: str

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static") 
templates = Jinja2Templates(directory="templates")

app.add_middleware( 
    CORSMiddleware, 
    allow_origins=origins, 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"], 
) 

jd_llm = AzureChatOpenAI(temperature=0.5, deployment_name=DEPLOYMENT, model_name=MODEL, verbose=True) # type: ignore
jq_llm = AzureChatOpenAI(temperature=0.9, deployment_name=DEPLOYMENT, model_name=MODEL, verbose=True) # type: ignore

jd_prompt_template = PromptTemplate(
    input_variables=['requirements'],
    template="""As an expert human resource, you get new hiring requirements. You are skilled in creating Job 
    description with information given in the {requirements}.

    When creating a job description, it is important to make it appealing to encourage individuals with the relevant skills to apply.
    At the same time, it should subtly discourage those who do not meet the requirements from applying. 

    The requirements are provided below, delimited by ```

    ```{requirements}```
    
    Template for job description.
        **About the company:** \n
        Cognizant is a leading provider of information technology, consulting, and business process services. Our passion is helping clients worldwide build stronger businesses and maximize their competitive performance through innovative technologies and processes. Headquartered in Teaneck, New Jersey (U.S.), Cognizant combines a passion for client satisfaction, technology innovation, deep industry and business process expertise, and a global, collaborative workforce that embodies the future of work.
        
        Job title 
        
        Job summary
        
        Experience
        
        Technical skills
        
        Qualification
        
        Responsibilities
        
        Domain Experience
        
    
    Elaborate each section in the template in detail with words and bullet points.
    Responsibilities section should have atleast 10 bullet points for candidate having experience greater than 5.
    Elaborate domain expertise as well with 5 bullet points.
    And mention the percentage in all the academics should be greater than 70 in qualification section.
    Mention neat conclusion point at the end of job description to apply only who are relevant and ignore for the rest.
    
    Provide the output in the form of Markdown document.
    Use ** to make text bold.
    """)
jq_prompt_template = PromptTemplate(
    input_variables=['requirements'],
    template="""
    As an expert human resource, you get new hiring requirements. 
    You are skilled in creating technical interview questions and domain interview questions with information provided in requirements like technical skills and domain expertise.

    When creating interview questions, the technical questions complexity should vary based on the total experience provided.
    For total experience greater than 5 years give techincal questions from advanced or complex topics and who has total experience less than 5 years provide less complex technical questions.
    Generate 15 interview questions along with answers, 10 techical questions and 5 domain questions.

    The requirements are provided below, delimited by ```
    ```{requirements}```

    Provide the output in the form of Markdown document.
    Use ** to make text bold.
    """)

jd_chain = LLMChain(llm=jd_llm, prompt=jd_prompt_template, verbose=True)
jq_chain = LLMChain(llm=jd_llm, prompt=jq_prompt_template, verbose=True)

@app.get("/", status_code=200)
def root(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})

@app.post("/get_jd")
def get_jd(data:Data):
    query = data.query
    result = jd_chain.run(query)
    return (json.dumps({'success':True,'message':"Job description Created","result":result}), 200, {'ContentType':'application/json'})

@app.post("/get_question")
def get_question(data:Data):
    query = data.query
    result = jq_chain.run(query)
    return (json.dumps({'success':True,'message':"Job question Created","result":result}), 200, {'ContentType':'application/json'})

if __name__=="__main__":
    uvicorn.run('main:app',host="127.0.0.1", port=8000,reload=False)