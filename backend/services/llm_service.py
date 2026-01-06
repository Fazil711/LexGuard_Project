from langchain_openai import ChatOpenAI
from langchain_classic.chains import RetrievalQA
from langchain_classic.prompts import PromptTemplate
from services.rag_service import get_retriever
import os

llm = ChatOpenAI(
    model_name="gpt-4o", 
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

def get_chat_response(case_id: str, user_query: str):
    """
    1. Fetches relevant documents from VectorDB (filtered by case_id if possible).
    2. Sends context + query to LLM.
    3. Returns the AI's response.
    """
    retriever = get_retriever()
    
    prompt_template = """
    You are LexGuard, an AI Corporate Lawyer for Indian businesses.
    Use the following pieces of context to answer the question at the end.
    If the answer is not in the context, say "I couldn't find that information in the uploaded documents."
    Do not make up legal advice.
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:
    """
    
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm, 
        chain_type="stuff", 
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT}
    )
    
    try:
        response = qa_chain.run(user_query)
        return response
    except Exception as e:
        print(f"Error in LLM generation: {e}")
        return "I encountered an error processing your request."