import httpx
from fastapi import FastAPI, HTTPException, Request, status
from starlette.background import BackgroundTask
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/openai/{path:path}")
async def openai_proxy(request: Request, path: str):
    base_url = "https://api.openai.com"
    _path = path
    _query = request.url.query

    headers = dict(request.headers)
    key = headers.pop('authorization', "")
    _headers = {"Content-Type": "application/json", "Authorization": key}

    return await proxy(request, base_url, _path, _query, _headers, 600)


@app.post("/azure/{path:path}")
async def azure_gpt_proxy(request: Request, path: str):
    # resource_name = os.environ.get('AZURE_RESOURCE')
    # deployment = os.environ.get('AZURE_DEPLOYMENT')
    # api_version = os.environ.get('AZURE_API_VERSION')
    # api_key = os.environ.get('AZURE_API_KEY')

    headers = dict(request.headers)
    resource_name = headers.pop('resource-name', "")
    deployment = headers.pop('deployment-name', "")
    api_version = headers.pop('api-version', "")
    api_key = headers.pop('api-key', "")


    base_url = f"https://{resource_name}.openai.azure.com"
    _path = f"/openai/deployments/{deployment}/{path}"
    _query = f"{request.url.query}&api-version={api_version}"
    _headers = {"Content-Type": "application/json", "api-key": api_key}

    return await proxy(request, base_url, _path, _query, _headers, 600)


async def proxy(request, base_url, path, query, headers, timeout):
    client = httpx.AsyncClient(base_url=base_url, http1=True, http2=False)
    url = httpx.URL(path=path, query=query.encode("utf-8"))
    req = client.build_request(
        request.method,
        url,
        headers=headers,
        content=request.stream(),
        timeout=timeout
    )

    try:
        r = await client.send(req, stream=True)
    except (httpx.ConnectError, httpx.ConnectTimeout) as e:
        print(f"{type(e)}")
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=e)
    except Exception as e:
        print(f"{type(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)

    return StreamingResponse(
        r.aiter_bytes(),
        status_code=r.status_code,
        media_type=r.headers.get("content-type"),
        background=BackgroundTask(r.aclose),
    )
