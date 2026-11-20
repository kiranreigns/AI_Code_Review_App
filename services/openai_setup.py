import os

import openai
from dotenv import load_dotenv

load_dotenv()

def setup_openai_client():
  """
  Set up the OpenAI client with API key from environment variables.

  Returns:
      str: The name of the model to use for code review
  """
  api_key = os.getenv('OPENAI_API_KEY')
  client = openai.OpenAI(api_key=api_key)
  model = 'gpt-6-luna'
  return client, model

def test_setup():
  """Test the OpenAI client setup"""
  client, model = setup_openai_client()
  if client.api_key:
      print(f"OpenAI client set up successfully with model: {model}")
  else:
      print("Failed to set up OpenAI client. Check your API key.")

if __name__ == "__main__":
  test_setup()