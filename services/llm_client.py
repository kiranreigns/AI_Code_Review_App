import logging
import os
import random
import time

import openai

from services.openai_setup import setup_openai_client

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gpt-6-luna"  # override with the OPENAI_MODEL env var
DEFAULT_MAX_COMPLETION_TOKENS = 1000
# Rough guard against exceeding the model context window.
MAX_DIFF_CHARS = 20000

# Transient failures worth retrying. Timeouts are a subclass of APIConnectionError.
RETRYABLE_ERRORS = (
    openai.RateLimitError,
    openai.APIConnectionError,
    openai.InternalServerError,
)

REVIEW_PROMPT_TEMPLATE = """Review the following code change and provide feedback.

File: {file_path}
{context}
Diff:
{diff}

Focus on correctness bugs, security issues, readability and missing tests. \
Be specific and reference the relevant lines."""


class LLMError(Exception):
    """Raised when the LLM could not produce a response."""


class LLMClient:
    """Reusable wrapper around the OpenAI client with retries and error handling."""

    def __init__(
        self,
        client=None,
        model=None,
        max_completion_tokens=DEFAULT_MAX_COMPLETION_TOKENS,
        max_retries=4,
        base_delay=1.0,
        max_delay=30.0,
        max_diff_chars=MAX_DIFF_CHARS,
    ):
        """
        Args:
            client: Optional OpenAI client. Built via setup_openai_client() if omitted.
            model: Model name. Defaults to $OPENAI_MODEL, then DEFAULT_MODEL.
            max_completion_tokens: Cap on tokens in each response.
            max_retries: Retries after the first attempt for transient errors.
            base_delay: Initial backoff delay in seconds (doubles each retry).
            max_delay: Upper bound for a single backoff delay in seconds.
            max_diff_chars: Diffs longer than this are truncated in review prompts.

        Raises:
            ValueError: If a numeric setting is out of range.
        """
        if max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        if base_delay < 0 or max_delay < base_delay:
            raise ValueError("require 0 <= base_delay <= max_delay")
        if max_completion_tokens <= 0 or max_diff_chars <= 0:
            raise ValueError("max_completion_tokens and max_diff_chars must be > 0")

        # Disable the SDK's built-in retries so they don't multiply with ours.
        self._client = (client or setup_openai_client()).with_options(max_retries=0)
        self.model = model or os.getenv("OPENAI_MODEL") or DEFAULT_MODEL
        self.max_completion_tokens = max_completion_tokens
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.max_diff_chars = max_diff_chars

    def complete(self, prompt):
        """
        Send a prompt and return the response text.

        Retries rate limits, connection errors/timeouts and 5xx with exponential
        backoff plus jitter. Other errors fail immediately.

        Raises:
            ValueError: If the prompt is empty.
            LLMError: If no response could be obtained.
        """
        if not prompt or not prompt.strip():
            raise ValueError("prompt must be a non-empty string")

        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_completion_tokens=self.max_completion_tokens,
                )
            except RETRYABLE_ERRORS as e:
                last_error = e
                if attempt == self.max_retries:
                    break
                delay = self._backoff_delay(attempt)
                logger.warning(
                    "Attempt %d/%d failed (%s). Retrying in %.1fs",
                    attempt + 1, self.max_retries + 1, type(e).__name__, delay,
                )
                time.sleep(delay)
                continue
            except openai.AuthenticationError as e:
                raise LLMError("Authentication failed. Check OPENAI_API_KEY.") from e
            except openai.APIError as e:
                raise LLMError(f"OpenAI API error: {e}") from e

            if not response.choices:
                raise LLMError("OpenAI returned no choices.")
            content = response.choices[0].message.content
            if not content:
                raise LLMError("OpenAI returned an empty response.")
            return content

        raise LLMError(
            f"Failed after {self.max_retries + 1} attempts: {last_error}"
        ) from last_error

    def review_diff(self, file_path, diff, commit_message=None):
        """
        Build a review prompt for a code diff and return the review text.

        Args:
            file_path: Path of the changed file.
            diff: Unified diff content.
            commit_message: Optional commit message to give the model context.
        """
        if not diff or not diff.strip():
            raise ValueError("diff must be a non-empty string")
        if len(diff) > self.max_diff_chars:
            logger.warning("Diff for %s truncated to %d chars", file_path, self.max_diff_chars)
            diff = diff[: self.max_diff_chars] + "\n... [diff truncated]"
        context = f"Commit message: {commit_message}\n" if commit_message else ""
        prompt = REVIEW_PROMPT_TEMPLATE.format(
            file_path=file_path, context=context, diff=diff
        )
        return self.complete(prompt)

    def _backoff_delay(self, attempt):
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        return delay + random.uniform(0, delay * 0.25)  # jitter
