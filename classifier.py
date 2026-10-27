import os
from openai import APITimeoutError
from openai import OpenAI

API_KEY = os.getenv(
    "OPENAI_API_KEY"
)

client = OpenAI(api_key=API_KEY)

categories_array = ["hardware", "software", "access", "data", "other"]

PROMPT_TO_CLASSIFY_TICKETS= f"""You are an IT ticket classifier.
    Classify the ticket into exactly one of the following categories: {categories_array}.
    Return only the category name."""

def classify_tickets(input_text):
    if not input_text.strip():
        raise ValueError("Ticket text cannot be empty")
        
    try:
        response = client.responses.create(
            model="gpt-6-luna",
            instructions=PROMPT_TO_CLASSIFY_TICKETS,
            input= input_text)
        
        if response.output_text.strip() in categories_array:
            return response.output_text.strip()
        else:
            print(f"Error in category: {response.output_text.strip()}")
            return "Category not defined"
    except APITimeoutError as error:
        print(f"Error encountered {error}")
        raise