import os
from typing import Dict
from openai import AsyncOpenAI


async def generate_cold_email(
    resume_profile: Dict,
    professor: Dict,
    user_name: str,
) -> str:
    """
    Call OpenAI mini model to generate a cold email.
    Expects OPENAI_API_KEY in the environment.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return (
            "OPENAI_API_KEY is not configured. "
            "Please set it in the environment and restart the backend."
        )

    client = AsyncOpenAI(api_key=api_key)

    skills = ", ".join(resume_profile.get("skills", []))
    interests = ", ".join(resume_profile.get("interests", []))
    experiences = "\n".join(resume_profile.get("experiences", [])[:3])  # Top 3 experiences

    prof_name = professor.get("name", "Professor")
    institution = professor.get("institution", "")
    department = professor.get("department", "")
    research_focus = professor.get("research_focus", "")

    system_prompt = (
        "You are an assistant that writes concise, professional cold outreach emails "
        "from a student to a professor about potential research opportunities. "
        "Use clear, respectful language appropriate for high school or undergraduate students. "
        "The email should be personalized, specific, and demonstrate genuine interest in the professor's work."
    )

    user_prompt = f"""Write a personalized cold email from a student named {user_name} to {prof_name} at {institution}, in the {department} department.

The professor's research focus:
{research_focus}

Student background:
- Skills: {skills}
- Research Interests: {interests}
- Relevant Experiences:
{experiences}

Requirements:
- Include a clear subject line
- 2-4 short paragraphs in the email body
- Clearly connect the student's background to the professor's research
- Mention specific aspects of the professor's work that interest the student
- Include a polite closing and a specific ask about potential research opportunities
- Professional but warm tone
- Keep it concise (under 200 words)

Format the response as:
Subject: [subject line]

[email body]"""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=500,
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating email: {str(e)}"

