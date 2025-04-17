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
from agent.tools.ticketing import issue_ticket
from utils import AgentState, llm, fast_llm, agent_prompt_template, generate_prompt_template, translate_text, detect
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.callbacks import get_openai_callback

memory=MemorySaver()

def build_graph(web_name):

    """
    Build a graph to generate a response to a user question.

    The graph starts by calling an agent model to decide whether to retrieve documents
    using the retriever tool, or simply generate a response.

    If the agent decides to retrieve, it will retrieve documents using the retriever tool.

    After retrieving documents, the graph will call the agent model again to assess whether
    the documents are relevant to the user question.

    If the documents are deemed relevant, the graph will generate a response using the
    documents and the user question.

    If the documents are deemed not relevant, the graph will re-write the user question
    using a language model.

    The graph will continue to loop between the agent model, retrieving documents, and
    re-writing the question until the agent decides that the documents are relevant.

    Args:
        vector_store_path (str): Path to vector store
        web_name (str): Name of website

    Returns:
        StateGraph: A graph representing the state machine
    """
    retriever_tool=get_retriever_tool(web_name=web_name)
    
    tools=[retriever_tool, contact]

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
    Asynchronously generates a chat response based on the provided question using a state graph.

    Args:
        graph (StateGraph): The graph to process the chat message and generate a response.
        question (str): The user's question to be answered.
        thread_id (str, optional): The identifier for the chat thread. Defaults to "1".

    Returns:
        str: The final response generated by the graph, or an error message if something goes wrong.
    """

    try:
        response= ""        
        config = {"configurable": {"thread_id": thread_id}}
        
        language= await detect(question)
        
        if language != "en":
            question, language = await translate_text(text=question)
        
        with get_openai_callback() as cb:    
            async for chunk in graph.astream(
                {
                    "messages": [("user", question)],
                },
                config=config,
                stream_mode="values",        
            ):
                if chunk["messages"]:
                    response = chunk["messages"][-1].content
                    if language != "en":
                        response = await translate_text(text=response, src=language)
        
        print(f"Total Tokens: {cb.total_tokens}")
        print(f"Prompt Tokens: {cb.prompt_tokens}")
        print(f"Completion Tokens: {cb.completion_tokens}")
        print(f"Total Cost (USD): ${cb.total_cost}")
        
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