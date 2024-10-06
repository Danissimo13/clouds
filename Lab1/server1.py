import uvicorn
from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route


async def home(request):
    return HTMLResponse(f"""<pre>
            url: {str(request.url)}
            message: Это сервер 1
            client:
                host: {request.client.host}
                port: {request.client.port}
            headers:
                {('<br>' + '&nbsp' * 12).join(k + ': ' + v for k, v in request.headers.items())}
        </pre>""")


async def ping(request):
    return JSONResponse(content={'message': 'OK', 'code': '200'}, status_code=200)


app = Starlette(debug=True, routes=[Route('/', home), Route('/ping', ping)])

if __name__ == "__main__":
    uvicorn.run("server1:app", host="localhost", port=81, reload=True,
                ssl_keyfile="./service.key",
                ssl_certfile="./service.crt"
                )
