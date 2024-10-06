import uvicorn
from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route


async def home(request):
    return HTMLResponse(f"""<pre>
            url: {str(request.url)}
            message: Это сервер 2
            client:
                host: {request.client.host}
                port: {request.client.port}
            headers:
                {('<br>' + '&nbsp' * 12).join(k + ': ' + v for k, v in request.headers.items())}
        </pre>""")


async def monitoring(request):
    return JSONResponse(content={'message': 'INTERNAL_SERVER_ERROR', 'code': '500'}, status_code=500)


app = Starlette(debug=True, routes=[Route('/', home), Route('/monitoring', monitoring)])

if __name__ == "__main__":
    uvicorn.run("server2:app", host="localhost", port=82, reload=True,
                ssl_keyfile="./service.key",
                ssl_certfile="./service.crt"
                )
