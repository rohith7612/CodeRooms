import os
import json
import openai
from django.conf import settings
from .models import Problem

def generate_problem_via_ai(topic, difficulty):
    api_key = settings.OPENAI_API_KEY

    if not api_key:
        print("OpenAI API Key not found.")
        return None

    client = openai.OpenAI(api_key=api_key)

    prompt = f"""
    Generate a unique Data Structures and Algorithms problem.
    Topic: {topic}
    Difficulty: {difficulty}
    
    Output must be valid JSON with the following schema:
    {{
        "title": "Problem Title",
        "description": "Full problem description (markdown supported).",
        "initial_code": "Python class Solution with method signature.",
        "test_cases": [
            {{"input": "arg1=val1, arg2=val2", "output": "expected_result"}},
            {{"input": "...", "output": "..."}}
        ]
    }}
    Ensure the test cases cover edge cases. Provide at least 3 test cases.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a senior technical interviewer designed to generate coding problems."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        data = json.loads(content)
        
        # Create and Save Problem
        problem = Problem.objects.create(
            title=data.get("title", "AI Generated Problem"),
            description=data.get("description", "No description provided."),
            difficulty=difficulty,
            topic=topic,
            initial_code=data.get("initial_code", ""),
            test_cases=data.get("test_cases", [])
        )
        return problem

    except Exception as e:
        print(f"Error generating problem: {e}")
        return None
