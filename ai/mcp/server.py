# server.py

from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP, Context
import contextlib
import httpx
import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
PROMPTS_PATH = os.getenv("MCP_PROMPTS_DIR", "./prompts")

mcp = FastMCP("Chromosome Analysis", stateless_http=True, host="0.0.0.0", port=8080)


def load_prompt(filename: str) -> str:
    with open(os.path.join(PROMPTS_PATH, filename), "r", encoding="utf-8") as f:
        return f.read()


async def ask_ollama(model: str, prompt: str, temperature: float = 0.2) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False, "temperature": temperature},
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["response"].strip()


@mcp.tool(description="Pipeline de análise cromossômica")
async def full_pipeline(question: str, ctx: Context) -> dict:
    memory_text = ctx.memory.get_messages_string() if ctx.memory else ""

    prompt_context = load_prompt("context-manager.txt") \
        .replace("{{question}}", question) \
        .replace("{{memory}}", memory_text)
    step = await ask_ollama("llava:13b", prompt_context)

    if step == "just-text":
        prompt_start = load_prompt("agent-chat-start.txt").replace("{{question}}", question).replace("{{memory}}", memory_text)
        chat_input = await ask_ollama("llava:13b", prompt_start)

        if chat_input == "just-text":
            return {
                "resume": "Entrada apenas textual.",
                "data": {},
                "intruction": "Por favor, anexe uma imagem de metáfase para iniciarmos a análise cromossômica."
            }
        step = "image-received"

    if step == "image-received":
        prompt_check = load_prompt("agent-image-verify.txt").replace("{{question}}", question)
        image = await ask_ollama("llava:13b", prompt_check)

        if image != "metafase":
            return {
                "resume": "A imagem enviada não é uma metáfase.",
                "data": {},
                "intruction": "Envie uma imagem microscópica com cromossomos visíveis."
            }
        step = "segmentation"

    if step in ["segmentation", "rotation", "classification", "idiogram"]:
        task_prompt_file = {
            "segmentation": "agent-segment-images.txt",
            "rotation": "agent-position-analysis.txt",
            "classification": "agent-canvas-organizer.txt",
            "idiogram": "agent-chart-analysis.txt",
        }

        model_per_task = {
            "segmentation": "llava:13b",
            "rotation": "openhermes:2.5-mistral",
            "classification": "llava:13b",
            "idiogram": "codellama:13b-instruct"
        }

        prompt_file = task_prompt_file.get(step)
        model = model_per_task.get(step)

        if prompt_file is None or model is None:
            return {
                "resume": f"Etapa inválida: {step}",
                "data": {},
                "intruction": "Não foi possível continuar o fluxo."
            }

        task_prompt = load_prompt(prompt_file).replace("{{question}}", question).replace("{{memory}}", memory_text)
        task_output = await ask_ollama(model, task_prompt)

        format_prompt = load_prompt("response-formatter.txt") \
            .replace("{{question}}", question) \
            .replace("{{prev.output}}", task_output)

        result = await ask_ollama("llava:13b", format_prompt)

        return {
            "resume": f"Etapa: {step}",
            "data": {"raw": task_output},
            "intruction": result
        }

    return {
        "resume": "Etapa não reconhecida pelo gerenciador de contexto.",
        "data": {},
        "intruction": "Por favor, tente novamente com outra entrada."
    }


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with contextlib.AsyncExitStack() as stack:
        await stack.enter_async_context(mcp.session_manager.run())
        yield


app = FastAPI(title="Chromosome MCP Server", lifespan=lifespan)
app.mount("/mcp", mcp.streamable_http_app())
