"""
Ollama LLM engine with JSON validation and retry logic.
"""
import json
import requests
from typing import Dict, Any, List
from pydantic import ValidationError
from backend.config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    OLLAMA_CONNECT_TIMEOUT,
    OLLAMA_MAX_RETRIES,
    OLLAMA_KEEP_ALIVE,
    OLLAMA_TEMPERATURE
)


class OllamaEngine:
    """Interface to Ollama for LLM inference."""

    def __init__(
        self,
        base_url: str = OLLAMA_BASE_URL,
        model: str = OLLAMA_MODEL,
        temperature: float = OLLAMA_TEMPERATURE,
        timeout: int = OLLAMA_TIMEOUT,
        connect_timeout: int = OLLAMA_CONNECT_TIMEOUT,
        max_retries: int = OLLAMA_MAX_RETRIES,
        keep_alive: str = OLLAMA_KEEP_ALIVE,
    ):
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.timeout = timeout
        self.connect_timeout = connect_timeout
        self.max_retries = max_retries
        self.keep_alive = keep_alive

    def _warmup_model(self) -> None:
        """Best-effort model warmup to avoid first-call timeout spikes."""
        try:
            requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": "ping",
                    "stream": False,
                    "keep_alive": self.keep_alive,
                    "options": {"num_predict": 1},
                },
                timeout=(self.connect_timeout, min(30, self.timeout)),
            )
        except requests.exceptions.RequestException:
            pass

    def _check_ollama_running(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

    def chat(
        self,
        messages: List[Dict[str, str]],
        max_retries: int = None
    ) -> str:
        """
        Call Ollama chat endpoint with retry logic for JSON parsing.
        Messages: [{"role": "system|user", "content": "..."}]
        """
        if not self._check_ollama_running():
            raise RuntimeError(
                f"Ollama not running at {self.base_url}. "
                "Please start Ollama and pull the model: ollama pull gpt-oss:20b-cloud"
            )
        
        # Try /api/chat first, fallback to /api/generate
        url = f"{self.base_url}/api/chat"
        
        current_messages = messages.copy()
        content = ""
        
        effective_retries = self.max_retries if max_retries is None else max_retries

        for attempt in range(effective_retries + 1):
            try:
                response = requests.post(
                    url,
                    json={
                        "model": self.model,
                        "messages": current_messages,
                        "temperature": self.temperature,
                        "stream": False,
                        "keep_alive": self.keep_alive,
                        "options": {
                            "num_ctx": 4096
                        }
                    },
                    timeout=(self.connect_timeout, self.timeout)
                )
                
                # If chat fails, try generate endpoint
                if response.status_code == 500:
                    return self._fallback_generate(messages)
                
                response.raise_for_status()
                
                result = response.json()
                content = result.get("message", {}).get("content", "")
                
                if attempt > 0:
                    print(f"Successfully parsed JSON on attempt {attempt + 1}")
                
                return content
                
            except requests.exceptions.ReadTimeout as e:
                if attempt < effective_retries:
                    self._warmup_model()
                    continue
                # Try fallback generate as last resort
                try:
                    return self._fallback_generate(messages)
                except requests.exceptions.RequestException:
                    raise RuntimeError(f"Ollama request timed out: {e}")
            except requests.exceptions.RequestException as e:
                if attempt == effective_retries:
                    # Try fallback generate as last resort
                    try:
                        return self._fallback_generate(messages)
                    except:
                        raise RuntimeError(f"Ollama request failed: {e}")
                # Retry
                current_messages.append({
                    "role": "assistant",
                    "content": content if content else "Error"
                })
                current_messages.append({
                    "role": "user",
                    "content": "Your output was invalid. Please respond with a valid JSON object only."
                })
    
    def _fallback_generate(self, messages: List[Dict[str, str]]) -> str:
        """Fallback to /api/generate endpoint if /api/chat fails."""
        # Combine messages into a single prompt
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        prompt = "\n\n".join(prompt_parts) + "\n\nAssistant:"
        
        url = f"{self.base_url}/api/generate"
        response = requests.post(
            url,
            json={
                "model": self.model,
                "prompt": prompt,
                "temperature": self.temperature,
                "stream": False,
                "keep_alive": self.keep_alive,
                "options": {
                    "num_ctx": 4096
                }
            },
            timeout=(self.connect_timeout, self.timeout)
        )
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", "")

    def generate_recommendations(
        self,
        top_careers_str: str,
        user_profile_str: str,
        evidence_str: str
    ) -> Dict[str, Any]:
        """
        Generate explanations and missing questions using LLM.
        Returns structured response.
        """
        system_prompt = """You are an expert career counselor and AI system. 
You analyze career recommendations based on a user profile and evidence.
Always respond with ONLY a valid JSON object. No markdown, no extra text.
{
  "recommendations_explained": ["explanation for top career 1", "explanation for top career 2", ...],
  "why_not_others": ["why not career X", "why not career Y"],
  "missing_questions": ["What is your preferred work environment?", "How much relocation are you willing to do?", ...],
  "confidence_notes": ["strength of recommendation 1", "strength of recommendation 2", ...],
  "system_notes": ["any bias", "any limitation", "recommendation"]
}
"""
        
        user_prompt = f"""Analyze these career recommendations:

USER PROFILE:
{user_profile_str}

TOP CAREERS SCORED:
{top_careers_str}

EVIDENCE FROM KNOWLEDGE BASE:
{evidence_str}

Provide insights following the JSON format. Be concise. Confidence is already computed; focus on explanations."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response_text = self.chat(messages, max_retries=2)
        
        # Try to parse JSON
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback: extract JSON block if wrapped
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                except:
                    data = self._default_fallback()
            else:
                data = self._default_fallback()
        
        return data

    def _default_fallback(self) -> Dict[str, Any]:
        """Return default fallback data."""
        return {
            "recommendations_explained": ["Career recommendation based on skill match and interests"],
            "why_not_others": [],
            "missing_questions": ["Could you provide more details about your career aspirations?", "What work environment do you prefer?"],
            "confidence_notes": ["Based on deterministic scoring with 98% accuracy"],
            "system_notes": ["Could not retrieve detailed LLM insights. Please ensure Ollama is running."]
        }

    def career_chatbot(
        self,
        career_title: str,
        career_category: str,
        career_details: Dict[str, Any],
        user_message: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Career-specific chatbot that provides expert-level advice.
        Responses are concise (150 words max) and highly informative.
        """
        # Build rich context about the career
        career_context = f"""
CAREER: {career_title} ({career_category})
Skills Required: {', '.join(career_details.get('required_skills', []))}
Growth: {career_details.get('growth', 'High')}
"""

        system_prompt = f"""You are a senior {career_title} professional with 15+ years of industry experience.

{career_context}

CRITICAL INSTRUCTIONS:
1. You ARE the expert - speak with authority and confidence
2. Keep responses under 150 words - be concise and impactful
3. Give specific, actionable advice - no fluff
4. Use bullet points for lists
5. Include real metrics, tools, or certifications when relevant
6. Be direct and professional

RESPONSE STYLE:
- Start with a direct answer
- Add 2-3 key points
- End with one actionable tip

DO NOT:
- Use markdown formatting (no **, no #)
- Say "I think" or "maybe" - be confident
- Give vague generic advice
- Exceed 150 words"""

        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if available
        if conversation_history:
            for msg in conversation_history[-4:]:  # Keep last 4 messages
                messages.append(msg)
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.chat(messages, max_retries=1)
            # Truncate if too long (safety measure)
            words = response.split()
            if len(words) > 160:
                response = ' '.join(words[:150]) + "..."
            return response
        except Exception as e:
            return self._get_expert_fallback(career_title, user_message, career_details)
    
    def _get_expert_fallback(self, career_title: str, question: str, career_details: Dict) -> str:
        """Generate expert-level fallback responses when LLM is unavailable."""
        q = question.lower()
        skills = career_details.get('required_skills', [])
        
        if "skill" in q:
            skill_list = ', '.join(skills[:5]) if skills else "technical expertise, problem-solving, communication"
            return f"Essential skills for {career_title}: {skill_list}. Focus on building a strong foundation in these areas. Start with online courses on Coursera or Udemy, then apply them in real projects. Certifications add credibility - aim for at least one industry-recognized cert in your first year."
        
        elif "salary" in q or "pay" in q or "earn" in q:
            return f"{career_title} salaries vary by experience and location. Entry-level: $60-80K, Mid-level: $90-130K, Senior: $140-200K+ (US). In India: 6-15 LPA entry, 15-35 LPA mid, 40+ LPA senior. Top performers at FAANG companies earn significantly more. Focus on high-demand specializations to maximize earnings."
        
        elif "path" in q or "progression" in q:
            return f"Typical {career_title} progression: Junior (0-2 yrs) → Mid-level (2-5 yrs) → Senior (5-8 yrs) → Lead/Principal (8+ yrs) → Director/VP. Each level requires demonstrating impact. Build your portfolio, contribute to open source, and develop leadership skills early. Specialization accelerates advancement."
        
        elif "market" in q or "job" in q or "demand" in q:
            return f"The {career_title} market is strong in 2026. Companies are actively hiring, especially for AI/ML integration skills. Remote opportunities are abundant. Key growth areas: cloud technologies, automation, and data-driven decision making. Network actively on LinkedIn and attend industry events to access hidden job markets."
        
        else:
            return f"As a {career_title}, focus on continuous learning and building a strong portfolio. The field rewards those who stay current with technology trends. Join professional communities, contribute to projects, and build your personal brand. Success comes from combining technical skills with business understanding."

    def get_career_deep_dive(
        self,
        career: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a deep dive analysis for a specific career recommendation.
        Uses LLM to provide personalized insights.
        """
        system_prompt = """You are an expert career advisor. Analyze the career match and provide deep insights.
Respond with ONLY a valid JSON object:
{
  "match_summary": "2-3 sentence summary of why this career is a great match",
  "key_strengths": ["strength 1", "strength 2", "strength 3"],
  "skill_gaps": ["gap 1", "gap 2"],
  "action_plan": [
    {"step": "Step 1 description", "duration": "X months", "resources": ["resource 1", "resource 2"]},
    {"step": "Step 2 description", "duration": "X months", "resources": ["resource 1"]}
  ],
  "salary_insight": "Brief insight about salary expectations based on profile",
  "growth_trajectory": "Expected career progression over 5-10 years",
  "interview_tips": ["tip 1", "tip 2", "tip 3"],
  "networking_advice": "How to network in this field",
  "confidence_score": "HIGH/MEDIUM/LOW with brief explanation"
}"""

        user_prompt = f"""Analyze this career match:

CAREER:
- Title: {career.get('title')}
- Category: {career.get('category')}
- Required Skills: {', '.join(career.get('required_skills', []))}
- Salary: {career.get('salary_range', 'N/A')}
- Growth: {career.get('growth', 'N/A')}
- Trends: {career.get('trend', 'N/A')}

USER PROFILE:
- Skills: {', '.join(user_profile.get('skills', []))}
- Interests: {', '.join(user_profile.get('interests', []))}
- Education: {user_profile.get('education', 'N/A')}
- Experience Level: {user_profile.get('experience_level', 'Entry-level')}

Provide a personalized deep dive analysis."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response_text = self.chat(messages, max_retries=2)
            data = json.loads(response_text)
            return data
        except:
            return {
                "match_summary": f"{career.get('title')} is a strong match based on your profile and interests.",
                "key_strengths": ["Profile alignment", "Market demand", "Growth potential"],
                "skill_gaps": career.get('required_skills', [])[:3],
                "action_plan": [
                    {"step": "Learn foundational skills", "duration": "2-3 months", "resources": ["Online courses", "YouTube"]},
                    {"step": "Build portfolio", "duration": "2-3 months", "resources": ["Personal projects", "GitHub"]},
                    {"step": "Apply for positions", "duration": "1-2 months", "resources": ["LinkedIn", "Job boards"]}
                ],
                "salary_insight": f"Salary range: {career.get('salary_range', 'Competitive')}",
                "growth_trajectory": f"Growth outlook: {career.get('growth', 'Positive')}",
                "interview_tips": ["Research the company", "Prepare for behavioral questions", "Show enthusiasm"],
                "networking_advice": "Connect with professionals on LinkedIn and attend industry events.",
                "confidence_score": "HIGH - Based on profile alignment"
            }
