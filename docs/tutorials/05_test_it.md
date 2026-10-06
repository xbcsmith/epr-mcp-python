# 05 Test It

Time: 20 minutes.

Tools that call a live system are hard to test: EPR must be up, the data must
exist, and failures such as timeouts are difficult to cause. FastMCP and httpx2
give you two tools that remove all of that. The finished code is in
`checkpoint_05_tests/`: the module 04 server plus a test file.

## The idea

- An in-memory client connects to your server object directly. No process, no
  port, no stdio. `Client(server.mcp)` is all it takes.
- `httpx2.MockTransport` replaces the network. You hand it a function that
  receives each request and returns the response EPR should give.
- Your server has one function that creates HTTP clients, `new_client`. A test
  swaps it for one that uses the mock transport.

## Set up

```bash
cp -r checkpoint_05_tests/. work/
```

This puts `server.py`, `conftest.py`, and `test_workshop_server.py` in `work/`.
The conftest lets the tests import the `server` module next to them.

## Read the fixture

```python
@pytest.fixture
def epr(monkeypatch):
    """Replace the EPR client; set epr["respond"] to choose what EPR answers."""
    state = {"requests": [], "respond": lambda request: httpx2.Response(200, json={"data": EVENT})}

    def handler(request):
        state["requests"].append(request)
        return state["respond"](request)

    monkeypatch.setattr(
        server,
        "new_client",
        lambda: httpx2.AsyncClient(base_url="http://epr.test", transport=httpx2.MockTransport(handler)),
    )
    return state
```

Each test sets what EPR answers and then inspects the requests your server made.

## Read a test

```python
@pytest.mark.asyncio
async def test_fetch_event_rejects_a_malformed_id_without_calling_epr(epr):
    result = await call("fetch_event", {"id": "not-an-id"}, raise_on_error=False)
    assert result.is_error
    assert epr["requests"] == []
```

This one proves the validation from module 04: the call fails and EPR never saw
a request. The other tests cover the happy path, search criteria, the `schema`
alias, an EPR 404, an error inside a 200 response, an unreachable EPR, and the
bearer token.

## Run them

```bash
uv run pytest work
```

You should see `11 passed`. To run the finished checkpoint instead:

```bash
uv run pytest checkpoint_05_tests
```

## Exercise

Add a test for a failure no test covers yet: EPR is slow. Make the mock raise a
timeout and assert that the error message says the request timed out.

```python
@pytest.mark.asyncio
async def test_slow_epr_says_it_timed_out(epr):
    def slow(request):
        raise httpx2.ReadTimeout("too slow", request=request)

    epr["respond"] = slow
    result = await call("fetch_event", {"id": EPR_ID}, raise_on_error=False)
    assert result.is_error
    assert "timed out" in result.content[0].text
```

Then break the server on purpose: change `describe_error` so a timeout says
something different, and watch this test fail.

## Checkpoint

`uv run pytest work` passes, including your new test.

Next: [06 Use it from an editor](06_use_from_an_editor.md).
