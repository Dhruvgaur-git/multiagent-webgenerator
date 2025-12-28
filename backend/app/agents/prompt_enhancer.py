import json
import google.generativeai as genai
from config import GEMINI_API_KEY

async def enhance_prompt(user_prompt: str) -> dict:
    try:
        print("Gemini API Key loaded for prompt enhancer")
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = (
            "You are a prompt enhancement expert. Return ONLY valid JSON, no other text.\n\n"
            "User Request: " + user_prompt + "\n\n"
            "Return this exact JSON structure:\n"
            "{\n"
            '  "project_name": "kebab-case-name",\n'
            '  "enhanced_prompt": "detailed description",\n'
            '  "features": ["feature1", "feature2"],\n'
            '  "tech_stack": {\n'
            '    "frontend": ["Next.js 14", "Tailwind CSS", "shadcn/ui"],\n'
            '    "backend": ["Node.js", "Express", "PostgreSQL"],\n'
            '    "database": "Neon PostgreSQL"\n'
            '  },\n'
            '  "pages": ["page1", "page2"],\n'
            '  "components": ["component1", "component2"]\n'
            "}"
        )
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        backticks = "```"
        json_backticks = "```json"
        
        if json_backticks in response_text:
            parts = response_text.split(json_backticks)
            if len(parts) > 1:
                response_text = parts[1].split(backticks)[0].strip()
        elif backticks in response_text:
            parts = response_text.split(backticks)
            if len(parts) > 1:
                response_text = parts[1].split(backticks)[0].strip()
        
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        if start != -1 and end > start:
            response_text = response_text[start:end]
        
        enhanced_data = json.loads(response_text)
        print("Prompt enhanced with Gemini!")
        
        return {
            "success": True,
            "enhanced_prompt": enhanced_data,
            "model": "gemini-2.5-flash"
        }
        
    except Exception as e:
        print("Prompt Enhancement Error: " + str(e))
        return {
            "success": False,
            "error": "Prompt enhancement failed",
            "details": str(e)
        }
