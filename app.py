# flake8: noqa: E302
import logging
import yaml

import uvicorn
from fastapi import FastAPI, File, UploadFile
from papergraph.graph import create_graph
from papergraph.state import get_iofile_input_state
from papergraph.output import push_result


def load_config(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        conf = yaml.safe_load(f)
    return conf

config = load_config('configs/config.yaml')
graph = create_graph(config['graph'])
app = FastAPI()

logger = logging.getLogger("uvicorn.error")

def build_input_state(upload_file: UploadFile):
    state = get_iofile_input_state(upload_file.file)
    return state

@app.post("/process")
async def run_graph(file: UploadFile = File(...)):
    logger.info("Processing file..")

    state = build_input_state(file)

    result = graph.invoke(state)

    push_result(result['result'])

    logger.info("Processing completed")

    return {"result": result['result']}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
