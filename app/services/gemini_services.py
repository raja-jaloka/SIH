import os 
from dotenv import load_dotenv
from google import genai 
import json
from calculator import get_full_calculation

load_dotenv(override=True)

API_key=os.getenv("GEMINI_API_KEY2")


client=genai.Client(api_key=API_key) #authentication done 

def get_hyperlocal_data(hpuserprompt,questions):
    system_prompt=f"""
    You are an information extraction system.

    The user was asked these questions:

    {json.dumps(questions, indent=2)}

    The user's answer is:

    "{hpuserprompt}"

    Extract answers from the user's message.

    Return ONLY valid JSON.

    Rules:
    - Do not invent information.
    - Use null for unanswered fields.
    - The user may answer multiple questions in one message.
    """
    response=client.models.generate_content(
        model="gemini-3.7-flash",
        contents=system_prompt,
        config={
            "response_mime_type":"application/json"
        },
    )
    return response.text

def get_hyperlocal_questions_data(profile):
    system_prompt=f"""
    You are an AI business advisor for rural and semi-urban entrepreneurs in India.

    The entrepreneur profile is:

    {json.dumps(profile, indent=2)}

    Your goal is to collect ground-level LOCAL OBSERVATIONS that the user may
    know, but which may not be available in datasets.

    IMPORTANT:
    Do NOT ask the user to perform business analysis or draw conclusions.

    For example, DO NOT ask:
    - "Is demand high or low?"
    - "Is competition high?"
    - "Is this business profitable?"
    - "Is there a market opportunity?"

    Instead, ask for OBSERVABLE FACTS such as:
    - approximately how many similar businesses the user knows nearby
    - where people currently buy similar products
    - approximate distance to the nearest market or supplier
    - types of customers or establishments present nearby
    - whether customers travel elsewhere to buy the product
    - approximate local selling prices the user has observed
    - presence of restaurants, shops, schools, hostels, etc.
    - transport or supply difficulties the user has personally observed
    - seasonal changes they have personally noticed

    You, the AI, will later analyse these observations to determine:
    - market reach
    - opportunity
    - competition
    - threats
    - SWOT
    - product strategy
    - pricing considerations

    Ask a maximum of 5 concise, high-value questions.

    Adapt the questions specifically to the proposed business category and
    specific product/service.

    Do not ask for information already present in the entrepreneur profile.

    The user may answer all questions together in natural language and in any
    Indian language.

    Return ONLY valid JSON in this format:

    {{
        "questions": [
            {{
                "field": "competitor_observation",
                "question": "..."
            }}
        ]
    }}
    """
    questions_response=client.models.generate_content(
        model="gemini-3.7-flash",
        contents=system_prompt,
        config={
            "response_mime_type":"application/json"
        },
    )
    return json.loads(questions_response.text)



def structure_input(user_prompt):
    system_prompt2="""

    You are an information extraction assistant for a multilingual rural
    business advisory application in India.

    Extract the entrepreneur's basic information from their message.

    Required fields:
    - location: village, town, block, district, or geographic location mentioned
    - margin_capital: money available for the entrepreneur's required margin
      contribution, expressed as a numeric INR amount
    - business_category: broad business category or business idea
    - specific_product_or_service: specific product/service if mentioned

    Rules:
    - Understand English, Odia, Hindi, and other Indian languages.
    - Do not invent information.
    - Use null for missing information.
    - Convert Indian number expressions such as "two lakh", "50 thousand",
    or "2.5 lakh" into numeric INR values.
    - Distinguish a broad category from a specific product.
    Example: "dairy" = business_category, "paneer" = specific_product_or_service.
    - Return only valid JSON.
    """
    data=[]
    response=client.models.generate_content(
        model="gemini-3.7-flash",
        contents=f"{system_prompt2} User Prompt:{user_prompt}",
        config={
            "response_mime_type":"application/json"
        },
    )
    data.append(response.text)

    profile=json.loads(data[0])
    questions=get_hyperlocal_questions_data(profile)

    hpuserprompt=""" #Note: replace this with actual user input in production 
    There are around 6 dairy shops near my area.
    The dairy shops are usually busy in the mornings.
    Several small restaurants nearby regularly purchase milk and curd.
    I plan to mainly sell to households and local restaurants. 
    Milk supply is generally available, 
    but transportation can become difficult during heavy rains.
    """
    hp_data=get_hyperlocal_data(hpuserprompt,questions["questions"])
    data.append(hp_data)
    return profile, json.loads(data[1])


