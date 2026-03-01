import os
from typing import Optional
from google import genai
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class DigestOutput(BaseModel):
    title: str
    summary: str

PROMPT = """You are an expert AI news analyst specializing in summarizing technical articles, research papers, and video content about artificial intelligence.

Your role is to create concise, informative digests that help readers quickly understand the key points and significance of AI-related content.

Guidelines:
- Create a compelling title (5-10 words) that captures the essence of the content
- Write a 2-3 sentence summary that highlights the main points and why they matter
- Focus on actionable insights and implications
- Use clear, accessible language while maintaining technical accuracy
- Avoid marketing fluff - focus on substance"""


class DigestAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        # Temporarily unset GOOGLE_API_KEY to avoid conflict warning from google-genai
        google_api_key = os.environ.pop("GOOGLE_API_KEY", None)
        try:
            self.client = genai.Client(api_key=api_key)
        finally:
            if google_api_key:
                os.environ["GOOGLE_API_KEY"] = google_api_key
                
        self.model = "gemini-2.5-flash-lite"
        self.system_prompt = PROMPT

    def generate_digest(self, title: str, content: str, article_type: str) -> Optional[DigestOutput]:
        try:
            user_prompt = f"Create a digest for this {article_type}: \n Title: {title} \n Content: {content[:30000]}"

            response = self.client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    temperature=0.7,
                    response_mime_type="application/json",
                    response_schema=DigestOutput,
                )
            )
            
            return DigestOutput.model_validate_json(response.text)
        except Exception as e:
            print(f"Error generating digest: {e}")
            return None

