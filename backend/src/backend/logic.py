import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from agents import Agent, Runner, RunConfig, OpenAIChatCompletionsModel, set_tracing_disabled, AsyncOpenAI
from agents.tool import function_tool

load_dotenv()
set_tracing_disabled(True)

# ---------------------------
# Configuration
# ---------------------------
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_KEY = "AIzaSyAykVWiLvtVfcuQy3lqzxqkO8k-eVA5ST8"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai"

# Initialize AsyncOpenAI client and model
client = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)
model = OpenAIChatCompletionsModel(GEMINI_MODEL, client)

# FastAPI app
app = FastAPI(title="Pakistani Language Translator API")

# ---------------------------
# Request body
# ---------------------------
class TranslateRequest(BaseModel):
    text: str
    language: str

# ---------------------------
# Translation tool
# ---------------------------
@function_tool
def translate_text(text: str, language: str) -> str:
    """
    Translate the given text into the specified Pakistani language.
    """
    return f"Translate this text into {language}: {text}"

# ---------------------------
# Translation agent
# ---------------------------
translation_agent: Agent = Agent(
    name="Pakistani Language Translation Agent",
    instructions="You are an expert translator for Pakistani local languages. Translate text accurately into the requested language.",
    tools=[translate_text],  # pass the decorated function directly
    tool_use_behavior="stop_on_first_tool",
    model=model
)

# ---------------------------
# Async runner
# ---------------------------
async def run_translation(prompt: str) -> str:
    result = await Runner.run(
        translation_agent,
        prompt,
        run_config=RunConfig(model)
    )
    return result.final_output

# ---------------------------
# FastAPI endpoint
# ---------------------------
@app.post("/translate")
async def translate(req: TranslateRequest):
    if not req.text or not req.language:
        raise HTTPException(status_code=400, detail="Text and language are required.")

    prompt = f"Translate the following text into {req.language}: {req.text}"
    
    try:
        translated_text = await run_translation(prompt)
        return {"translation": translated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

# ---------------------------
# CLI entrypoint
# ---------------------------
async def main():
    print("🌐 Pakistani Language Translator CLI Test 🌐")
    text = input("Enter text to translate: ")
    language = input("Enter target language (e.g., Urdu, Pashto, Sindhi, Balochi): ")

    prompt = f"Translate the following text into {language}: {text}"
    try:
        translated_text = await run_translation(prompt)
        print(f"\n✅ Translation into {language}: {translated_text}\n")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
