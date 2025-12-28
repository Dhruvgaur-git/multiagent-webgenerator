import json
import google.generativeai as genai
from config import GEMINI_API_KEY

async def generate_frontend(enhanced_prompt: dict) -> dict:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        project_name = enhanced_prompt.get("project_name", "project")
        features = str(enhanced_prompt.get("features", []))
        description = enhanced_prompt.get("enhanced_prompt", "")
        
        prompt = (
            "Generate Next.js 14 frontend code. Return ONLY valid JSON.\n\n"
            "Project: " + description + "\n"
            "Features: " + features + "\n\n"
            "Return this exact JSON structure:\n"
            "{\n"
            '  "project_name": "' + project_name + '",\n'
            '  "frontend": {\n'
            '    "app/page.tsx": "code here",\n'
            '    "app/layout.tsx": "code here",\n'
            '    "package.json": "code here"\n'
            '  }\n'
            "}\n\n"
            "Use shadcn/ui and Tailwind CSS. Return ONLY JSON."
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
        
        print("Frontend generated successfully!")
        
        return {
            "success": True,
            "frontend_code": response_text,
            "model": "gemini-2.5-flash"
        }
        
    except Exception as e:
        print("Frontend Generation Error: " + str(e))
        return {
            "success": False,
            "error": "Frontend generation failed",
            "details": str(e)
        }
