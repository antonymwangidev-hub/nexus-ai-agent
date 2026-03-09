from pydantic import BaseModel, Field
from typing import List


class SocialContentOutput(BaseModel):
    platform: str = Field(description="Target social media platform")
    target_audience: str = Field(description="Primary audience for the post")
    tone: str = Field(description="Desired tone of the content")
    caption: str = Field(description="Final social media caption")
    hashtags: List[str] = Field(description="List of relevant hashtags")
    image_prompt: str = Field(description="Detailed visual prompt for image generation")
    notes: str = Field(description="Short explanation of the creative direction")
