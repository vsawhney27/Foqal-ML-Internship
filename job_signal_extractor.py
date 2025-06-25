import ollama
import json
import re
from typing import Dict, List, Any


def extract_job_signals(description: str) -> Dict[str, Any]:
    """
    Extract job signals from job description using Ollama Mistral model.
    
    Args:
        description: The job description text
        
    Returns:
        Dictionary containing tech_stack, urgency, and budget_indicators
    """
    
    system_prompt = """You are a job analysis expert. Extract key signals from job descriptions and return ONLY valid JSON.

Extract:
1. tech_stack: List of technologies, programming languages, frameworks, tools, platforms
2. urgency: Boolean - true if job shows urgency (immediate hire, ASAP, urgent, fast-paced, quickly, rapid growth, etc.)
3. budget_indicators: List of salary/compensation clues (competitive salary, equity, benefits, specific ranges like $100k, etc.)

Return ONLY this JSON format:
{
  "tech_stack": ["technology1", "technology2"],
  "urgency": true/false,
  "budget_indicators": ["indicator1", "indicator2"]
}"""

    user_prompt = f"Analyze this job description:\n\n{description}"
    
    try:
        response = ollama.chat(
            model='mistral',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ]
        )
        
        response_text = response['message']['content'].strip()
        
        # Extract JSON from response (in case model adds extra text)
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            result = json.loads(json_str)
        else:
            result = json.loads(response_text)
        
        # Ensure required keys exist with defaults
        return {
            "tech_stack": result.get("tech_stack", []),
            "urgency": result.get("urgency", False),
            "budget_indicators": result.get("budget_indicators", [])
        }
        
    except (json.JSONDecodeError, KeyError, Exception) as e:
        # Return empty structure if parsing fails
        return {
            "tech_stack": [],
            "urgency": False,
            "budget_indicators": []
        }


if __name__ == "__main__":
    # Test example
    sample_job = """
    We are looking for a Senior Python Developer to join our fast-paced startup immediately!
    
    Requirements:
    - 5+ years Python experience
    - AWS cloud experience
    - React frontend knowledge
    - Docker containerization
    
    We offer competitive salary and equity package. Join our rapidly growing team!
    """
    
    result = extract_job_signals(sample_job)
    print(json.dumps(result, indent=2))