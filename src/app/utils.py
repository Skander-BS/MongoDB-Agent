from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import time

def chat_title_generator(msg: str) -> str:
    """Generates title for each chat session"""
    llm = ChatGroq(
        model="llama3-70b-8192",
        temperature=0.3,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    prompt = PromptTemplate(
        input_variables=["msg"],
        template="Based on the user Message: '{msg}', generate a very short title that summarizes the query in 3 to 5 words, and do not geenrate any quotes or markdowns"
    )   
    chain = prompt | llm
    output = chain.invoke({"msg": msg}).content
    return output

def response_generator(api_response: dict):
    """Util function for handling streaming"""
    response_text = api_response.get("result", "")
    for word in response_text.split():
        yield word + " "
        time.sleep(0.05)