import os
import base64
from groq import Groq
from dotenv import load_dotenv
import re

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def encode_image(file):
    image_bytes=file.read()
    encoded_image=base64.b64encode(image_bytes).decode("utf-8")
    return encoded_image

def clean_model_response(text):
    if not text:
        return None
    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE
    )
    return text.strip()

def analyze_medical_scan(file, scan_type):
    try:
        encoded_image=encode_image(file)
        prompt=f"""
        You are an AI-assisted medical imaging education and research assistant.
        The user has uploaded a medical image.
        scan type: {scan_type}
        Analyze the image carefully
        Do not say that the patient definitely has a disease or medical condition.
        Describe visible observations and possible findings that should be discussed with a qualified doctor.
        Use simple language that can be understood easily by the user
        Structure your reponse as follows:
        1.Scan Type
        state the type of scan provided
        2.Observations
        Describe the major visible structures and general observations
        3.Findings
        Mention any visible features that may be important to discuss with a doctor
        If nothing is concerning do tell that
        4.Interpretation
        Explain what the observations can be associated with
        5.Discussion
        Give useful question to users to dicuss with the doctor
"""
        response=client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[
                {
                    "role":"user",
                    "content":[{"type":"text", "text":prompt},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{encoded_image}"}}]
                }
            ],
            temperature=0.2,
            max_completion_tokens=2000
        )
        raw_response = response.choices[0].message.content
        clean_response = clean_model_response(raw_response)
        return clean_response
    except Exception as e:
        print("scan analysis error: ",e)
        return None