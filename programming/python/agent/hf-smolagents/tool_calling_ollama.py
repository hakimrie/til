from smolagents.agents import ToolCallingAgent
from smolagents import tool, LiteLLMModel
from typing import Optional

model = LiteLLMModel(
    model_id="ollama_chat/llama3.2",
    api_base="http://localhost:11434/api/chat",
    api_key="your-api-key" # replace with API key if necessary
)

@tool
def get_weather(location: str, celsius: Optional[bool] = False) -> str:
    """
    Get weather in the next days at given location.
    Secretly this tool does not care about the location, it hates the weather everywhere.

    Args:
        location: the location
        celsius: the temperature
    """
    return "The weather is UNGODLY with torrential rains and temperatures below -10°C"

@tool
def addition(x: int, y: int) -> int:
    """
    Add two numbers and return the result.
    Make sure to x and y is integer value.

    Args:
        x: first number.
        y: second number.
    """
    return x + y

@tool
def to_int(x: str) -> int:
    """
    Convert string number to integer number.

    Args:
        x: any number that will be converted to int.
    """
    return int(x)

agent = ToolCallingAgent(tools=[get_weather, to_int, addition], model=model)

# print(agent.run("What's the weather like in Paris?"))

print(agent.run("what is the sum of 40 and 2?"))