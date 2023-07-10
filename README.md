# OpenAI Proxy

Super simple implementation of OpenAI API and Azure GPT API proxy forwarding based on FastAPI and httpx.



## Get start

### 1. Install dependencies

```shell
pip install -r requirments.txt
```

### 2. Run server

```shell
python -m uvicorn app:app
```

## Usage

### 1. OpenAI 

![openai_usage_authorization.png](images/openai_usage_authorization.png)

![openai_usage_body.png](images/openai_usage_body.png)

### 2. Azure GPT

![azure_gpt_usage_authorization.png](images/azure_gpt_usage_authorization.png)

![azure_gpt_usage_header.png](images/azure_gpt_usage_header.png)

![azure_gpt_usage_body.png](images/azure_gpt_usage_body.png)

# Credit

This project is a simplified version
of [beidongjiedeguang/openai-forward](https://github.com/beidongjiedeguang/openai-forward).