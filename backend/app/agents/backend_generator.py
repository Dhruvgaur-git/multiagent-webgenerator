import json
import google.generativeai as genai
from config import GEMINI_API_KEY

async def generate_backend(enhanced_prompt: dict) -> dict:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        project_name = enhanced_prompt.get("project_name", "project")
        features = str(enhanced_prompt.get("features", []))
        description = enhanced_prompt.get("enhanced_prompt", "")
        
        prompt = (
            "Generate Express.js backend code. Return ONLY valid JSON.\n\n"
            "Project: " + description + "\n"
            "Features: " + features + "\n\n"
            "Return this exact JSON structure:\n"
            "{\n"
            '  "project_name": "' + project_name + '",\n'
            '  "backend": {\n'
            '    "server.js": "code here",\n'
            '    "package.json": "code here"\n'
            '  }\n'
            "}\n\n"
            "Use Express.js and PostgreSQL (Neon DB). Return ONLY JSON."
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
        
        print("Backend generated successfully!")
        
        return {
            "success": True,
            "backend_code": response_text,
            "model": "gemini-2.5-flash"
        }
        
    except Exception as e:
        print("Backend Generation Error: " + str(e))
        return {
            "success": False,
            "error": "Backend generation failed",
            "details": str(e)
        }
