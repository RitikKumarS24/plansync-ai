import json
import os
from google import genai
from google.genai import types

# Initialize Gemini Client
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
  print("⚠️ Warning: GEMINI_API_KEY environment variable not set. Please set it before running.")

client = genai.Client(api_key=api_key)

# Load Test Cases
with open("tests/test_cases.json", "r") as f:
  test_cases = json.load(f)

print(f"🚀 Running Evaluation Suite on {len(test_cases)} test cases...\n")

passed_tests = 0

for tc in test_cases:
  test_id = tc["test_id"]
  print(f"--- Running {test_id}: {tc['description']} ---")
  
  inputs = tc["inputs"]
  prompt = f"""
            Student Name: {inputs['student_name']}
            Subjects & Topics: {inputs['subjects']}
            Exam Timeline: {inputs['exam_timeline']}
            Available Daily Hours: {inputs['daily_hours']} hours/day
            
            Generate a structured study schedule adhering strictly to the JSON schema.
            """
  
  system_instruction = "You are PlanSync AI, an expert academic scheduling engine. Output valid JSON matching the schema with zero time overlaps."

  try:
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )
    
    # Test 1: JSON Parse Check
    result_json = json.loads(response.text)
    print(f"  ✅ JSON Validity: PASSED")
    
    # Test 2: Structure Check
    schedule = result_json.get("schedule", []) or result_json.get("daily_schedule", [])
    if len(schedule) > 0:
      print(f"  ✅ Structure Check: PASSED ({len(schedule)} days generated)")
      passed_tests += 1
    else:
      print(f"  ❌ Structure Check: FAILED (No schedule days found)")

  except Exception as e:
    print(f"  ❌ Test FAILED with exception: {e}")
  
  print("\n" + "="*40 + "\n")

print(f"🏁 Evaluation Complete. Passed {passed_tests}/{len(test_cases)} test cases.")