import os
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader
from langchain.chat_models import ChatOpenAI
from getpass import getpass
os.environ['OPENAI_API_KEY'] = getpass("OpenAI Key:")

# Load and process the text files
# loader = TextLoader('single_text_file.txt')
loader = DirectoryLoader('C:\\Users\\423920\\Downloads\\kantar\\Kantar_v8_Public_Beta1', glob="qa_example.txt", loader_cls=TextLoader)
documents = loader.load() #2947

#splitting the text into
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

# Embed and store the texts
# Supplying a persist_directory will store the embeddings on disk
persist_directory = 'db'

## here we are using OpenAI embeddings but in future we will swap out to local embeddings
embedding = OpenAIEmbeddings()

vectordb = Chroma.from_documents(documents=texts,
                                 embedding=embedding,
                                 persist_directory=persist_directory)

vectorstore = Chroma.from_documents(documents=texts, embedding=OpenAIEmbeddings())
# persiste the db to disk
vectordb.persist()
vectordb = None

# Now we can load the persisted database from disk, and use it as normal.
vectordb = Chroma(persist_directory=persist_directory,
                  embedding_function=embedding)

retriever = vectordb.as_retriever()

#llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
# create the chain to answer questions
qa_chain = RetrievalQA.from_chain_type(llm=OpenAI(),
                                  chain_type="stuff",
                                  retriever=retriever,
                                  return_source_documents=True)
#'text-davinci-003'
#example 1
query = "what is the main comparison between American workers and Japanese workers?"
llm_response = qa_chain(query)
process_llm_response(llm_response)
print(llm_response)

#example 2
query = "why American corporations not able to beat other competitors"
llm_response = qa_chain(query)
# process_llm_response(llm_response)
print(llm_response)

#example 3
query = "does recent mergers helped"
llm_response = qa_chain(query)
# process_llm_response(llm_response)
print(llm_response)