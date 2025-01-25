import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from the .env file
load_dotenv("./openai_key.env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to interact with OpenAI API
def chat_with_gpt(prompt):
    try:
        # Call the Chat API
        response = client.chat.completions.create(model="gpt-3.5-turbo",  # Replace with "gpt-3.5-turbo" if using that model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7)
        # Extract and return the assistant's reply
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# Test the function
if __name__ == "__main__":
    prompt = "What is the largest animal on Earth?"
    print(chat_with_gpt(prompt))
