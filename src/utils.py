import asyncio
from openai import AsyncOpenAI
from pydantic_ai_litellm import LiteLLMModel
import tiktoken
import os
from litellm import completion

import config

enc = tiktoken.encoding_for_model("gpt-4")

def truncate_tokens(text: str) -> str:
    """
    Count the number of tokens in a text.
    """
    tokens = enc.encode(text)

    # count tokens
    length = len(tokens)

    if length > config.MAX_TOKENS_PER_TOOL_RESPONSE:
        # truncate the text
        text = enc.decode(tokens[:config.MAX_TOKENS_PER_TOOL_RESPONSE])
        text += "\n... [truncated because it exceeds the max tokens limit, try deeper paths]"

    return text

def get_llm(model: str = None) -> LiteLLMModel:
    """Initialize and return the specified LLM using LiteLLM"""

    model_name = model or config.MODEL
    
    base_url = None
    api_key = None
    extra_settings = {}
    if model_name.startswith("iflow/"):
        model_name = model_name.replace("iflow/", "dashscope/")
        base_url = "https://apis.iflow.cn/v1"
        api_key = os.getenv("IFLOW_API_KEY", config.API_KEY)
        model = LiteLLMModel(
            model_name=model_name,
            api_key=api_key,
            api_base=base_url,
            settings=extra_settings
        )
        return model
    elif model_name.startswith("github_copilot/"):
        api_key = os.getenv("GITHUB_TOKEN", config.API_KEY)
        extra_settings = {
            "extra_headers": {
                "editor-version": "vscode/1.90.0",
                "Copilot-Integration-Id": "vscode-chat"
            }
        }
        model = LiteLLMModel(
            model_name=model_name,
            api_key=api_key,
            settings=extra_settings
        )
        return model
    elif model_name.startswith("gemini/"):
        api_key = os.getenv("GEMINI_API_KEY", config.API_KEY)
        model = LiteLLMModel(
            model_name=model_name,
            api_key=api_key
        )
        return model

    model = LiteLLMModel(
        model_name=model_name,
        api_key=config.API_KEY,
        base_url=config.BASE_URL
    )
    return model
    
async def run_llm_natively(model: str = None, prompt: str = None, messages: list[dict] = None) -> str:
    model=model or config.MODEL
    if messages is None:
        messages = [{"role": "user", "content": prompt}]

    if model.startswith("github_copilot/"):
        response = completion(
            model=model,
            messages=messages,
            extra_headers={
                "editor-version": "vscode/1.90.0",
                "Copilot-Integration-Id": "vscode-chat"
            }
        )        
        return response.choices[0].message.content

    client = AsyncOpenAI(
        base_url=config.BASE_URL,
        api_key=config.API_KEY,
    )

    response = await client.chat.completions.create(
        model=model,
        messages=messages,
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    result = asyncio.run(run_llm_natively(model="gpt-oss-120b", messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "Hello, world!"}]))
    print(result)

# ------------------------------------------------------------
# Embeddings
# ------------------------------------------------------------

async def get_embeddings(texts: list[str]) -> list[list[float]]:
    client = AsyncOpenAI(
        base_url=config.BASE_URL,
        api_key=config.API_KEY,
    )
    response = await client.embeddings.create(
        input=texts,
        model=config.EMBEDDING_MODEL,
    )

    return [embedding.embedding for embedding in response.data]



