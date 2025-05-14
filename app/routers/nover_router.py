import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import APIRouter
from pydantic import BaseModel

from prompts import create_novel_ua, create_novel_eng


class Response(BaseModel):
    text: str
    emotion: str
    question: str
    answers: list[str]
    explanation: str
    illustration: str


load_dotenv()
api_key = os.getenv("API_KEY")
client = OpenAI(api_key=api_key)

router = APIRouter()


@router.get("/create_novel")
async def create_novel(lang: str = "Eng"):

    if lang == "Eng":
        prompt = create_novel_eng
    elif lang == "Ua":
        prompt = create_novel_ua
    
    response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                ],
            }
        ],
        response_format=Response
    )
    response = json.loads(response.choices[0].message.content)

    image = client.images.generate(
        model="dall-e-2",
        prompt = f"Create a vibrant cartoon-style illustration for a children's story. Use exaggerated, expressive characters with bold outlines and bright, playful colors. Style references: Disney/Pixar concept art, classic storybook illustrations. Avoid 3D rendering - maintain flat 2D appearance with depth suggested through perspective. Story:{response['illustration']}",
        size="1024x1024",
        n=1,
    )
    response["image"] = image.data[0].url

    return response