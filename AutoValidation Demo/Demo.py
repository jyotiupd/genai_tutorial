import gradio as gr
from openai import ChatCompletion
from get_env_config import *

def eval_ai(output_context, output_instructions, output, evaluation_criteria, evaluation_points):
    system_prompt_template = f"""
    You are a LLM evaluator. Your task is to evaluate the given Model Output based on the Context, Instructions.

    Answer the following questions for the given output - 
    
    ```{evaluation_criteria}```
    
    Based on the points system below for the possible answers to the above questions, calculate the final score for the above answers given by you. (output a number):
    
    ```{evaluation_points}```
    
    In your Output share the Question, it's answer, corresponding score, and the final score for the evaluation.
    Add the Max Possible Score based on the questions at the bottom of your output.
    """
    user_prompt = f"""
    
    Context: ```{output_context}```
    
    Instructions: ```{output_instructions}
    
    Model Output: ```{output}```
    
    Utilize the Context, and Instructions for your output only if they don't say ```Not Required```.
    
    """
    
    msgs = [{"role":"system","content":system_prompt_template},
            {"role":"user","content":user_prompt}]
    
    eval_output = ChatCompletion.create(model = model, deployment_id=deployment_id,temperature = 0.0,messages=msgs)
    eval_output = eval_output['choices'][0]['message']['content']
    
    return system_prompt_template, user_prompt, eval_output 
    

with gr.Blocks() as Demo:
    gr.Markdown("# Auto Validaion using LLMs Demo")
    with gr.Row():
        with gr.Column():
            OUTPUT_CONTEXT = gr.TextArea("Please insert the Context for which the output was generated",lines=20,label="Output Context")
            OUTPUT_INSTRUCTIONS = gr.TextArea("Please insert the Instructions based on which the output was generated",lines=5,label="Output Instructions")
            OUTPUT = gr.TextArea("Please insert the output generated here",lines=3,label="Output to be Evaluated")
            EVALUATION_CRITERIA = gr.TextArea("Please insert the rubrics questions here",lines=10,label="Evaluation Criteria")
            EVALUATION_POINTS = gr.TextArea("Please insert the rubrics points to be assigned here",lines=10,label="Evaluation Points")
            submit = gr.Button("Evaluate")
        with gr.Column():
            SYSTEM_PROMPT = gr.TextArea("This is where we see the System Output Prompt",lines=20,label="System Prompt")
            USER_PROMPT = gr.TextArea("This is where we see the User Output Prompt",lines=20,label="User Prompt")
            EVAL_OUTPUT = gr.TextArea("This is where we can see the Evaluation Output",lines=10,label="Evaluation Output")
         
        submit.click(eval_ai,inputs=[OUTPUT_CONTEXT,OUTPUT_INSTRUCTIONS,OUTPUT,EVALUATION_CRITERIA,EVALUATION_POINTS], 
                         outputs=[SYSTEM_PROMPT,USER_PROMPT,EVAL_OUTPUT])

Demo.launch()