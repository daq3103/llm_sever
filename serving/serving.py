import subprocess
import sys
import time
import os
import yaml
from loguru import logger

def run_vllm_server(config_path: str):
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    llm_config = config["llm"]
    resource_config = config["resource"]

    command = [
        sys.executable,  
        "-m", "vllm.entrypoints.openai.api_server",
        
        "--model", llm_config["model"],
        "--tensor-parallel-size", str(llm_config["tensor_parallel_size"]),
        "--dtype", llm_config["dtype"],
        "--max-model-len", str(llm_config["max_model_len"]),
        
        "--gpu-memory-utilization", str(resource_config["gpu_memory_utilization"]),
        "--swap-space", str(resource_config["swap_space"]),
        
        "--port", str(resource_config.get("port", 8000)), 
        "--host", resource_config.get("host", "localhost"), 
        # "--api-key", "nhatminh123"
    ]

    logger.info(f"Khởi chạy server vLLM: {' '.join(command)}")

    server_process = None
    try:
        server_process = subprocess.Popen(command, stdout=None, stderr=None)
        logger.info(f"Đang chờ server tại http://{resource_config.get('host', 'localhost')}:{resource_config.get('port', 8000)}...")
        server_process.wait() 

    except KeyboardInterrupt:
        logger.info("Phát hiện KeyboardInterrupt, đang dừng server...")
    except Exception as e:
        logger.exception(f"Server gặp lỗi: {e}")
    finally:
        if server_process and server_process.poll() is None:
            logger.info("Gửi tín hiệu dừng (terminate) tới server vLLM...")
            server_process.terminate()
            try:
                server_process.wait(timeout=10)
                logger.info("Server đã dừng.")
            except subprocess.TimeoutExpired:
                logger.warning("Server không dừng, ép buộc (kill)...")
                server_process.kill()
                logger.info("Server đã bị kill.")

if __name__ == "__main__":
    run_vllm_server("./configs.yaml")