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


