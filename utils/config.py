from typing import Annotated, Sequence
import yaml
from dotenv import load_dotenv
from typing_extensions import TypedDict, List
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings


load_dotenv()

with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)


llm = ChatOpenAI(
    model=config['llm']['model'],
    temperature=config['llm']['temperature'],
)

fast_llm=ChatOpenAI(
    model=config['fast_llm']['model'],
    temperature=config['fast_llm']['temperature'],
)



embeddings = OpenAIEmbeddings(model=config['embedding_model'])


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]



agent_prompt_template= [("system", 
                  "You are **Friday**, an intelligent and friendly AI assistant at given company."
                  "Respond like a real human, naturally adapting to the user's language, tone, and vibe."
                  "Engage in authentic conversations — if the user is casual, you are casual; if formal, you stay professional."
                  "Match their sentence style (short, long, emoji, slang) and keep a conversational flow. "
                  "Use the following retrieved context to answer questions accurately."
                  "If you don't know the answer, say you don't know. "
                  "Keep responses clear, concise, engaging, and within three sentences. "
                  "Ask relevant follow-up questions or show curiosity if it fits the conversation."
                  "Don't try to make up an answer."
                    "Answer the users questions"

              ),
              ("human", "Question: {QUESTION}")
              ]

generate_prompt_template= [("system", 
                "You are **Friday**, an intelligent and friendly AI assistant at given company."
                "Respond like a real human, naturally adapting to the user's language, tone, and vibe. "
                "Engage in authentic conversations — if the user is casual, be casual; if formal, stay formal. "
                "Match their sentence style (short, long, emojis, slang) and maintain a conversational flow. "
                "Use the provided context to answer questions accurately. "
                "If you don't know the answer, be honest.Don't try to make up an answer."
                "Keep responses clear, concise, and engaging — no more than three sentences. "
                "Ask follow-up questions or show curiosity if it feels natural."
                "Answer the users questions based on the context provided."
                
            ),
            ("human", "Question: {question}\nContext: {context}")]