import openai
import json
import ast
import os
import chainlit as cl
import requests
import os
import io


from langchain.tools.python.tool import PythonAstREPLTool

import pandas as pd

#from codeboxapi import CodeBox

os.environ["OPENAI_API_KEY"] =   ""  
openai.api_key = os.getenv("OPENAI_API_KEY")

MAX_ITER = 15

def repl_tool_fun(code, balance_sheet_df, income_statement_df, cashflow_statement_df):
    python_repl = PythonAstREPLTool(locals={"balance_sheet_df": balance_sheet_df, "income_statement_df":income_statement_df,  "cashflow_statement_df":cashflow_statement_df})
    output= python_repl.run(code)
    return str(output)



functions =[
    {'name': 'run_python_code',
 'description': 'Useful when you need to run python code for doing data analysis and for checking discrepencies in financial statements. Remember. You have access to required dataframes',
 'parameters': {'title': 'pythoncode',
  'description': 'python code that needs to be run',
  'type': 'object',
  'properties': {'Code': {'title': 'Code',
    'description': 'Python code for doing data analysis and for checking discrepencies in financial statements. code always start importing pandas. ',
    'type': 'string'}}
 }}
]



async def process_new_delta(new_delta, openai_message, content_ui_message, function_ui_message):
    if "role" in new_delta:
        openai_message["role"] = new_delta["role"]
    if "content" in new_delta:
        new_content = new_delta.get("content") or ""
        openai_message["content"] += new_content
        await content_ui_message.stream_token(new_content)
    if "function_call" in new_delta:
        if "name" in new_delta["function_call"]:
            openai_message["function_call"] = {
                "name": new_delta["function_call"]["name"]}
            await content_ui_message.send()
            function_ui_message = cl.Message(
                author=new_delta["function_call"]["name"],
                content="", indent=1, language="json")
            await function_ui_message.stream_token(new_delta["function_call"]["name"])

        if "arguments" in new_delta["function_call"]:
            if "arguments" not in openai_message["function_call"]:
                openai_message["function_call"]["arguments"] = ""
            openai_message["function_call"]["arguments"] += new_delta["function_call"]["arguments"]
            await function_ui_message.stream_token(new_delta["function_call"]["arguments"])
    return openai_message, content_ui_message, function_ui_message



@cl.on_chat_start
async def start_chat():
    files = None

    while files == None:
        files = await cl.AskFileMessage(
            content="Please upload a csv file to begin!", accept=["csv", ".xlsx"]
        ).send()

    file = files[0]
    csv_file = io.BytesIO(file.content)

    xls = pd.ExcelFile(csv_file, engine='openpyxl')
    sheet_names = xls.sheet_names

    all_data = {}
    for sheet in sheet_names:
        all_data[sheet] = pd.read_excel(xls, sheet_name=sheet)

    file_name = file.name
    with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
        for sheet, data in all_data.items():
            data.to_excel(writer, sheet_name=sheet, index=False)

    column_info = {}
    for sheet, data in all_data.items():
        column_info[sheet] = list(data.columns)

    top_5_rows_str = {}
    for sheet, df in all_data.items():
        top_5_rows_str[sheet] = str(df.head())

    # Load the sheets into dataframes

    balance_sheet_df = pd.read_excel(xls, sheet_names[0])
    income_statement_df = pd.read_excel(xls, sheet_names[1])
    cashflow_statement_df = pd.read_excel(xls, sheet_names[2])


    message_content = f"You are an accounting analyst named Adam who reconciles financial statements for any discrepancies. You always use available tools for data analysis, focusing solely on discrepancies. Note that variables are not persisted across runs, so you must start from scratch to load the data and variables each time. "

    for sheet, columns in column_info.items():
        message_content += f"\n\nFor the {sheet} sheet, the columns are: {columns}. Follow these steps:\n"
        message_content += "1. Start by importing pandas, check first 5 rows of each dataframe and review names of metrics we have in different tabs/dataframes.\n"
        message_content += "2. After reviewing the financial metrics or items in each sheet, create a plan in natural language (you don't need to write code in plan but should be natural language plan for python tool) outlining which discrepancies you need to check.\n"
        message_content += "3. Use the Python tool to execute the plan one by one. in python tool always start with loading the data again as variables will not be persisted\n"
        message_content += "4. At the end, summarize any discrepancies found."

    msg = cl.Message(content=f"File Uploaded Successfully. You can ask questions now.")
    await msg.send()
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": message_content},
        {"role": "user", "content": f"You have access to 3 dataframe balance_sheet_df, income_statement_df, cashflow_statement_df. You need to always use these 3 dataframes for analysis"},
        {"role": "assistant", "content": "Ok. You can ask your questions now."}]
    )

    cl.user_session.set(
        "balance_sheet_df",
        balance_sheet_df
    )

    cl.user_session.set(
        "income_statement_df",
        income_statement_df
    )

    cl.user_session.set(
        "cashflow_statement_df",
        cashflow_statement_df
    )




