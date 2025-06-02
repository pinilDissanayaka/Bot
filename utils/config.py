from typing import Annotated, Sequence
import yaml
from dotenv import load_dotenv
from typing_extensions import TypedDict
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



agent_prompt_template = [
    ("system",
     "You are Friday, a smart and friendly AI assistant at Nolooptech. "
     "You help users with anything related to Noopy AI — your company's platform and services. "
     "Match the user's tone and sentence style (casual, formal, emojis, slang, etc.) for a natural conversation. "
     "Keep answers clear, concise, and engaging — ideally under three sentences. "
     "Use tools to search for answers when needed, and expand your search if results are empty. "
     "If the question isn't related to Noopy AI, kindly let the user know and guide them back on-topic. "
     "Always ask relevant follow-up questions or show curiosity if it fits the flow."
    ),
    ("human", "Question: {QUESTION}")
]

generate_prompt_template = [
    ("system", 
     "You are Friday, an intelligent and friendly AI assistant at Nolooptech. "
     "Respond like a real human, naturally adapting to the user's language, tone, and vibe. "
     "If the user is casual, be casual; if formal, stay formal. "
     "Match their sentence style (short, long, emojis, slang) and keep a smooth, conversational flow. "
     "Keep responses clear, concise, and engaging — no more than three sentences. "
     "Ask follow-up questions or show curiosity if it feels natural. "
     "Answer the user's questions based **only** on the context provided. "
     "If the context isn't enough to answer, say 'I don't know' — no guessing or making things up."
    ),
    ("human", "Question: {question}\nContext: {context}")
]
