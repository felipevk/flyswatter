from fastapi import Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, generate_latest

REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)

# Defined as Gauge since values are rebuilt everytime it checks the jobs database
JOBS_SUCCEEDED_GAUGE = Gauge("jobs_succeeded_total", "Jobs Succeeded", ["type"])
JOBS_ENQUEUED_GAUGE = Gauge("jobs_enqueued_total", "Jobs Enqueued", ["type"])
JOBS_FAILED_GAUGE = Gauge("jobs_failed_total", "Jobs Failed", ["type"])


def inc_request_count(request: Request, response: Response):
    ignore = ["/", "/docs", "/openapi.json", "/health", "/metrics", "/favicon.ico"]
    if request.url.path in ignore:
        return

    route = request.scope.get("route")
    # Gets the template instead of the raw url
    # Eg: /users/{user_id} instead of /users/dsaio201h3fdsfdsx
    # It's possible to call route.path_format, but it will throw an exception if not found
    route_tmpl = getattr(route, "path_format", request.url.path)
    REQUEST_COUNT.labels(
        method=request.method, endpoint=route_tmpl, status=str(response.status_code)
    ).inc()


def clear_jobs_gauges():
    JOBS_SUCCEEDED_GAUGE.clear()
    JOBS_ENQUEUED_GAUGE.clear()
    JOBS_FAILED_GAUGE.clear()


def set_jobs_succeeded_gauge(job_type: str, count: int):
    JOBS_SUCCEEDED_GAUGE.labels(type=job_type).set(count)


def set_jobs_enqueued_gauge(job_type: str, count: int):
    JOBS_ENQUEUED_GAUGE.labels(type=job_type).set(count)


def set_jobs_failed_gauge(job_type: str, count: int):
    JOBS_FAILED_GAUGE.labels(type=job_type).set(count)
