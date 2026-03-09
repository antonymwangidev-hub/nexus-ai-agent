from google.adk.agents import LlmAgent

from app.config import MODEL_NAME
from app.agent.prompt import SYSTEM_INSTRUCTION
from app.agent.tools import normalize_platform

root_agent = LlmAgent(
    name="socialfusion_agent",
    model=MODEL_NAME,
    description="Generates social media captions, hashtags, and image prompts.",
    instruction=SYSTEM_INSTRUCTION,
    tools=[normalize_platform],
)
