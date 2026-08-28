import os 
from dotenv import load_dotenv
from google import genai 
import json

load_dotenv(override=True)

API_key=os.getenv("GEMINI_API_KEY")


client=genai.Client(api_key=API_key) #authentication done 

def structure_input(user_prompt):
    system_prompt="""
    You are an information extraction system for a rural business advisory application in India.

    Extract:
    - location
    - margin_capital
    - business_category

    Rules:
    - Do not invent missing information.
    - Use null if information is missing.
    - Convert amounts such as "one lakh" or "80 thousand" into numeric INR.
    - Return valid JSON only."""

    response=client.models.generate_content(
        model="gemini-3.7-flash",
        contents=f"{system_prompt} User Prompt:{user_prompt}",
        config={
            "response_mime_type":"application/json"
        },
    )

    return json.loads(response.text)

result=structure_input("I am from Mandya, have one lakh rupees and want to start a dairy business.")

print(result)