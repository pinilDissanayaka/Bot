from typing import Literal
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from langgraph.prebuilt import tools_condition
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode
from agent.tools.retriever_tool import get_retriever_tool
from agent.tools.email import contact
from utils import AgentState, llm, fast_llm, translate_text, detect
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.callbacks import get_openai_callback
from functools import lru_cache



memory=MemorySaver()


def build_graph(agent_system_prompt:str, generate_system_prompt:str, web_name:str):
    """
    Builds a state machine for generating a response to a user question by retrieving
    relevant documents, grading their relevance, re-writing the question if the retrieved
    documents are not relevant, and generating a response based on the final question.

    The state machine is a graph of nodes, each representing a step in the process. The
    nodes are:

    - `agent`: The node that invokes the agent model to generate a response based on the
      current state. Given the question, it will decide to retrieve using the retriever
      tool, or simply end.
    - `retrieve`: The node that retrieves relevant documents using the retriever tool.
    - `rewrite`: The node that transforms the query to produce a better question if the
      retrieved documents are not relevant.
    - `generate`: The node that generates a response based on the final question.

    The edges between the nodes are determined by the output of the `grade_documents`
    function, which determines whether the retrieved documents are relevant to the
    question. If they are, the state machine proceeds to the `generate` node. If they are
    not, the state machine proceeds to the `rewrite` node.

    The state machine is compiled using the `StateGraph` class and the `compile` method,
    which returns a `Graph` object. The `Graph` object can be used to run the state machine
    by calling its `invoke` method.

    Returns:
        Graph: A state machine graph that can be used to generate a response to a user
          question.
    """
    retriever_tool = get_retriever_tool(web_name=web_name)
    
    tools = [retriever_tool, contact]
    
    agent_prompt_template = [
        ("system",
            agent_system_prompt
        ),
        ("human", "Visitor: {QUESTION}")
    ]
    
    generate_prompt_template = [
        ("system", 
            generate_system_prompt
        ),
        ("human", "Visitor: {question}\nContext: {context}")
    ]

    async def grade_documents(state) -> Literal["generate", "rewrite"]:
        """
        Determines whether the retrieved documents are relevant to the question.

        Args:
            state (messages): The current state

        Returns:
            str: A decision for whether the documents are relevant or not
        """
        print("---CHECK RELEVANCE---")

        # Data model
        class grade(BaseModel):
            """Binary score for relevance check."""

            binary_score: str = Field(description="Relevance score 'yes' or 'no'")

        # LLM with tool and validation
        llm_with_tool = fast_llm.with_structured_output(grade)

        # Prompt
        prompt = PromptTemplate(
            template="""You are a grader assessing relevance of a retrieved document to a user question. \n 
            Here is the retrieved document: \n\n {context} \n\n
            Here is the user question: {question} \n
            If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
            Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.""",
            input_variables=["context", "question"],
        )

        # Chain
        chain = prompt | llm_with_tool

        messages = state["messages"]
        last_message = messages[-1]

        question = messages[0].content
        docs = last_message.content

        scored_result = await chain.ainvoke({"question": question, "context": docs})

        score = scored_result.binary_score

        if score == "yes":
            print("---DECISION: DOCS RELEVANT---")
            return "generate"

        else:
            print("---DECISION: DOCS NOT RELEVANT---")
            print(score)
            return "rewrite"

    ### Nodes
    async def agent(state):
        """
        Invokes the agent model to generate a response based on the current state. Given
        the question, it will decide to retrieve using the retriever tool, or simply end.

        Args:
            state (messages): The current state

        Returns:
            dict: The updated state with the agent response appended to messages
        """
        print("---CALL AGENT---")
        
        agent_prompt = ChatPromptTemplate.from_messages(agent_prompt_template)
        
        messages = state["messages"]
        
        model = llm.bind_tools(tools)
        
        agent_chain = (
            {"QUESTION": RunnablePassthrough()} |
            agent_prompt |
            model
        )
        
        response = await agent_chain.ainvoke({"question": messages})
        # We return a list, because this will get added to the existing list
        return {"messages": [response]}

    async def rewrite(state):
        """
        Transform the query to produce a better question.

        Args:
            state (messages): The current state

        Returns:
            dict: The updated state with re-phrased question
        """
        print("---TRANSFORM QUERY---")
        messages = state["messages"]
        question = messages[0].content

        msg = [
            HumanMessage(
                content=f""" \n 
                    Look at the input and try to reason about the underlying semantic intent / meaning. \n 
                    Here is the initial question:
                    \n ------- \n
                    {question} 
                    \n ------- \n
                    Formulate an improved question: """,
                )
        ]

        # Grader
        response = await fast_llm.ainvoke(msg)
        return {"messages": [response]}

    async def generate(state):
        """
        Generate answer

        Args:
            state (messages): The current state

        Returns:
            dict: The updated state with re-phrased question
        """
        print("---GENERATE---")
        messages = state["messages"]
        question = messages[0].content
        last_message = messages[-1]

        docs = last_message.content

        # Prompt
        prompt = ChatPromptTemplate.from_messages(generate_prompt_template)

        # Chain
        generate_chain = prompt | llm | StrOutputParser()
        
        # Run
        response = await generate_chain.ainvoke({"context": docs, "question": question})
        return {"messages": [response]}

    # Define a new graph
    workflow = StateGraph(AgentState)

    # Define the nodes we will cycle between
    workflow.add_node("agent", agent)  # agent
    retrieve = ToolNode([retriever_tool, contact]) # tool node
    workflow.add_node("retrieve", retrieve)  # retrieval
    workflow.add_node("rewrite", rewrite)  # Re-writing the question
    workflow.add_node(
        "generate", generate
    )  # Generating a response after we know the documents are relevant
    # Call agent node to decide to retrieve or not
    workflow.add_edge(START, "agent")

    # Decide whether to retrieve
    workflow.add_conditional_edges(
        "agent",
        # Assess agent decision
        tools_condition,
        {
            # Translate the condition outputs to nodes in our graph
            "tools": "retrieve",
            END: END,
        },
    )

    # Edges taken after the `action` node is called.
    workflow.add_conditional_edges(
        "retrieve",
        # Assess agent decision
        grade_documents,
    )
    workflow.add_edge("generate", END)
    workflow.add_edge("rewrite", "agent")

    # Compile
    graph = workflow.compile(checkpointer=memory)
    
    return graph

