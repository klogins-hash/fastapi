"""
Test script for LangGraph Cloud deployment
"""

import os
from langchain_core.messages import HumanMessage
from langgraph_sdk import get_client


def test_local_agent():
    """Test the agent locally"""
    print("Testing local agent...")
    
    from agent import graph
    
    config = {"configurable": {"thread_id": "test-thread"}}
    
    # Test basic conversation
    result = graph.invoke(
        {"messages": [HumanMessage(content="Hello! Can you tell me what time it is?")]},
        config=config
    )
    
    print("Local Agent Response:")
    print(result["messages"][-1].content)
    print()


def test_deployed_agent():
    """Test the deployed agent on LangGraph Cloud"""
    print("Testing deployed agent...")
    
    # Get the deployment URL from environment or use default
    deployment_url = os.getenv("LANGGRAPH_DEPLOYMENT_URL")
    if not deployment_url:
        print("LANGGRAPH_DEPLOYMENT_URL not set. Skipping deployed agent test.")
        return
    
    # Initialize the client
    client = get_client(url=deployment_url)
    
    # Test the agent
    response = client.runs.create(
        assistant_id="agent",
        input={"messages": [HumanMessage(content="Hello! What can you help me with?")]},
        config={"configurable": {"thread_id": "test-deployment"}}
    )
    
    print("Deployed Agent Response:")
    print(response)
    print()


if __name__ == "__main__":
    # Test local agent
    test_local_agent()
    
    # Test deployed agent if URL is available
    test_deployed_agent()
    
    print("✅ Testing complete!")
