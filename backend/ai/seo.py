from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

def get_llm():
    return ChatGroq(
        temperature=0.7,
        model_name="llama-3.3-70b-versatile",
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

def clean_json(result: str) -> dict:
    result = result.strip()
    if "```" in result:
        result = re.sub(r"```json\s*", "", result)
        result = re.sub(r"```\s*", "", result)
        result = result.strip()
    start = result.find("{")
    if start == -1:
        return {}
    depth = 0
    end = start
    for i in range(start, len(result)):
        if result[i] == "{":
            depth += 1
        elif result[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    return json.loads(result[start:end].strip())

def generate_seo(topic: str, platform: str, scenes: list) -> dict:
    try:
        llm = get_llm()

        # Build a summary of scenes for context
        scene_summary = ""
        for s in scenes[:5]:
            scene_summary += f"- {s.get('scene_type', '')}: {s.get('dialogue', '')[:100]}\n"

        prompt = f"""You are an expert YouTube SEO specialist and content strategist.

Based on this video about "{topic}" for {platform} with these opening scenes:
{scene_summary}

Generate SEO metadata. Return ONLY a JSON object with no extra text:
{{
  "titles": [
    "Title option 1 — compelling and SEO optimized",
    "Title option 2 — different angle",
    "Title option 3 — question format"
  ],
  "description": "Full YouTube description 150-200 words with keywords naturally included. Include what viewers will learn. End with a call to action.",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10", "tag11", "tag12", "tag13", "tag14", "tag15"],
  "thumbnail_text": "Short punchy text for thumbnail overlay — max 6 words",
  "hook_score": 85,
  "hook_feedback": "Your hook is strong because... Here's how to improve it..."
}}

Make titles clickable and curiosity-driven.
Tags should be a mix of broad and specific keywords.
Hook score is out of 100.
"""

        result = llm.invoke(prompt)
        content = result.content if hasattr(result, 'content') else str(result)
        seo = clean_json(content)
        print(f"✅ SEO metadata generated")
        return seo

    except Exception as e:
        print(f"❌ SEO generation error: {str(e)}")
        return {
            "titles": [f"The Ultimate Guide to {topic}"],
            "description": f"In this video we cover everything about {topic}.",
            "tags": [topic],
            "thumbnail_text": topic[:30],
            "hook_score": 0,
            "hook_feedback": "Could not analyze hook"
        }