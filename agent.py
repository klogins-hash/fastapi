"""
LangGraph Cloud Agent
Optimized for LangSmith platform deployment
"""

import os
from typing import List, Annotated
from typing_extensions import TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.tools import tool

from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver


# Define the state for our agent
class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]


# Initialize the LLM
def get_llm():
    """Get the configured LLM"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    
    return ChatAnthropic(
        model="claude-3-haiku-20240307",
        api_key=api_key,
        temperature=0.7,
        max_tokens=1000
    )


# Define some example tools (you can expand this)
@tool
def get_current_time() -> str:
    """Get the current time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def echo_message(message: str) -> str:
    """Echo back a message with a prefix."""
    return f"Echo: {message}"


# Available tools
tools = [get_current_time, echo_message]
tool_node = ToolNode(tools)


# Define the agent node
def agent_node(state: State):
    """Main agent reasoning node"""
    llm = get_llm()
    
    # Bind tools to the LLM
    llm_with_tools = llm.bind_tools(tools)
    
    # Get the response from the LLM
    response = llm_with_tools.invoke(state["messages"])
    
    return {"messages": [response]}


# Define the conditional logic for routing
def should_continue(state: State):
    """Determine if we should continue to tools or end"""
    last_message = state["messages"][-1]
    
    # If there are tool calls, continue to tools
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    
    # Otherwise, end the conversation
    return END


# Build the graph
def create_graph():
    """Create the LangGraph workflow"""
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    
    # Set the entry point
    workflow.set_entry_point("agent")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )
    
    # Add edge from tools back to agent
    workflow.add_edge("tools", "agent")
    
    # Add memory for conversation persistence
    memory = MemorySaver()
    
    # Compile the graph
    return workflow.compile(checkpointer=memory)


# Create the graph instance
graph = create_graph()


# Entry point for testing
if __name__ == "__main__":
    # Test the agent locally
    config = {"configurable": {"thread_id": "test-thread"}}
    
    result = graph.invoke(
        {"messages": [HumanMessage(content="Hello! What time is it?")]},
        config=config
    )
    
    print("Agent Response:")
    print(result["messages"][-1].content)