async def get_chat_response(graph, question: str, thread_id: str = "1"):
    """
    Process a chat message through the chatbot agent.

    Args:
        graph: The agent state machine graph.
        question: The user's question to be processed.
        thread_id: The ID of the conversation thread.

    Returns:
        str: The response from the chatbot agent.
    """
    
    try:
        response= ""        
        config = {"configurable": {"thread_id": thread_id}}
        
        language= await detect(question)
        
        if language != "en":
            question, language = await translate_text(text=question)
        

        async for chunk in graph.astream(
            {
                "messages": [HumanMessage(content=question)],
            },
            config=config,
            stream_mode="values",        
        ):
            if chunk["messages"]:
                response = chunk["messages"][-1].content
                if language != "en":
                    response = await translate_text(text=response, src=language)
        
        if response:
            final_response= response
        else:
            if language != "en":
                final_response = await translate_text(text="Please Try again later", src=language)
            else:
                final_response = "Please Try again later"        
        return final_response
    
    except Exception as e:
        print(e)
        try:
            # Build fallback prompt and agent chain
            fallback_prompt = ChatPromptTemplate.from_messages([
                ("system", "A user faced a system error and wants help. Trigger the contact tool."),
                ("human", "There was an error in processing my request. Can you contact support for me?")
            ])
            
            model_with_tool = llm.bind_tools([contact])
            agent_chain = fallback_prompt | model_with_tool

            # Call the fallback chain
            response = await agent_chain.ainvoke({})

            # Translate if needed
            contact_response = response.content if language == "en" else await translate_text(text=response.content, src=language)

            # Save to memory (simulates continuation of the conversation)
            await memory.aput(
                thread_id,
                {
                    "messages": [
                        ("user", "There was an error in processing my request. Can you contact support for me?"),
                        ("assistant", contact_response)
                    ]
                }
            )

            return contact_response
        except Exception as inner_e:
            print("Tool fallback also failed:", inner_e)
            final_fallback = "Please try again later." if language == "en" else await translate_text(text="Please try again later", src=language)
            return final_fallback