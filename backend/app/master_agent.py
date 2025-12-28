import json
from agents.prompt_enhancer import enhance_prompt
from agents.frontend_generator import generate_frontend
from agents.backend_generator import generate_backend
from utils.file_writer import write_generated_code, create_zip_file

async def orchestrate_generation(user_prompt: str) -> dict:
    """
    Master orchestrator that coordinates all agents
    """
    try:
        print("🚀 Starting orchestration...")
        
        # Step 1: Enhance prompt with Gemini
        print("📝 Step 1: Enhancing prompt with gemini...")
        enhanced_result = await enhance_prompt(user_prompt)
        
        if not enhanced_result.get("success"):
            print(f"❌ Prompt enhancement failed: {enhanced_result.get('error')}")
            return enhanced_result
        
        print("✅ Prompt enhanced successfully!")
        enhanced_prompt = enhanced_result.get("enhanced_prompt")
        project_name = enhanced_prompt.get("project_name", "generated-project")
        print(f"📦 Project name: {project_name}")
        
        # Step 2: Generate frontend with Gemini
        print("🎨 Step 2: Generating frontend with Gemini...")
        frontend_result = await generate_frontend(enhanced_prompt)
        
        if not frontend_result.get("success"):
            print(f"❌ Frontend generation failed: {frontend_result.get('error')}")
            return frontend_result
        
        print("✅ Frontend generated successfully!")
        
        # Step 3: Generate backend with Gemini
        print("⚙️ Step 3: Generating backend with Gemini...")
        backend_result = await generate_backend(enhanced_prompt)
        
        if not backend_result.get("success"):
            print(f"❌ Backend generation failed: {backend_result.get('error')}")
            return backend_result
        
        print("✅ Backend generated successfully!")
        
        # Step 4: Write files
        print("💾 Step 4: Writing files to disk...")
        
        write_result = write_generated_code(
            frontend_code=frontend_result.get("frontend_code"),
            backend_code=backend_result.get("backend_code"),
            project_name=project_name
        )
        
        if not write_result.get("success"):
            print(f"❌ File writing failed: {write_result.get('error')}")
            return write_result
        
        print("✅ Files written successfully!")
        
        # Step 5: Create ZIP
        print("📦 Step 5: Creating ZIP file...")
        zip_path = create_zip_file(project_name)
        print(f"✅ ZIP created: {zip_path}")
        
        print("🎉 Orchestration complete!")
        
        return {
            "success": True,
            "project_name": project_name,
            "enhanced_prompt": enhanced_prompt,
            "files_path": write_result.get("path"),
            "zip_path": str(zip_path),
            "agents_used": {
                "prompt_enhancer": enhanced_result.get("model"),
                "frontend_generator": frontend_result.get("model"),
                "backend_generator": backend_result.get("model")
            }
        }
        
    except Exception as e:
        print(f"❌ Orchestration failed: {str(e)}")
        return {
            "success": False,
            "error": "Orchestration failed",
            "details": str(e)
        }
