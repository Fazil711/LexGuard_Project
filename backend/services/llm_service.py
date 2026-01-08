from langchain_openai import ChatOpenAI
from langchain_classic.chains import RetrievalQA
from langchain_classic.prompts import PromptTemplate
from services.rag_service import get_retriever
import os
import json
from langchain_classic.schema import HumanMessage, SystemMessage
import openai

llm = ChatOpenAI(
    model_name="gpt-4o", 
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)
'''
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
'''
def get_chat_response(case_id: str, user_query: str):
    retriever = get_retriever(case_id=case_id)
    
    try:
        retrieved_docs = retriever.invoke(user_query) 
        print(f"\n🔍 DEBUG: Retrieved {len(retrieved_docs)} chunks for query: '{user_query}'")
        for i, doc in enumerate(retrieved_docs):
            print(f"   Chunk {i+1}: {doc.page_content[:100]}...") 
    except Exception as e:
        print(f"⚠️ DEBUG Error retrieving docs: {e}")

    prompt_template = """
    You are LexGuard, an AI Corporate Lawyer.
    Use the provided legal context to answer the question.
    If the answer is not in the context, say "I couldn't find that information in the documents."
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:
    """
    
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm, 
        chain_type="stuff", 
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT}
    )
    
    return qa_chain.run(user_query)

def analyze_document_text(text_content: str):
    """
    Sends document text to LLM to extract structured legal metadata.
    Returns a Python dictionary (JSON).
    """
    system_prompt = """
    You are an experienced Indian corporate lawyer. 
    Analyze the legal document text provided and return a STRICT JSON object with these keys:
    - parties (list of strings)
    - agreement_type (string)
    - termination_clause (summary string)
    - payment_terms (summary string)
    - liability_indemnity (summary string)
    - risk_rating (High/Medium/Low)
    - key_risks (list of strings)
    
    Do not add markdown formatting (like ```json). Just return the raw JSON string.
    """
    
    truncated_text = text_content[:15000]
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Document Text:\n{truncated_text}")
    ]
    
    try:
        response = llm.invoke(messages)
        content = response.content.strip()
        
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "")
            
        return json.loads(content)
    except Exception as e:
        print(f"Error analyzing document: {e}")
        return {"error": "Failed to analyze document"}
    
def generate_case_strategy(case_summary: str, doc_analyses: list):
    """
    Generates a legal strategy based on case details and analyzed documents.
    """
    system_prompt = """
    You are a Senior Legal Strategist. Based on the case summary and document analysis provided, 
    output a strategic plan in JSON format with:
    - summary (brief overview)
    - safe_plan (list of conservative steps)
    - aggressive_plan (list of assertive steps)
    - missing_documents (what else is needed)
    """
    
    user_content = f"""
    CASE SUMMARY: {case_summary}
    
    DOCUMENT ANALYSES:
    {json.dumps(doc_analyses, indent=2)}
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_content)
    ]
    
    response = llm.invoke(messages)
    return response.content

def transcribe_audio(file_path: str):
    """
    Uses OpenAI Whisper API to convert audio file to text.
    """
    try:
        with open(file_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        return transcript.text
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None