@cl.on_message
async def run_conversation(user_message: str):
    message_history = cl.user_session.get("message_history")

    balance_sheet_df = cl.user_session.get("balance_sheet_df")
    income_statement_df = cl.user_session.get("income_statement_df")
    cashflow_statement_df = cl.user_session.get("cashflow_statement_df")


    print(len(message_history), 'at start:')

    print(message_history)


    filename = 'downloaded_image.png'
    if os.path.exists(filename):
        try:
            os.remove(filename)
            print(f"{filename} has been deleted.")
        except Exception as e:
            print(f"Error while deleting {filename}: {str(e)}")
    else:
        print(f"{filename} does not exist.")

    if len(message_history) > 12:
        del message_history[3:5]


    message_history.append({"role": "user", "content": user_message})

    cur_iter = 0

    while cur_iter < MAX_ITER:

        # OpenAI call
        openai_message = {"role": "", "content": ""}
        function_ui_message = None
        content_ui_message = cl.Message(content="")
        async for stream_resp in await openai.ChatCompletion.acreate(
            #model="gpt-3.5-turbo-0613",
            model="gpt-4-0613",
            messages=message_history,
            stream=True,
            function_call="auto",
            functions=functions,
            temperature=0
        ):

            new_delta = stream_resp.choices[0]["delta"]
            openai_message, content_ui_message, function_ui_message = await process_new_delta(
                new_delta, openai_message, content_ui_message, function_ui_message)

        message_history.append(openai_message)
        if function_ui_message is not None:
            await function_ui_message.send()

        if stream_resp.choices[0]["finish_reason"] == "stop":
            break

        elif stream_resp.choices[0]["finish_reason"] != "function_call":
            raise ValueError(stream_resp.choices[0]["finish_reason"])

        # if code arrives here, it means there is a function call

        print(openai_message)

        function_name = openai_message.get("function_call").get("name")
        arguments = ast.literal_eval(
            openai_message.get("function_call").get("arguments"))

        print(function_name)

        print(arguments)

        if function_name=='run_python_code':
            try:
                function_response = repl_tool_fun(arguments.get("Code"), balance_sheet_df,income_statement_df,cashflow_statement_df)
            except:
                function_response = repl_tool_fun(arguments.get("Code"), balance_sheet_df, income_statement_df,cashflow_statement_df)


        message_history.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )

        await cl.Message(
            author=function_name,
            content=str(function_response),
            language="json",
            indent=1,
        ).send()

        filename = 'downloaded_image.png'
        if os.path.exists(filename):

            elements = [cl.Image(name="image_1", display="inline",size = "large", path="./downloaded_image.png")]

            await cl.Message(content="Chart:", elements=elements).send()
        # else:
        #     print("inside else 230 .............")


        #Delete the image


        # if message_history[-1]['role']=='function':
        #     message_history[-1]['content']= ""


        cur_iter += 1

        # #print(message_history)
        # print(len(message_history))
