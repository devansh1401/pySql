from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
import streamlit as st
import os
from streamlit_chat import message as st_message

def init_database() -> SQLDatabase:
    db_uri = f"mysql+mysqlconnector://{os.getenv('SQL_USER')}:{os.getenv('SQL_PASSWORD')}@{os.getenv('SQL_HOST')}:{os.getenv('SQL_PORT')}/{os.getenv('SQL_DATABASE')}"
    return SQLDatabase.from_uri(db_uri)

def get_sql_chain(db):
  template = """
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
    Based on the table schema below, write a SQL query that would answer the user's question. Take the conversation history into account.
    
    <SCHEMA>{schema}</SCHEMA>
    
    Conversation History: {chat_history}
    
    Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks.
    
    For example:
    Question: which 3 artists have the most tracks?
    SQL Query: SELECT ArtistId, COUNT(*) as track_count FROM Track GROUP BY ArtistId ORDER BY track_count DESC LIMIT 3;
    Question: Name 10 artists
    SQL Query: SELECT Name FROM Artist LIMIT 10;
    
    Your turn:
    
    Question: {question}
    SQL Query:
    """
    
  prompt = ChatPromptTemplate.from_template(template)
  
  # llm = ChatOpenAI(model="gpt-4-0125-preview")
  llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0)
  
  def get_schema(_):
    return db.get_table_info()
  
  return (
    RunnablePassthrough.assign(schema=get_schema)
    | prompt
    | llm
    | StrOutputParser()
  )
    
def get_response(user_query: str, db: SQLDatabase, chat_history: list):
  sql_chain = get_sql_chain(db)
  
  template = """
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
    Based on the table schema below, question, sql query, and sql response, write a natural language response.
    <SCHEMA>{schema}</SCHEMA>

    Conversation History: {chat_history}
    SQL Query: <SQL>{query}</SQL>
    User question: {question}
    SQL Response: {response}"""
  
  prompt = ChatPromptTemplate.from_template(template)
  
  # llm = ChatOpenAI(model="gpt-4-0125-preview")
  llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0)
  
  chain = (
    RunnablePassthrough.assign(query=sql_chain).assign(
      schema=lambda _: db.get_table_info(),
      response=lambda vars: db.run(vars["query"]),
    )
    | prompt
    | llm
    | StrOutputParser()
  )
  
  return chain.invoke({
    "question": user_query,
    "chat_history": chat_history,
  })
    
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
      AIMessage(content="Hello! I'm a SQL assistant. Ask me anything about your database."),
    ]

load_dotenv()

# Initialize database connection
if "db" not in st.session_state:
    st.session_state.db = init_database()

st.set_page_config(page_title="Chat with MySQL", page_icon=":speech_balloon:")

st.title("PySql")

# Sidebar with description
with st.sidebar:
    st.subheader("About this Bot")
    st.write("""
    This is an AI-powered SQL assistant that can help you query and analyze data from a MySQL database. 
    It uses natural language processing to understand your questions and generate appropriate SQL queries.

    Features:
    - Translate natural language questions into SQL queries
    - Provide insights and explanations about the data
    - Handle follow-up questions and maintain context

    Simply type your question about the database, and the bot will assist you in getting the information you need.
    """)
    
# Display chat messages
for i, message in enumerate(st.session_state.chat_history):
    if isinstance(message, AIMessage):
        st_message(message.content, key=f"ai_{i}")
    elif isinstance(message, HumanMessage):
        st_message(message.content, is_user=True, key=f"human_{i}")

# User input
user_query = st.chat_input("Type a message...")

if user_query is not None and user_query.strip() != "":
    # Add user message to chat history
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    
    # Display user message
    st_message(user_query, is_user=True, key=f"human_{len(st.session_state.chat_history)}")
    
    # Get AI response
    with st.spinner("Thinking..."):
        response = get_response(user_query, st.session_state.db, st.session_state.chat_history)
    
    # Display AI response
    st_message(response, key=f"ai_{len(st.session_state.chat_history) + 1}")
    
    # Add AI response to chat history
    st.session_state.chat_history.append(AIMessage(content=response))