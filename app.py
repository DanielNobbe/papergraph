import uvicorn
from fastapi import FastAPI, File, UploadFile
from papergraph.graph import create_graph
from papergraph.state import get_iofile_input_state
from papergraph.output import push_result

import yaml

def load_config(path: str):
    with open(path, 'r') as f:
        config = yaml.safe_load(f)
    return config

config = load_config('configs/config.yaml')
graph = create_graph(config['graph'])
app = FastAPI()

def build_input_state(upload_file: UploadFile):
    state = get_iofile_input_state(upload_file.file)
    return state

@app.post("/process")
async def run_graph(file: UploadFile = File(...)):

    state = build_input_state(file)

    result = graph.invoke(state)

    push_result(result['result'])

    return {"result": result['result']}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
