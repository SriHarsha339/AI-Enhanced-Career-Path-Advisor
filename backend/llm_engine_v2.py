"""
Enhanced Ollama LLM Engine v2 - Career-Specific Fine-Tuned Prompts
Features:
- 3-decision ranking system with explainable AI
- Career-specific prompt engineering
- Market context integration (2024-2026)
- Personalized reasoning generation
- Confidence level assessment
- Fallback mechanisms
"""
import json
import requests
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class CareerLLMEngine:
    """Enhanced LLM engine with career-specific prompts"""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "gpt-oss:20b-cloud",
        temperature: float = 0.5,
        timeout: int = 200
    ):
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.timeout = timeout

    def _check_ollama_running(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def chat(self, messages: List[Dict[str, str]], max_retries: int = 2) -> str:
        """Call Ollama chat endpoint"""
        if not self._check_ollama_running():
            raise RuntimeError(f"Ollama not running at {self.base_url}")
        
        url = f"{self.base_url}/api/chat"
        
        for attempt in range(max_retries + 1):
            try:
                response = requests.post(
                    url,
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": self.temperature,
                        "stream": False
                    },
                    timeout=self.timeout
                )
                response.raise_for_status()
                result = response.json()
                return result.get("message", {}).get("content", "")
            except Exception as e:
                if attempt == max_retries:
                    raise RuntimeError(f"Ollama request failed: {e}")

    def generate_3_decisions_explanation(
        self,
        top_3_careers: List[Dict[str, Any]],
        user_profile: Dict[str, Any],
        internet_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate detailed explanations for 3 ranked career decisions.
        Fine-tuned for career recommendations with explainable AI.
        
        Args:
            top_3_careers: List of 3 career decisions with scores and metadata
            user_profile: User's education, skills, interests, preferences
            internet_data: Market data from web fetcher
        
        Returns:
            Dict with explanations for each decision and comparative analysis
        """
        system_prompt = """You are an elite career advisor specializing in personalized career matching.
You excel at:
1. Explaining WHY a career fits a specific person (not generic reasons)
2. Integrating market data into realistic career paths
3. Identifying concrete skill development needs
4. Providing actionable next steps
5. Being honest about challenges AND opportunities
6. Assessing confidence based on data alignment

IMPORTANT: Always respond with ONLY valid JSON (no markdown, no extra text).
Format exactly as specified."""

        # Build career details string
        career_details = ""
        for i, career in enumerate(top_3_careers[:3], 1):
            career_details += f"\n### CAREER #{i}: {career.get('career_title', 'Unknown')}\n"
            career_details += f"Category: {career.get('category', 'Unknown')}\n"
            career_details += f"Match Score: {career.get('overall_score', 0):.0%}\n"
            career_details += f"Market Growth: {career.get('market_growth_2026', 'Unknown')}\n"
            if career.get('trending_skills'):
                career_details += f"Key Skills: {', '.join(career.get('trending_skills', [])[:4])}\n"
            career_details += f"Salary Range: {career.get('salary_range', 'Unknown')}\n"

        # Build user profile string
        skills_str = ", ".join(user_profile.get('skills', [])[:6])
        interests_str = ", ".join(user_profile.get('interests', [])[:6])
        education = user_profile.get('education', {})
        education_str = f"{education.get('degree', 'Unknown')} in {education.get('field', 'Unknown field')}"
        preferences = user_profile.get('preferences', {})
        timeline = preferences.get('timeline', 'Flexible')
        work_style = ", ".join(preferences.get('preferred_work_style', []))

        user_prompt = f"""Generate career guidance for this person:

PERSON PROFILE:
- Education: {education_str}
- Skills: {skills_str}
- Interests: {interests_str}
- Work Style Preference: {work_style}
- Timeline: {timeline}

TOP 3 CAREER MATCHES:
{career_details}

MARKET CONTEXT (2024-2026):
- AI/ML roles growing 20%+ annually
- Healthcare sector expanding post-pandemic
- Remote work opportunities increasing
- Skills-based hiring replacing degree requirements
- Specialized roles in demand more than generalists

TASK: Provide personalized explanations for why each of these 3 careers specifically fits this person.
Focus on:
1. Their unique skill-interest combination
2. How their education prepares them
3. Market demand in their timeline
4. Specific challenges they'll face
5. Concrete next steps for the next 6 months

JSON FORMAT (REQUIRED - no markdown):
{{
  "decision_1": {{
    "title": "Career Title",
    "confidence": "very_high|high|medium|low",
    "primary_reason": "Why THIS person (not generic) should consider this career",
    "skills_alignment": "How their current skills match",
    "market_context": "Market reality for this career 2024-2026",
    "growth_path": "Timeline to seniority and salary progression",
    "challenges": ["Challenge 1", "Challenge 2", ...],
    "opportunities": ["Opportunity 1", "Opportunity 2", ...],
    "next_steps": ["Action 1", "Action 2", "Action 3"],
    "salary_expectations": "Entry/Mid/Senior level estimates"
  }},
  "decision_2": {{ ... }},
  "decision_3": {{ ... }},
  "comparative_analysis": "Why these 3 rank better than alternatives for this person",
  "personalization_score": "How personalized is this recommendation (1-10)"
}}

CRITICAL: Return ONLY the JSON object. No explanations, no markdown."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            response_text = self.chat(messages, max_retries=2)
            data = json.loads(response_text)
            return data
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM JSON response, using fallback")
            return self._fallback_3_decisions(top_3_careers, user_profile)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}, using fallback")
            return self._fallback_3_decisions(top_3_careers, user_profile)

    def generate_career_explanation(
        self,
        career_title: str,
        user_skills: List[str],
        user_interests: List[str],
        market_data: Dict[str, Any] = None
    ) -> str:
        """Generate explanation for a single career"""
        system_prompt = """You are a career advisor explaining a specific career path.
Provide 2-3 concise, personalized paragraphs explaining why this career matches the person's profile.
Be specific about market demand, required skills, and growth potential.
No JSON needed - just plain text explanation."""

        user_prompt = f"""Explain this career for this person:

Career: {career_title}
Skills: {', '.join(user_skills[:6])}
Interests: {', '.join(user_interests[:6])}

Provide personalized explanation (2-3 paragraphs). Be specific, not generic."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            return self.chat(messages, max_retries=1)
        except Exception as e:
            logger.error(f"Failed to generate explanation: {e}")
            return f"Excellent match in the {career_title} field based on your profile."

    def _fallback_3_decisions(
        self,
        careers: List[Dict[str, Any]],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback when LLM is unavailable"""
        fallback = {
            "decision_1": {
                "title": careers[0].get('career_title', 'Top Career') if careers else "Career 1",
                "confidence": "high",
                "primary_reason": f"Strong match combining your skills in {', '.join(user_profile.get('skills', [])[:2])} with interests in {careers[0].get('category', 'the field') if careers else 'your field of interest'}",
                "skills_alignment": "Your core skills directly map to required competencies",
                "market_context": f"{careers[0].get('market_growth_2026', 'Growing market')} with steady demand",
                "growth_path": "2-3 years to mid-level, 5-7 years to senior position",
                "challenges": ["Continuous learning required", "Competitive field"],
                "opportunities": ["Clear progression path", "Emerging specializations"],
                "next_steps": ["1. Take advanced courses", "2. Build portfolio", "3. Network with professionals"],
                "salary_expectations": f"Entry: {careers[0].get('salary_range', '$40-60K')} annually"
            },
            "decision_2": {
                "title": careers[1].get('career_title', 'Strong Alternative') if len(careers) > 1 else "Alternative Career",
                "confidence": "high",
                "primary_reason": "Good fit with growth potential aligned to your interests",
                "skills_alignment": "Most of your skills transfer with some additional training",
                "market_context": "Stable growth with consistent opportunities",
                "growth_path": "3-4 years to mid-level professional",
                "challenges": ["Requires additional certification", "Competitive entry"],
                "opportunities": ["Work-life balance", "Remote options"],
                "next_steps": ["1. Research companies", "2. Identify certifications", "3. Plan learning path"],
                "salary_expectations": "Competitive with industry averages"
            },
            "decision_3": {
                "title": careers[2].get('career_title', 'Growth Opportunity') if len(careers) > 2 else "Emerging Path",
                "confidence": "medium",
                "primary_reason": "Unique opportunity leveraging your diverse skill set",
                "skills_alignment": "Combination of your skills opens non-traditional path",
                "market_context": "Emerging field with growing demand",
                "growth_path": "4-5 years to establish yourself",
                "challenges": ["Less structured path", "Emerging field clarity"],
                "opportunities": ["Innovation potential", "Early mover advantage"],
                "next_steps": ["1. Explore opportunities", "2. Find mentors", "3. Take projects"],
                "salary_expectations": "High potential as field matures"
            },
            "comparative_analysis": "These three careers offer different value propositions matching your profile at different risk-reward levels",
            "personalization_score": "8"
        }
        return fallback
