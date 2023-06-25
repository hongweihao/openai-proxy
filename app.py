from fastapi import FastAPI, HTTPException, Request, status
from starlette.background import BackgroundTask
from starlette.middleware.cors import CORSMiddleware
import httpx
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
async def proxy(request: Request, path: str):
    client = httpx.AsyncClient(base_url="https://api.openai.com", http1=True, http2=False)
    url = httpx.URL(path=path, query=request.url.query.encode("utf-8"))

    headers = dict(request.headers)
    key = headers.pop('authorization', "")
    auth_headers_dict = {"Content-Type": "application/json", "Authorization": key}
    req = client.build_request(
        request.method,
        url,
        headers=auth_headers_dict,
        content=request.stream(),
        timeout=600
    )

    try:
        r = await client.send(req, stream=True)
    except (httpx.ConnectError, httpx.ConnectTimeout) as e:
        error_info = (
            f"{type(e)}: {e} | "
            f"Please check if host={request.client.host} can access?"
        )
        print(error_info)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=error_info
        )
    except Exception as e:
        print(f"{type(e)}:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e
        )

    return StreamingResponse(
        r.aiter_bytes(),
        status_code=r.status_code,
        media_type=r.headers.get("content-type"),
        background=BackgroundTask(r.aclose),
    )
