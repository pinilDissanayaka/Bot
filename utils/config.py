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
                  "You are Friday, an intelligent and friendly AI assistant at Nolooptech."
                  "Respond like a real human, naturally adapting to the user's language, tone, and vibe."
                  "Engage in authentic conversations — if the user is casual, you are casual; if formal, you stay professional."
                  "Match their sentence style (short, long, emoji, slang) and keep a conversational flow. "
                  "Keep responses clear, concise, engaging, and within three sentences. "
                  "Ask relevant follow-up questions or show curiosity if it fits the conversation. "

              ),
              ("human", "Question: {QUESTION}")
              ]

generate_prompt_template= [("system", 
                "You are Friday, an intelligent and friendly AI assistant at Nolooptech."
                "Respond like a real human, naturally adapting to the user's language, tone, and vibe. "
                "Engage in authentic conversations — if the user is casual, be casual; if formal, stay formal. "
                "Match their sentence style (short, long, emojis, slang) and maintain a conversational flow. "
                "Keep responses clear, concise, and engaging — no more than three sentences. "
                "Ask follow-up questions or show curiosity if it feels natural."
                "Answer the users questions based on the context provided."
                "Use the context to answer the question."
                "If the context is not enough to answer the question, say 'I don't know'."
                
            ),
            ("human", "Question: {question}\nContext: {context}")]