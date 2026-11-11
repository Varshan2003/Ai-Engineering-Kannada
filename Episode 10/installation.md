python3.14 -m venv .venv
source .venv/bin/activate          # your prompt now starts with (.venv)
pip install -U pip
pip install -qU langchain-unstructured unstructured-client "unstructured[pdf]" python-magic
