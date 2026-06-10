import re

from httpx import AsyncClient


async def test_provided_trace_id_echoed(client: AsyncClient) -> None:
    resp = await client.get(
        "/auth/users/me",
        headers={"X-Trace-Id": "my-custom-trace-id"},
    )

    assert resp.headers["x-trace-id"] == "my-custom-trace-id"


async def test_missing_trace_id_generates_uuid(client: AsyncClient) -> None:
    resp = await client.get("/auth/users/me")

    trace_id = resp.headers.get("x-trace-id", "")
    assert re.fullmatch(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", trace_id
    )


async def test_different_requests_get_different_trace_ids(client: AsyncClient) -> None:
    resp1 = await client.get("/auth/users/me")
    resp2 = await client.get("/auth/users/me")

    assert resp1.headers["x-trace-id"] != resp2.headers["x-trace-id"]
