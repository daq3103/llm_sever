# llm/llm_model.py
import yaml
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.utils import random_uuid
from vllm.sampling_params import SamplingParams
from loguru import logger

with open("./configs.yaml", "r") as f:
    config_llm = yaml.safe_load(f)


_sampling = SamplingParams(
    temperature=config_llm["llm"]["temperature"],
    top_p=config_llm["llm"]["top_p"],
    max_tokens=config_llm["llm"]["max_tokens"],
)

_engine_args = AsyncEngineArgs(
    model=config_llm["llm"]["model"],
    tensor_parallel_size=config_llm["llm"]["tensor_parallel_size"],
    dtype=config_llm["llm"]["dtype"],
    max_model_len=config_llm["llm"]["max_model_len"],
    gpu_memory_utilization=config_llm["resource"]["gpu_memory_utilization"],
    swap_space=config_llm["resource"]["swap_space"]
)


class LocalLLM:
    def __init__(self):
        self.engine = AsyncLLMEngine.from_engine_args(_engine_args)

    async def generate(self, prompts: list[str]) -> list[str]:
        if isinstance(prompts, str):
            prompts = [prompts]
        
        texts: list[str] = []
        
        for prompt in prompts:
            request_id = random_uuid()
            results_generators = self.engine.generate(
                prompt,
                _sampling,  # sampling_params đứng thứ hai
                request_id  # request_id đứng thứ ba
            )
            final_output = []
            try:
                async for response_output in results_generators:
                    final_output.append(response_output)
            except Exception as e:
                logger.exception(f"Lỗi trong quá trình generate của vLLM: {e}")
                raise e

            if final_output:
                out = final_output[-1]  
                if out.outputs and not out.finished:
                    logger.warning(f"Request {out.request_id} finished incomplete: {out.outputs[0].finish_reason}")

                if out.outputs:
                    texts.append(out.outputs[0].text)
                else:
                    texts.append("")
            else:
                texts.append("")

        return texts