def get_advisory(result, hp_result, finance):
    system_prompt = f"""
    You are an AI business advisor for rural and semi-urban entrepreneurs in India.

    Generate a practical hyper-local business feasibility report.

    ENTREPRENEUR PROFILE:
    {json.dumps(result, indent=2)}

    HYPERLOCAL OBSERVATIONS PROVIDED BY THE ENTREPRENEUR:
    {json.dumps(hp_result, indent=2)}

    FINANCIAL CALCULATIONS GENERATED BY THE SYSTEM:
    {json.dumps(finance, indent=2)}

    Using the information above, provide:

    1. MARKET REACH
    Analyse the likely immediate customer base and potential distribution
    channels based only on the available information.

    2. OPPORTUNITY ANALYSIS
    Identify possible underserved opportunities or product strategies.
    Do not claim an opportunity is proven unless supported by the observations.

    3. SWOT ANALYSIS
    Provide:
    - Strengths
    - Weaknesses
    - Opportunities
    - Threats

    Tailor this to the entrepreneur's business, location, observations,
    and financial capacity.

    4. THREAT IDENTIFICATION
    Identify practical risks such as:
    - supply chain problems
    - transportation difficulties
    - seasonality
    - competition
    - dependency on particular customers

    5. COMPETITOR ANALYSIS
    Interpret the user's observations regarding existing competitors.
    Do not invent exact market shares or competitor statistics.

    6. PRODUCT AND PRICING STRATEGY
    Suggest practical product positioning, customer segments, and pricing
    considerations based on observed local prices and competition.

    7. FINANCIAL FEASIBILITY
    Interpret the calculated:
    - project cost
    - loan amount
    - scheme
    - interest rate
    - tenure
    - EMI

    Explain whether the repayment obligation appears manageable given the
    business context.

    IMPORTANT RULES:
    - Do not invent local statistics.
    - Clearly distinguish observations from AI inferences.
    - Do not claim precise population, market size, or demand figures unless
    they were provided.
    - Be practical and actionable.
    - Highlight uncertainty where information is insufficient.
    - The financial calculations are system-generated facts and should not
    be recalculated or changed.

    Return the report in clear structured JSON.

    Format:

    {{
        "market_reach": "...",
        "opportunity_analysis": "...",
        "swot": {{
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": []
        }},
        "threat_identification": [],
        "competitor_analysis": "...",
        "product_strategy": "...",
        "pricing_strategy": "...",
        "financial_feasibility": "...",
        "key_recommendations": []
        }}
    """
    response=client.models.generate_content(
        model="gemini-3.7-flash",
        contents=system_prompt,
      )
    return response.text 

#Note: replace this with actual user input in production 
#result=structure_input("I am from Mandya, have 12 thousand rupees and want to start a dairy business.")
result,hp_result=structure_input("ମୁଁ ମଣ୍ଡିଆ ଜିଲ୍ଲାରୁ ଆସିଛି, ମୋ ପାଖରେ ୨.୪ ଲକ୍ଷ ଟଙ୍କା ମାର୍ଜିନ୍ କ୍ୟାପିଟାଲ୍ ଅଛି ଏବଂ ମୁଁ ଏକ ଡେୟାରୀ ବ୍ୟବସାୟ ଆରମ୍ଭ କରିବାକୁ ଚାହୁଁଛି।")
print(result)
print(hp_result)

finance=get_full_calculation(result["margin_capital"])

advisory=get_advisory(result,hp_result,finance)
print(advisory)

