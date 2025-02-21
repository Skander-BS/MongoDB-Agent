import streamlit as st
import requests
import pymongo
import os
from dotenv import load_dotenv
import warnings
from utils import chat_title_generator, response_generator

warnings.filterwarnings("ignore")
load_dotenv()

API_URL = "http://127.0.0.1:8000/query"

MONGO_URI = os.getenv("MONGODB_URI_APP")  
MONGO_DATABASE = os.getenv("MONGODB_DATABASE_APP")
MONGO_COLLECTION = os.getenv("MONGODB_COLLECTION_APP")   

client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DATABASE]          
chats_collection = db[MONGO_COLLECTION]  

st.set_page_config(
    page_title="MongoDB Agent"
)

st.markdown(
    """
    <div style="display: flex; justify-content: center; margin-right:140px">
        <img src="https://www.vectorlogo.zone/logos/mongodb/mongodb-ar21~bgwhite.svg" 
             alt="MongoDB Logo" 
             style="height: 40px;" />
    </div>
    """,
    unsafe_allow_html=True
)

st.title("MongoDB Agent Query Interface")

if 'chats' not in st.session_state:
    st.session_state['chats'] = list(chats_collection.find())
if 'chat_select' not in st.session_state:
    st.session_state['chat_select'] = 0  

st.sidebar.title("Chats")
col1, col_spacer, col2 = st.sidebar.columns([1, 0.3, 1])
if col1.button("New Chat"):
    new_chat = {'title': 'New Chat', 'messages': []}
    result = chats_collection.insert_one(new_chat)
    new_chat['_id'] = result.inserted_id
    st.session_state['chats'].append(new_chat)
    st.session_state['chat_select'] = len(st.session_state['chats']) - 1
    st.rerun()

if col2.button("Clear History"):
    chats_collection.delete_many({})  
    st.session_state['chats'] = []  
    st.rerun()

if st.session_state['chats']:
    chat_titles = [chat['title'] for chat in st.session_state['chats']]
    selected_index = st.sidebar.selectbox(
        "Select a chat:",
        options=range(len(chat_titles)),
        format_func=lambda i: chat_titles[i],
        index=st.session_state.get('chat_select', 0),
        key="selected_chat"
    )
    st.session_state['chat_select'] = selected_index
else:
    st.sidebar.write("No chats yet.")

if st.session_state['chats']:
    current_chat = st.session_state['chats'][st.session_state['chat_select']]

    st.write(f"##### *{current_chat['title']}*")
    for message in current_chat['messages']:
        with st.chat_message(message['role']):
            st.markdown(message['content'])
    
    user_input = st.chat_input("Type your message here...")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        current_chat['messages'].append({'role': 'user', 'content': user_input})
        
        if len(current_chat['messages']) == 1:
            current_chat['title'] = chat_title_generator(user_input)
        
        with st.spinner("Waiting for response..."):
            try:
                response = requests.post(API_URL, json={"natural_query": user_input})
                response.raise_for_status()
                data = response.json()
                
                assistant_message = ""
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    for chunk in response_generator(data):
                        assistant_message += chunk
                        message_placeholder.markdown(assistant_message)
                
                current_chat['messages'].append({'role': 'assistant', 'content': assistant_message})
                chats_collection.update_one(
                    {"_id": current_chat['_id']},
                    {"$set": {"messages": current_chat['messages'], "title": current_chat['title']}}
                )
                st.rerun() 
            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.markdown(
    '<p style="text-align: center; font-style: italic; margin-right:140px">Select a chat or start a new one.</p>',
    unsafe_allow_html=True
)