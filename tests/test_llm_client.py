from unittest import mock

import httpx2 as httpx
import openai
import pytest

from services.llm_client import LLMClient, LLMError

REQ = httpx.Request("POST", "http://test")


def make_response(content="ok"):
    msg = mock.Mock(content=content)
    return mock.Mock(choices=[mock.Mock(message=msg)])


def make_llm(effects, **kwargs):
    sdk = mock.MagicMock()
    sdk.with_options.return_value = sdk
    sdk.chat.completions.create.side_effect = effects
    return LLMClient(client=sdk, **kwargs), sdk


def status_error(cls, code):
    return cls("err", response=httpx.Response(code, request=REQ), body=None)


@pytest.fixture(autouse=True)
def no_sleep():
    with mock.patch("time.sleep") as s:
        yield s


def test_success_first_try(no_sleep):
    llm, sdk = make_llm([make_response("great")])
    assert llm.complete("hi") == "great"
    assert sdk.chat.completions.create.call_count == 1
    no_sleep.assert_not_called()


def test_retries_then_succeeds(no_sleep):
    rl = status_error(openai.RateLimitError, 429)
    llm, sdk = make_llm([rl, rl, make_response()])
    assert llm.complete("hi") == "ok"
    assert sdk.chat.completions.create.call_count == 3
    assert no_sleep.call_count == 2


def test_backoff_grows(no_sleep):
    rl = status_error(openai.RateLimitError, 429)
    llm, _ = make_llm([rl, rl, rl, make_response()])
    llm.complete("hi")
    delays = [c.args[0] for c in no_sleep.call_args_list]
    assert delays[0] < delays[1] < delays[2]


def test_gives_up_after_max_retries(no_sleep):
    rl = status_error(openai.RateLimitError, 429)
    llm, sdk = make_llm([rl] * 10, max_retries=2)
    with pytest.raises(LLMError):
        llm.complete("hi")
    assert sdk.chat.completions.create.call_count == 3


def test_connection_error_is_retried():
    llm, sdk = make_llm([openai.APIConnectionError(request=REQ), make_response()])
    assert llm.complete("hi") == "ok"
    assert sdk.chat.completions.create.call_count == 2


def test_auth_error_not_retried():
    llm, sdk = make_llm([status_error(openai.AuthenticationError, 401)])
    with pytest.raises(LLMError, match="Authentication"):
        llm.complete("hi")
    assert sdk.chat.completions.create.call_count == 1


def test_bad_request_not_retried():
    llm, sdk = make_llm([status_error(openai.BadRequestError, 400)])
    with pytest.raises(LLMError):
        llm.complete("hi")
    assert sdk.chat.completions.create.call_count == 1


def test_empty_response_raises():
    llm, _ = make_llm([make_response("")])
    with pytest.raises(LLMError):
        llm.complete("hi")


@pytest.mark.parametrize("prompt", ["", "   ", None])
def test_empty_prompt_rejected(prompt):
    llm, _ = make_llm([])
    with pytest.raises(ValueError):
        llm.complete(prompt)


def test_review_diff_builds_prompt():
    llm, sdk = make_llm([make_response()])
    llm.review_diff("a.py", "+print(1)", commit_message="add print")
    prompt = sdk.chat.completions.create.call_args.kwargs["messages"][0]["content"]
    assert "a.py" in prompt and "+print(1)" in prompt and "add print" in prompt
    for section in ("Summary of changes", "Potential issues",
                    "Suggestions for improvement", "Overall quality assessment"):
        assert section in prompt


def test_review_diff_truncates_large_diff():
    llm, sdk = make_llm([make_response()], max_diff_chars=50)
    llm.review_diff("a.py", "x" * 500)
    prompt = sdk.chat.completions.create.call_args.kwargs["messages"][0]["content"]
    assert "x" * 51 not in prompt and "[diff truncated]" in prompt


def test_model_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "env-model")
    llm, _ = make_llm([])
    assert llm.model == "env-model"


def test_explicit_model_wins(monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "env-model")
    llm, _ = make_llm([], model="explicit")
    assert llm.model == "explicit"


@pytest.mark.parametrize("kwargs", [
    {"max_retries": -1}, {"base_delay": -1}, {"base_delay": 5, "max_delay": 1},
    {"max_completion_tokens": 0},
])
def test_invalid_config_rejected(kwargs):
    with pytest.raises(ValueError):
        make_llm([], **kwargs)
