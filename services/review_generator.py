import functools
import logging

from services.llm_client import LLMClient, LLMError


@functools.lru_cache(maxsize=1)
def get_default_client():
    """Create the shared LLMClient once and reuse it."""
    return LLMClient()


def generate_review(prompt, llm=None):
    """
    Generate a code review based on the given prompt.

    Args:
        prompt (str): The prompt describing the code to review
        llm: Optional LLMClient. A shared default is used if omitted.

    Returns:
        str: The generated review text

    Raises:
        ValueError: If the prompt is empty
        LLMError: If the review could not be generated
    """
    return (llm or get_default_client()).complete(prompt)


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
    except LLMError as e:
        print(f"Could not generate review: {e}")
        return

    print("\nGenerated Review:")
    print("-----------------")
    print(review)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_review()
