from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

def get_llm(streaming=False):
    return ChatGroq(
        temperature=0.7,
        model_name="llama-3.3-70b-versatile",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        streaming=streaming
    )

def clean_json(result: str) -> any:
    result = result.strip()
    if "```" in result:
        result = re.sub(r"```json\s*", "", result)
        result = re.sub(r"```\s*", "", result)
        result = result.strip()
    start = result.find("[") if result.find("[") != -1 and (
        result.find("{") == -1 or result.find("[") < result.find("{")
    ) else result.find("{")
    if start == -1:
        return []
    open_char = result[start]
    close_char = "]" if open_char == "[" else "}"
    depth = 0
    end = start
    for i in range(start, len(result)):
        if result[i] == open_char:
            depth += 1
        elif result[i] == close_char:
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    return json.loads(result[start:end].strip())

def build_prompt(topic: str, audience: str, platform: str, tone: str, length_minutes: int, language: str) -> str:
    # Calculate approximate scenes based on length
    scenes_count = length_minutes * 2  # roughly 2 scenes per minute

    platform_notes = {
        "YouTube": "Include a strong hook in first 30 seconds. End with subscribe CTA.",
        "LinkedIn": "Professional tone. Start with a bold insight. End with a question to drive comments.",
        "TikTok": "Very fast paced. Hook in first 3 seconds. Keep each scene under 15 seconds.",
        "Instagram Reels": "Visually driven. Text overlays important. 30-60 seconds max.",
    }

    tone_notes = {
        "Educational": "Clear, structured, informative. Use examples and analogies.",
        "Entertaining": "Engaging, fun, conversational. Use humor and storytelling.",
        "Promotional": "Persuasive, benefit-focused. Build desire and urgency.",
        "Inspirational": "Motivating, emotional. Use stories and powerful statements.",
    }

    return f"""You are a world-class video scriptwriter with 10 years of experience writing viral {platform} content.

Write a complete {length_minutes}-minute {platform} video script about: "{topic}"
Target audience: {audience}
Tone: {tone} — {tone_notes.get(tone, "")}
Platform notes: {platform_notes.get(platform, "")}
Language: {language}

Generate exactly {scenes_count} scenes.

Return ONLY a JSON array with no extra text, in this exact format:
[
  {{
    "scene_number": 1,
    "timestamp_start": "00:00",
    "timestamp_end": "00:30",
    "scene_type": "HOOK",
    "dialogue": "The exact words the presenter should say",
    "broll": "Description of what visuals to show on screen",
    "onscreen_text": "Text overlay to display on screen",
    "speaker_note": "Direction for the presenter on how to deliver this"
  }}
]

Scene types to use: HOOK, PROBLEM, AGITATION, SOLUTION, EXPLANATION, EXAMPLE, STATISTICS, STORY, TIPS, DEMO, OBJECTION, CTA
Make the dialogue natural and conversational, not robotic.
Make b-roll suggestions specific and visual.
Timestamps must be sequential and accurate for a {length_minutes} minute video.
"""

def generate_script(topic: str, audience: str, platform: str, tone: str, length_minutes: int, language: str) -> list:
    try:
        llm = get_llm()
        prompt = build_prompt(topic, audience, platform, tone, length_minutes, language)
        result = llm.invoke(prompt)
        content = result.content if hasattr(result, 'content') else str(result)
        print(f"🎬 Raw script generated, parsing...")
        scenes = clean_json(content)
        print(f"✅ Generated {len(scenes)} scenes")
        return scenes
    except Exception as e:
        print(f"❌ Script generation error: {str(e)}")
        return []

async def generate_script_stream(topic: str, audience: str, platform: str, tone: str, length_minutes: int, language: str):
    """Async generator that streams script content chunk by chunk"""
    try:
        llm = get_llm(streaming=True)
        prompt = build_prompt(topic, audience, platform, tone, length_minutes, language)
        full_content = ""

        async for chunk in llm.astream(prompt):
            content = chunk.content if hasattr(chunk, 'content') else str(chunk)
            if content:
                full_content += content
                yield content

        # After streaming completes, parse and save
        print(f"✅ Streaming complete, total length: {len(full_content)}")

    except Exception as e:
        print(f"❌ Streaming error: {str(e)}")
        yield f"[ERROR: {str(e)}]"