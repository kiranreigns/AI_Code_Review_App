import logging
import random
import time

import openai

from services.openai_setup import setup_openai_client

logger = logging.getLogger(__name__)

MODEL = "gpt-6-luna"
MAX_COMPLETION_TOKENS = 1000

# Errors worth retrying: transient network/server problems and rate limits.
# Timeouts are a subclass of APIConnectionError.
RETRYABLE_ERRORS = (
    openai.RateLimitError,
    openai.APIConnectionError,
    openai.InternalServerError,
)


class ReviewGenerationError(Exception):
    """Raised when a review could not be generated."""


def generate_review(
    prompt,
    client=None,
    max_retries=4,
    base_delay=1.0,
    max_delay=30.0,
):
    """
    Generate a code review based on the given prompt.

    Transient failures (rate limits, connection errors/timeouts, 5xx) are retried
    with exponential backoff plus jitter: roughly 1s, 2s, 4s, 8s (capped at max_delay).
    Non-retryable failures (bad API key, invalid request, etc.) fail immediately.

    Args:
        prompt (str): The prompt describing the code to review
        client: Optional OpenAI client. Created from the environment if omitted.
        max_retries (int): Retries after the first attempt
        base_delay (float): Initial backoff delay in seconds
        max_delay (float): Upper bound for a single backoff delay in seconds

    Returns:
        str: The generated review text

    Raises:
        ValueError: If the prompt is empty
        ReviewGenerationError: If the review could not be generated
    """
    if not prompt or not prompt.strip():
        raise ValueError("prompt must be a non-empty string")

    # Disable the SDK's built-in retries so they don't multiply with ours.
    client = (client or setup_openai_client()).with_options(max_retries=0)

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=MAX_COMPLETION_TOKENS,
            )
        except RETRYABLE_ERRORS as e:
            last_error = e
            if attempt == max_retries:
                break
            delay = min(base_delay * (2 ** attempt), max_delay)
            delay += random.uniform(0, delay * 0.25)  # jitter avoids thundering herd
            logger.warning(
                "Attempt %d/%d failed (%s). Retrying in %.1fs",
                attempt + 1, max_retries + 1, type(e).__name__, delay,
            )
            time.sleep(delay)
            continue
        except openai.AuthenticationError as e:
            raise ReviewGenerationError(
                "Authentication failed. Check OPENAI_API_KEY."
            ) from e
        except openai.APIError as e:
            # Bad request, not found, permission denied, etc. Retrying won't help.
            raise ReviewGenerationError(f"OpenAI API error: {e}") from e

        if not response.choices:
            raise ReviewGenerationError("OpenAI returned no choices.")

        content = response.choices[0].message.content
        if not content:
            raise ReviewGenerationError("OpenAI returned an empty review.")
        return content

    raise ReviewGenerationError(
        f"Failed after {max_retries + 1} attempts: {last_error}"
    ) from last_error


def test_review():
    """Test the review generation with a simple code snippet"""
    code_snippet = """
    def calculate_sum(numbers):
        total = 0
        for num in numbers:
            total += num
        return total
    """

    prompt = f"Review this code snippet and provide feedback:\n\n{code_snippet}"

    try:
        review = generate_review(prompt)
    except ReviewGenerationError as e:
        print(f"Could not generate review: {e}")
        return

    print("\nGenerated Review:")
    print("-----------------")
    print(review)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_review()
