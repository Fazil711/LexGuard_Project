import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings 
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import RetrievalQA
from langchain_classic.memory import ConversationBufferMemory
from dotenv import load_dotenv
from langchain_classic.agents import initialize_agent, Tool, AgentType
from datetime import datetime
import pandas as pd

def load_documents(file_paths):
    docs = []
    dataframes = []
    
    for path in file_paths:
        try:
            if path.endswith(".pdf"):
                loader = PyPDFLoader(path)
                docs.extend(loader.load())
            
            elif path.endswith(".txt"):
                try:
                    loader = TextLoader(path, encoding='utf-8')
                    docs.extend(loader.load())
                except UnicodeDecodeError:
                    loader = TextLoader(path, encoding='latin-1')
                    docs.extend(loader.load())

            elif path.endswith(".csv"):
                try:
                    df = pd.read_csv(path, encoding='utf-8')
                except UnicodeDecodeError:
                    df = pd.read_csv(path, encoding='latin-1')
                dataframes.append(df)
            
            elif path.endswith(".xlsx"):
                df = pd.read_excel(path)
                dataframes.append(df)
                
        except Exception as e:
            print(f"Error loading {path}: {e}") 
            continue 
            
    return docs, dataframes

def split_documents(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return text_splitter.split_documents(docs)


def create_vector_db(splits):
    if not splits:
        return None 
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    vectordb = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    return vectordb

def setup_agent(vectordb, dataframes=None, model_choice="OpenAI GPT-4o"):
    if model_choice == "OpenAI GPT-4o":
        llm = ChatOpenAI(
            model_name="gpt-4o", 
            temperature=0
        )

    tools = []
    
    if vectordb:
        retriever = vectordb.as_retriever(search_kwargs={"k": 3})
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm, 
            chain_type="stuff", 
            retriever=retriever
        )
        rag_tool = Tool(
            name="Personal Knowledge Base",
            func=qa_chain.run,
            description=(
                "Useful for answering questions based on the uploaded documents. "
                "IMPORTANT: Do not pass generic terms like 'document', 'file', or 'what is this' to this tool. "
                "Instead, paraphrased the query to be specific. "
                "Example: If user asks 'what is this?', input 'Summarize the main topics of the document'. "
                "Example: If user asks 'explain', input 'Explain the core concepts found in the text'."
            )
        )
        tools.append(rag_tool)


    memory = ConversationBufferMemory(
        memory_key="chat_history", 
        return_messages=True
    )

    agent_kwargs = {
        "prefix": (
            "You have access to the following tools:\n\n"
            "{tools}\n\n"
        )
    }

    agent = initialize_agent(
        tools, 
        llm, 
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, 
        verbose=True,
        memory=memory,
        agent_kwargs=agent_kwargs, 
        handle_parsing_errors=True,
        max_iterations=3
    )
    
    return agent