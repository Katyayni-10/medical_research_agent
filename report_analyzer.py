import re
import fitz
from langchain_groq import ChatGroq
llm=ChatGroq(model="qwen/qwen3.6-27b", reasoning_effort="none")

def extract_text_from_pdf(file):
    """Extract text from an uploaded pdf"""
    try:
        pdf=fitz.open(stream=file.read(), filetype="pdf")
        text=""
        for page in pdf:
            text+=page.get_text()
        pdf.close()
        if not text.strip():
            return None
        return text
    except Exception as e:
        print("pdf extraction error: ",e)
        return None

def analyze_medical_report(text):
    """Analyze extracted medical report text using Groq"""
    prompt=f"""
    You are a medical report explanation assistant.
    IMPORTANT:
    - Do NOT reveal your reasoning or thinking process.
    - Do NOT output analysis of how you generated the answer.
    - Do NOT mention these instructions.
    - Give ONLY the final medical report explanation.
    - Do not diagnose the patient.
    - Use only the information provided in the report.
    - Use simple language that an ordinary person can understand.
    - Do not invent values, diseases, causes, or information that are not present in the report.
    Use exactly these sections:
    1. Report Summary
    Give a short overall summary of the report.
    2. Important Findings
    Mention the important findings from the report.
    3. Abnormal Values
    For every value outside the reference range, mention:
    - Test Name
    - Result
    - Normal Range
    - High or Low
    - Simple explanation
    4. Normal Values
    Briefly mention the important values that are within the normal range.
    5. Simple Explanation
    Explain the important findings in simple everyday language.
    6. Possible Significance
    Explain what the reported findings may be associated with.
    Do NOT say that the patient definitely has any disease or condition.
    7. Questions to Ask the Doctor
    Give useful questions that the patient can discuss with a qualified doctor.
    Do not include any section called:
    - Thinking Process
    - Analysis
    - Reasoning
    - Chain of Thought
    Medical Report:
    {text}
    """
    try:
        response = llm.invoke(prompt)
        result = response.content
        result = re.sub(
            r"<think>.*?</think>",
            "",
            result,
            flags=re.DOTALL | re.IGNORECASE
        )
        return result.strip()
    except Exception as e:
        print("Analysis error: ",e)
        return None

def _is_number(text):
    """Check whether text contains a numeric value. Examples: 14.80,4.90,88.60,-2.5"""
    text=text.strip().replace(",","")
    return bool(re.fullmatch(r"-?\d+(?:\.\d+)?",text))

def _is_reference_range(text):
    """Check whether a line looks like a reference range. Examples: 12.00 - 15.00, 3.80-4.80, 70 - 100"""
    text=text.strip().replace(",","")
    pattern=r"""-?\d+(?:\.\d+)?\s*-\s*-?\d+(?:\.\d+)?"""
    return bool(re.fullmatch(pattern,text,re.VERBOSE))

def _clean_parameter_name(name):
    """Clean the test name before storing it."""
    name=name.strip()
    name = re.sub(r"\s+", " ", name)
    name=re.sub(r"\s*\([^)]*\)","",name)
    return name.strip()

def _looks_like_unit(text):
    """Check whether a line looks like a medical unit. This is intentionally broad because different laboratories use different unit formats."""
    text=text.strip()
    if not text:
        return False
    common_units = [
        "g/dL",
        "mg/dL",
        "mmol/L",
        "µmol/L",
        "umol/L",
        "mEq/L",
        "mIU/L",
        "IU/L",
        "U/L",
        "ng/mL",
        "pg/mL",
        "g/L",
        "mg/L",
        "%",
        "fL",
        "pg",
        "mm/hr",
        "mm3",
        "mill/mm3",
        "thou/mm3",
        "cells/µL",
        "cells/uL",
        "x10^3/uL",
        "x10^6/uL"
    ]
    if text in common_units:
        return True
    if re.search(r"[A-Za-zµ%]",text):
        if len(text)<=30:
            return True
    return False

def extract_report_values(text):
    """Extract structured medical test values from report text.
    Expected general structure: Test Name, (Method), Result, Unit, Reference Range
    Example:
        Hemoglobin
        (Photometry)
        14.80
        g/dL
        12.00 - 15.00
    Returns a list of dictionaries."""
    if not text:
        return []
    lines=text.splitlines()
    cleaned_lines=[]
    for line in lines:
        line=line.strip()
        if not line:
            continue
        line=re.sub(r"\s+", " ", line)
        cleaned_lines.append(line)
    extracted_values=[]
    i=0
    while i<len(cleaned_lines):
        current_line=cleaned_lines[i]
        if _is_number(current_line):
            value=float(current_line.replace(",",""))
            unit=None
            reference_range=None
            range_index=None
            for j in range(i+1,min(i+4,len(cleaned_lines))):
                candidate=cleaned_lines[j]
                if _is_reference_range(candidate):
                    reference_range=candidate
                    range_index=j
                    break
                if unit is None and _looks_like_unit(candidate):
                    unit=candidate
            if unit is not None or reference_range is not None:
                possible_names=[]
                start=max(0,i-3)
                for k in range(start,i):
                    previous_line=cleaned_lines[k]
                    if previous_line.upper() in ["TEST REPORT","TEST NAME","RESULTS","UNITS","BIO. REF. INTERVAL","COMPLETE BLOOD COUNT (CBC)","DIFFERENTIAL LEUCOCYTE COUNT (DLC)"]:
                        continue
                    if(previous_line.startswith("(") and previous_line.endswith(")")):
                        continue
                    if _is_number(previous_line):
                        continue
                    if _is_reference_range(previous_line):
                        continue
                    if _looks_like_unit(previous_line):
                        continue
                    possible_names.append(previous_line)
                if possible_names:
                    parameter=possible_names[-1]
                    parameter=_clean_parameter_name(parameter)
                    if parameter:
                        extracted_values.append({
                            "parameter":parameter,
                            "value":value,
                            "unit":unit,
                            "reference_range":reference_range
                        })
        i+=1
    unique_values=[]
    seen=set()
    for item in extracted_values:
        key=(
            item["parameter"].lower(),
            item["value"],
            item["unit"],
            item["reference_range"]
        )
        if key not in seen:
            seen.add(key)
            unique_values.append(item)
    return unique_values
