# llm/serving
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from llm_model import LocalLLM
from loguru import logger
from typing import Annotated

app = FastAPI(
    title="LLM Block",
    description="copyright: nnminh322@gmail.com",
    version="1.0.0 beta",
)


class ChatRequest(BaseModel):
    prompts: list[str] | str


class ChatRespose(BaseModel):
    responses: list[str]


llm_model: LocalLLM | None = None


@app.on_event("startup")
def _startup():
    global llm_model
    llm_model = LocalLLM()
    logger.info("LLM engine loaded")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
async def chat(
    req: ChatRequest, api_key: Annotated[str, Header(..., alias="X-API-Key")]
):
    logger.info(f"Hihi có thằng vừa gọi request")
    try:
        ps = [req.prompts] if isinstance(req.prompts, str) else req.prompts
        texts = await llm_model.generate(ps)
        logger.info(f"User: {req}")
        return {"responses": texts}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))
