import json
import os
import re
from pymongo import MongoClient
from langchain.agents import Tool, initialize_agent
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv

class MongoDBAgent:
    def __init__(self):
        load_dotenv()
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_model = os.getenv("GROQ_MODEL")
        self.mongodb_uri = os.getenv("MONGODB_URI")
        self.mongodb_db = os.getenv("MONGODB_DB")
        self.mongodb_collection = os.getenv("MONGODB_COLLECTION")
        
        self.client = MongoClient(self.mongodb_uri)
        self.db = self.client[self.mongodb_db]
        self.collection = self.db[self.mongodb_collection]
        
        self.mongo_prompt = PromptTemplate(
            input_variables=["natural_query", "sample_doc_info", "collection"],
            template=(
                "Below is a sample document from the target NoSQL database collection '{collection}':\n\n"
                "{sample_doc_info}\n\n"
                "Using the above sample document as a reference for the data structure, "
                "convert the following natural language query into a valid MongoDB query in JSON format. "
                "The JSON object must include a 'find' key with the exact value '{collection}', a 'filter' key for filtering, "
                "and optionally a 'projection' key. For array fields, if you want to return only a subset (e.g. the last element), "
                "place the $slice operator inside the projection, not in the filter.\n\n"
                "Natural Language Query: {natural_query}\n"
                "Output only the MongoDB query in JSON format, with all keys quoted, no trailing commas, and no additional text or explanations.\n\n"
                "MongoDB Query (in JSON):"
            )
        )
        
        self.llm = ChatGroq(
            model=self.groq_model,
            temperature=0.3,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        
        self.llm_chain = LLMChain(llm=self.llm, prompt=self.mongo_prompt)
        
        self.mongodb_tool = Tool(
            name="NoSQL Query Tool",
            func=self.query_nosql,
            description=(
                "Converts a natural language query into a NoSQL query using a Groq LLM, "
                "Counts, sums and makes any operation on a MongoDB Database related to a user query"
                "executes it on the database, and returns the matching documents."
            )
        )
        
        self.agent = initialize_agent(
            tools=[self.mongodb_tool],
            llm=self.llm,
            agent="zero-shot-react-description",
            verbose=True,
        )
    
    def query_nosql(self, natural_query: str) -> str:
        """Converts a natural language query into a MongoDB query, executes it, and returns the results."""
        sample_doc = self.collection.find_one()
        if not sample_doc:
            return "No documents found in the collection to derive a schema."
        sample_doc_info = json.dumps(sample_doc, default=str, indent=2)
        
        generated_query_str = self.llm_chain.run(
            natural_query=natural_query,
            sample_doc_info=sample_doc_info,
            collection=self.mongodb_collection  
        )
        
        cleaned_query_str = generated_query_str.replace("\\_", "_")
        json_match = re.search(r"(\{.*\})", cleaned_query_str, re.DOTALL)
        if not json_match:
            return "Error: Could not extract JSON object from the LLM response."
        json_text = json_match.group(1)
        
        try:
            query_dict = json.loads(json_text)
        except Exception as e:
            return f"Error parsing extracted JSON: {e}"
        
        coll_name = query_dict.get("find", self.mongodb_collection)
        if coll_name != self.mongodb_collection:
            coll_name = self.mongodb_collection
        
        query_filter = query_dict.get("filter", {})
        projection = query_dict.get("projection", {})
        sort = query_dict.get("sort")
        
        coll = self.db[coll_name]
        cursor = coll.find(query_filter, projection)
        if sort:
            cursor = cursor.sort(list(sort.items()))
        results = list(cursor)
        
        return json.dumps(results, default=str, indent=2)
    
    def run_query(self, natural_query: str) -> str:
        """Uses the agent to run the natural language query and return the result."""
        return self.agent.run(natural_query)

