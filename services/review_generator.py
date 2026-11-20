from openai_setup import setup_openai_client
import openai

def generate_review(prompt):
    """
        Generate a code review based on the given prompt.
        
        Args:
            prompt (str): The prompt describing the code to review
            
        Returns:
            str: The generated review text
    """

    # Call openai.chat.completions.create() with the following parameters:
    # - model: "gpt-6-luna"
    # - messages: a list containing a dictionary with "role" as "user" and "content" as the prompt
    # - max_completion_tokens: 1000
    response = openai.chat.completions.create(
        model="gpt-6-luna",
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=1000
    )

    # Extract and return the content from the first choice in the response
    return response.choices[0].message.content

def test_review():
    """Test the review generation with a simple code snippet"""
    # Set up the OpenAI client
    setup_openai_client()
    
    # Sample code to review
    code_snippet = """
    def calculate_sum(numbers):
        total = 0
        for num in numbers:
            total += num
        return total
    """
    
    prompt = f"Review this code snippet and provide feedback:\n\n{code_snippet}"
    
    # Generate and print the review
    review = generate_review(prompt)
    print("\nGenerated Review:")
    print("-----------------")
    print(review)

if __name__ == "__main__":
    test_review()  
   
