from flask import Flask, render_template, request, send_from_directory, jsonify, send_file
import langchain
import openai
#import streamlit as st
#import streamlit_chat
import tiktoken
# import chromadb
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import json
from langchain.memory import ConversationBufferMemory
import openai
import os
from flask_cors import CORS
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma

app = Flask(__name__)
CORS(app)
os.environ["OPENAI_API_KEY"] = ''
openai.api_key = ''


# print(db.table_info)


@app.route('/')
def index():
    return open('templates/index.html')


@app.route('/ask', methods=['POST'])
def ask():
    try:
        user_input = request.json.get('question', '')
        print(user_input)
        loader = WebBaseLoader("https://www.flipkart.com/pages/returnpolicy")
        data = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
        all_splits = text_splitter.split_documents(data)
        vectorstore = FAISS.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())
        memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True)

        chain = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(temperature=0.0, model_name='gpt-3.5-turbo'),
            retriever=vectorstore.as_retriever(),
            memory=memory,
        )
        history = []

        answer = chain({"question": user_input, "chat_history": history})["answer"]
        print(answer)
        return jsonify({"answer": answer})
    except BaseException as error:
        print('An exception occurred: {}'.format(error))


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)