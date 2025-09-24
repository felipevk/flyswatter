from fastapi import Request, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

REQUEST_COUNT = Counter(
    "http_requests_total", 
    "Total HTTP requests",
    ["method", "endpoint", "status"])

def inc_request_count(request: Request, response: Response):
    ignore = [
        "/",
        "/docs",
        "/openapi.json",
        "/health",
        "/metrics",
        "/favicon.ico"
    ]
    if request.url.path in ignore:
        return

    route = request.scope.get("route")
    # Gets the template instead of the raw url
    # Eg: /users/{user_id} instead of /users/dsaio201h3fdsfdsx
    # It's possible to call route.path_format, but it will throw an exception if not found
    route_tmpl = getattr(route, "path_format", request.url.path)
    REQUEST_COUNT.labels(
            method=request.method,
            endpoint=route_tmpl,
            status=str(response.status_code)
    ).inc()