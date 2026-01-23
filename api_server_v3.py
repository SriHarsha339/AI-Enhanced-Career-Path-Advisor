"""
Advanced FastAPI server with full LLM integration for dynamic career recommendations.
Features:
- Dynamic career matching using Ollama LLM
- Google News RSS feed for career market insights
- Dynamic course recommendations
- Intelligent chatbot with role-based context
"""
import json
import logging
import sys
import asyncio
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import requests
import feedparser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============= Ollama LLM Configuration =============

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:7b-instruct"  # or llama3.2, mistral, etc.
OLLAMA_TIMEOUT = 120

def check_ollama_available() -> bool:
    """Check if Ollama is running and model is available."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def call_ollama(prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
    """Call Ollama LLM with the given prompt."""
    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": messages,
                "temperature": temperature,
                "stream": False,
                "options": {"num_ctx": 4096}
            },
            timeout=OLLAMA_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json().get("message", {}).get("content", "")
        else:
            logger.error(f"Ollama error: {response.status_code}")
            return ""
    except Exception as e:
        logger.error(f"Ollama call failed: {e}")
        return ""

def call_ollama_json(prompt: str, system_prompt: str = "") -> Dict[str, Any]:
    """Call Ollama and parse JSON response."""
    full_system = system_prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON. No markdown, no explanation, just the JSON object."
    
    response = call_ollama(prompt, full_system, temperature=0.3)
    
    # Try to extract JSON from response
    try:
        # Remove markdown code blocks if present
        cleaned = re.sub(r'```json?\s*', '', response)
        cleaned = re.sub(r'```\s*', '', cleaned)
        cleaned = cleaned.strip()
        
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to find JSON object in response
        match = re.search(r'\{[\s\S]*\}', response)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
        return {}

# ============= Initialize FastAPI =============

app = FastAPI(
    title="Career Recommender API - LLM Powered",
    description="AI-powered career recommendation system with dynamic LLM integration",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= Request/Response Schemas =============

class CareerQueryRequest(BaseModel):
    educationLevel: str
    interests: List[str]
    hobbies: List[str] = []
    skills: List[str] = []
    personalityTraits: List[str] = []
    extraInfo: str = ""

class CourseItem(BaseModel):
    name: str
    provider: str
    duration: str
    level: str
    url: Optional[str] = None
    description: str

class LandscapeItem(BaseModel):
    title: str
    salary: str
    demand: str
    description: str
    requiredSkills: List[str] = []
    growthRate: str = "Growing"
    roadmap: List['RoadmapItem'] = []  # Career-specific roadmap

class FeaturedCareer(BaseModel):
    title: str
    alignment: str
    passion: str
    outlook: str
    dayInLife: str = ""
    challenges: str = ""

class RoadmapItem(BaseModel):
    phase: str
    title: str
    duration: str
    details: str
    courses: List[CourseItem] = []
    milestones: List[str] = []

class StructuredData(BaseModel):
    landscape: List[LandscapeItem]
    featured: FeaturedCareer
    roadmap: List[RoadmapItem]
    steps: List[str]
    marketInsights: List[str] = []

class CareerRecommendationResponse(BaseModel):
    queryId: int
    recommendation: str
    structuredData: StructuredData
    llmPowered: bool = True

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None
    selectedRole: Optional[str] = None
    conversationHistory: List[Dict[str, str]] = []

class ChatResponse(BaseModel):
    response: str
    suggestedQuestions: List[str] = []

class NewsItem(BaseModel):
    title: str
    link: str
    source: str
    published: str
    summary: str

class NewsResponse(BaseModel):
    career: str
    articles: List[NewsItem]
    insights: str

# ============= Comprehensive Career Categories =============

CAREER_CATEGORIES = {
    "creative": {
        "keywords": ["art", "design", "painting", "drawing", "illustration", "creative", "music", 
                    "photography", "film", "animation", "sculpture", "crafts", "theater", "dance",
                    "writing", "poetry", "storytelling", "fashion", "interior design", "architecture",
                    "graphic design", "ui", "ux", "visual", "aesthetic", "artistic"],
        "careers": [
            {"title": "Graphic Designer", "salary": "₹4-15 LPA", "demand": "High", "growth": "12%"},
            {"title": "UX/UI Designer", "salary": "₹6-25 LPA", "demand": "Very High", "growth": "18%"},
            {"title": "Animator", "salary": "₹4-18 LPA", "demand": "High", "growth": "15%"},
            {"title": "Art Director", "salary": "₹8-30 LPA", "demand": "Medium", "growth": "8%"},
            {"title": "Fashion Designer", "salary": "₹4-20 LPA", "demand": "Medium", "growth": "6%"},
            {"title": "Interior Designer", "salary": "₹5-18 LPA", "demand": "High", "growth": "10%"},
            {"title": "Photographer", "salary": "₹3-15 LPA", "demand": "Medium", "growth": "5%"},
            {"title": "Film Director", "salary": "₹5-50 LPA", "demand": "Low", "growth": "4%"},
            {"title": "Content Creator", "salary": "₹3-25 LPA", "demand": "Very High", "growth": "25%"},
            {"title": "Game Designer", "salary": "₹6-22 LPA", "demand": "High", "growth": "15%"},
        ]
    },
    "technology": {
        "keywords": ["programming", "coding", "software", "computer", "tech", "technology", "ai",
                    "machine learning", "data", "python", "java", "javascript", "web", "app",
                    "developer", "engineer", "devops", "cloud", "cybersecurity", "blockchain",
                    "iot", "robotics", "automation", "database", "algorithm"],
        "careers": [
            {"title": "Software Developer", "salary": "₹8-30 LPA", "demand": "Very High", "growth": "22%"},
            {"title": "Data Scientist", "salary": "₹10-35 LPA", "demand": "Very High", "growth": "28%"},
            {"title": "AI/ML Engineer", "salary": "₹12-45 LPA", "demand": "Very High", "growth": "35%"},
            {"title": "Full Stack Developer", "salary": "₹8-28 LPA", "demand": "High", "growth": "20%"},
            {"title": "DevOps Engineer", "salary": "₹10-32 LPA", "demand": "Very High", "growth": "25%"},
            {"title": "Cloud Architect", "salary": "₹15-50 LPA", "demand": "Very High", "growth": "30%"},
            {"title": "Cybersecurity Analyst", "salary": "₹8-28 LPA", "demand": "Very High", "growth": "32%"},
            {"title": "Mobile App Developer", "salary": "₹6-25 LPA", "demand": "High", "growth": "18%"},
            {"title": "Blockchain Developer", "salary": "₹10-40 LPA", "demand": "High", "growth": "20%"},
            {"title": "Product Manager (Tech)", "salary": "₹15-45 LPA", "demand": "High", "growth": "15%"},
        ]
    },
    "healthcare": {
        "keywords": ["medicine", "doctor", "health", "healthcare", "nursing", "hospital", "patient",
                    "medical", "pharmacy", "therapy", "psychology", "surgery", "clinical", "diagnosis",
                    "treatment", "wellness", "fitness", "nutrition", "mental health", "dentistry",
                    "veterinary", "biology", "anatomy", "helping people"],
        "careers": [
            {"title": "Doctor (MBBS)", "salary": "₹8-50 LPA", "demand": "Very High", "growth": "12%"},
            {"title": "Surgeon", "salary": "₹15-80 LPA", "demand": "High", "growth": "10%"},
            {"title": "Nurse", "salary": "₹3-10 LPA", "demand": "Very High", "growth": "15%"},
            {"title": "Pharmacist", "salary": "₹4-15 LPA", "demand": "High", "growth": "8%"},
            {"title": "Clinical Psychologist", "salary": "₹5-20 LPA", "demand": "High", "growth": "18%"},
            {"title": "Physical Therapist", "salary": "₹4-15 LPA", "demand": "High", "growth": "14%"},
            {"title": "Dentist", "salary": "₹6-30 LPA", "demand": "High", "growth": "10%"},
            {"title": "Medical Researcher", "salary": "₹6-25 LPA", "demand": "Medium", "growth": "12%"},
            {"title": "Healthcare Administrator", "salary": "₹8-25 LPA", "demand": "High", "growth": "16%"},
            {"title": "Nutritionist", "salary": "₹4-12 LPA", "demand": "High", "growth": "15%"},
        ]
    },
    "business": {
        "keywords": ["business", "management", "entrepreneur", "startup", "mba", "marketing",
                    "sales", "strategy", "consulting", "leadership", "operations", "hr",
                    "human resources", "brand", "commerce", "trade", "retail", "e-commerce"],
        "careers": [
            {"title": "Business Analyst", "salary": "₹6-20 LPA", "demand": "High", "growth": "14%"},
            {"title": "Marketing Manager", "salary": "₹8-25 LPA", "demand": "High", "growth": "12%"},
            {"title": "Management Consultant", "salary": "₹12-40 LPA", "demand": "High", "growth": "10%"},
            {"title": "Entrepreneur", "salary": "Variable", "demand": "High", "growth": "20%"},
            {"title": "HR Manager", "salary": "₹8-22 LPA", "demand": "Medium", "growth": "8%"},
            {"title": "Operations Manager", "salary": "₹10-28 LPA", "demand": "High", "growth": "10%"},
            {"title": "Sales Director", "salary": "₹12-35 LPA", "demand": "High", "growth": "8%"},
            {"title": "Brand Manager", "salary": "₹8-25 LPA", "demand": "Medium", "growth": "10%"},
            {"title": "E-commerce Manager", "salary": "₹8-25 LPA", "demand": "Very High", "growth": "22%"},
            {"title": "Supply Chain Manager", "salary": "₹10-30 LPA", "demand": "High", "growth": "12%"},
        ]
    },
    "finance": {
        "keywords": ["finance", "banking", "investment", "accounting", "money", "stock", "trading",
                    "economics", "financial", "chartered accountant", "ca", "cfa", "audit",
                    "tax", "wealth", "insurance", "fintech", "cryptocurrency"],
        "careers": [
            {"title": "Chartered Accountant", "salary": "₹8-30 LPA", "demand": "High", "growth": "10%"},
            {"title": "Financial Analyst", "salary": "₹6-22 LPA", "demand": "High", "growth": "12%"},
            {"title": "Investment Banker", "salary": "₹15-60 LPA", "demand": "Medium", "growth": "8%"},
            {"title": "Portfolio Manager", "salary": "₹12-45 LPA", "demand": "Medium", "growth": "10%"},
            {"title": "Risk Analyst", "salary": "₹8-25 LPA", "demand": "High", "growth": "15%"},
            {"title": "Tax Consultant", "salary": "₹6-20 LPA", "demand": "High", "growth": "8%"},
            {"title": "Fintech Product Manager", "salary": "₹12-35 LPA", "demand": "Very High", "growth": "25%"},
            {"title": "Actuary", "salary": "₹10-40 LPA", "demand": "Medium", "growth": "12%"},
            {"title": "Wealth Manager", "salary": "₹8-30 LPA", "demand": "Medium", "growth": "10%"},
            {"title": "Credit Analyst", "salary": "₹5-18 LPA", "demand": "Medium", "growth": "8%"},
        ]
    },
    "law": {
        "keywords": ["law", "legal", "lawyer", "advocate", "court", "justice", "litigation",
                    "corporate law", "criminal", "civil", "judge", "paralegal", "legal advisor",
                    "contract", "intellectual property", "patent", "arbitration", "debate"],
        "careers": [
            {"title": "Corporate Lawyer", "salary": "₹8-35 LPA", "demand": "High", "growth": "10%"},
            {"title": "Criminal Lawyer", "salary": "₹5-25 LPA", "demand": "Medium", "growth": "6%"},
            {"title": "IP Lawyer", "salary": "₹10-40 LPA", "demand": "High", "growth": "15%"},
            {"title": "Legal Consultant", "salary": "₹6-22 LPA", "demand": "Medium", "growth": "8%"},
            {"title": "Judge", "salary": "₹10-35 LPA", "demand": "Low", "growth": "3%"},
            {"title": "Paralegal", "salary": "₹3-10 LPA", "demand": "Medium", "growth": "10%"},
            {"title": "Legal Tech Specialist", "salary": "₹8-25 LPA", "demand": "High", "growth": "20%"},
            {"title": "Compliance Officer", "salary": "₹8-25 LPA", "demand": "High", "growth": "12%"},
            {"title": "Contract Manager", "salary": "₹6-20 LPA", "demand": "Medium", "growth": "10%"},
            {"title": "Arbitrator", "salary": "₹10-40 LPA", "demand": "Low", "growth": "5%"},
        ]
    },
    "education": {
        "keywords": ["teaching", "teacher", "professor", "education", "school", "college",
                    "university", "training", "coaching", "tutoring", "curriculum", "learning",
                    "academic", "research", "mentor", "instructor", "edtech"],
        "careers": [
            {"title": "School Teacher", "salary": "₹3-12 LPA", "demand": "Very High", "growth": "8%"},
            {"title": "College Professor", "salary": "₹8-30 LPA", "demand": "Medium", "growth": "6%"},
            {"title": "Education Consultant", "salary": "₹5-18 LPA", "demand": "High", "growth": "12%"},
            {"title": "Curriculum Designer", "salary": "₹6-18 LPA", "demand": "Medium", "growth": "10%"},
            {"title": "EdTech Product Manager", "salary": "₹10-30 LPA", "demand": "Very High", "growth": "25%"},
            {"title": "Corporate Trainer", "salary": "₹6-20 LPA", "demand": "High", "growth": "14%"},
            {"title": "Special Education Teacher", "salary": "₹4-12 LPA", "demand": "High", "growth": "12%"},
            {"title": "Academic Counselor", "salary": "₹4-12 LPA", "demand": "High", "growth": "10%"},
            {"title": "Online Course Creator", "salary": "₹5-25 LPA", "demand": "Very High", "growth": "30%"},
            {"title": "Research Scholar", "salary": "₹4-15 LPA", "demand": "Medium", "growth": "8%"},
        ]
    },
    "engineering": {
        "keywords": ["engineering", "mechanical", "civil", "electrical", "electronics", "chemical",
                    "aerospace", "automobile", "manufacturing", "construction", "structural",
                    "industrial", "production", "power", "energy", "renewable"],
        "careers": [
            {"title": "Mechanical Engineer", "salary": "₹5-20 LPA", "demand": "High", "growth": "8%"},
            {"title": "Civil Engineer", "salary": "₹5-18 LPA", "demand": "High", "growth": "10%"},
            {"title": "Electrical Engineer", "salary": "₹5-18 LPA", "demand": "High", "growth": "10%"},
            {"title": "Aerospace Engineer", "salary": "₹8-30 LPA", "demand": "Medium", "growth": "12%"},
            {"title": "Renewable Energy Engineer", "salary": "₹6-22 LPA", "demand": "Very High", "growth": "25%"},
            {"title": "Robotics Engineer", "salary": "₹8-28 LPA", "demand": "High", "growth": "20%"},
            {"title": "Industrial Engineer", "salary": "₹5-18 LPA", "demand": "Medium", "growth": "8%"},
            {"title": "Project Manager (Engineering)", "salary": "₹10-30 LPA", "demand": "High", "growth": "12%"},
            {"title": "Quality Engineer", "salary": "₹5-15 LPA", "demand": "High", "growth": "8%"},
            {"title": "Automotive Engineer", "salary": "₹6-22 LPA", "demand": "High", "growth": "15%"},
        ]
    },
    "science": {
        "keywords": ["science", "research", "physics", "chemistry", "biology", "laboratory",
                    "experiment", "scientist", "discovery", "innovation", "space", "astronomy",
                    "genetics", "biotechnology", "environmental", "marine", "geology"],
        "careers": [
            {"title": "Research Scientist", "salary": "₹6-25 LPA", "demand": "Medium", "growth": "10%"},
            {"title": "Biotechnologist", "salary": "₹5-20 LPA", "demand": "High", "growth": "15%"},
            {"title": "Environmental Scientist", "salary": "₹5-18 LPA", "demand": "High", "growth": "18%"},
            {"title": "Astrophysicist", "salary": "₹8-30 LPA", "demand": "Low", "growth": "8%"},
            {"title": "Geneticist", "salary": "₹8-28 LPA", "demand": "High", "growth": "20%"},
            {"title": "Marine Biologist", "salary": "₹5-15 LPA", "demand": "Low", "growth": "8%"},
            {"title": "Chemist", "salary": "₹5-18 LPA", "demand": "Medium", "growth": "6%"},
            {"title": "Lab Manager", "salary": "₹6-18 LPA", "demand": "Medium", "growth": "8%"},
            {"title": "Science Communicator", "salary": "₹4-15 LPA", "demand": "Medium", "growth": "12%"},
            {"title": "R&D Manager", "salary": "₹12-35 LPA", "demand": "Medium", "growth": "10%"},
        ]
    },
    "media": {
        "keywords": ["media", "journalism", "news", "reporter", "broadcasting", "television",
                    "radio", "podcast", "social media", "influencer", "vlogger", "blogger",
                    "public relations", "pr", "communications", "advertising", "copywriting"],
        "careers": [
            {"title": "Journalist", "salary": "₹4-15 LPA", "demand": "Medium", "growth": "5%"},
            {"title": "Content Strategist", "salary": "₹6-22 LPA", "demand": "High", "growth": "18%"},
            {"title": "Social Media Manager", "salary": "₹4-18 LPA", "demand": "Very High", "growth": "22%"},
            {"title": "PR Manager", "salary": "₹6-22 LPA", "demand": "Medium", "growth": "8%"},
            {"title": "Copywriter", "salary": "₹4-15 LPA", "demand": "High", "growth": "12%"},
            {"title": "Video Producer", "salary": "₹5-20 LPA", "demand": "High", "growth": "15%"},
            {"title": "Podcast Host", "salary": "₹3-20 LPA", "demand": "High", "growth": "25%"},
            {"title": "Digital Marketing Manager", "salary": "₹6-25 LPA", "demand": "Very High", "growth": "20%"},
            {"title": "Brand Strategist", "salary": "₹8-25 LPA", "demand": "Medium", "growth": "12%"},
            {"title": "Media Planner", "salary": "₹5-18 LPA", "demand": "Medium", "growth": "10%"},
        ]
    }
}

# ============= Dynamic Career Matching with LLM =============

async def get_careers_from_llm(request: CareerQueryRequest) -> List[Dict]:
    """
    Use LLM to dynamically find relevant careers based on user inputs.
    This replaces static category matching with intelligent, context-aware career discovery.
    """
    interests_str = ", ".join(request.interests) if request.interests else "general"
    skills_str = ", ".join(request.skills) if request.skills else "not specified"
    hobbies_str = ", ".join(request.hobbies) if request.hobbies else "not specified"
    personality_str = ", ".join(request.personalityTraits) if request.personalityTraits else "not specified"
    
    system_prompt = """You are an expert career counselor with comprehensive knowledge of careers worldwide, including the Indian job market.
Your task is to recommend careers that DIRECTLY match the user's interests, skills, and hobbies.
Be VERY specific - if someone mentions farming, agriculture, or organic, recommend ONLY agriculture-related careers.
If someone mentions technology, recommend ONLY tech careers.
NEVER recommend unrelated careers. The career MUST be a logical fit for their stated interests."""

    prompt = f"""Based on this person's profile, recommend exactly 5 careers that DIRECTLY match their interests.

PROFILE:
- Education Level: {request.educationLevel}
- Interests: {interests_str}
- Skills: {skills_str}
- Hobbies: {hobbies_str}
- Personality Traits: {personality_str}
- Additional Info: {request.extraInfo if request.extraInfo else "None"}

IMPORTANT RULES:
1. Careers MUST directly relate to their stated interests (e.g., farming interest = farming careers)
2. Do NOT suggest unrelated careers like "Content Creator" for someone interested in agriculture
3. Include salary ranges in Indian Rupees (LPA = Lakhs Per Annum)
4. Include realistic growth percentages for the Indian market

Respond ONLY with a valid JSON array (no markdown, no explanation):
[
    {{
        "title": "Career Title (specific to their interests)",
        "salary": "₹X-Y LPA",
        "demand": "Very High/High/Medium/Low",
        "growth": "X%",
        "category": "primary field of this career"
    }},
    ... (exactly 5 careers)
]"""

    if check_ollama_available():
        try:
            llm_response = call_ollama(prompt, system_prompt, temperature=0.3)
            # Clean and parse JSON
            cleaned = re.sub(r'```json?\s*', '', llm_response)
            cleaned = re.sub(r'```\s*', '', cleaned)
            match = re.search(r'\[[\s\S]*\]', cleaned)
            if match:
                careers = json.loads(match.group())
                if isinstance(careers, list) and len(careers) > 0:
                    logger.info(f"LLM returned careers: {[c.get('title') for c in careers]}")
                    return careers[:5]
        except Exception as e:
            logger.error(f"LLM career matching error: {e}")
    
    # Fallback: Try to intelligently match from static categories based on keywords
    return await fallback_career_match(request)


async def fallback_career_match(request: CareerQueryRequest) -> List[Dict]:
    """Fallback career matching when LLM is unavailable. Uses expanded keyword matching."""
    all_inputs = " ".join([
        *request.interests, 
        *request.skills, 
        *request.hobbies
    ]).lower()
    
    # Expanded keyword mappings for common fields not in static categories
    expanded_careers = {
        "agriculture": [
            {"title": "Agricultural Scientist", "salary": "₹5-18 LPA", "demand": "High", "growth": "12%", "category": "agriculture"},
            {"title": "Organic Farm Manager", "salary": "₹4-15 LPA", "demand": "High", "growth": "18%", "category": "agriculture"},
            {"title": "Agronomist", "salary": "₹5-20 LPA", "demand": "High", "growth": "15%", "category": "agriculture"},
            {"title": "Agricultural Consultant", "salary": "₹6-22 LPA", "demand": "Medium", "growth": "14%", "category": "agriculture"},
            {"title": "Horticulturist", "salary": "₹4-15 LPA", "demand": "Medium", "growth": "10%", "category": "agriculture"},
        ],
        "farming": [
            {"title": "Organic Farmer", "salary": "₹3-20 LPA", "demand": "Very High", "growth": "20%", "category": "agriculture"},
            {"title": "Precision Agriculture Specialist", "salary": "₹6-25 LPA", "demand": "High", "growth": "25%", "category": "agriculture"},
            {"title": "Agricultural Extension Officer", "salary": "₹4-12 LPA", "demand": "High", "growth": "10%", "category": "agriculture"},
            {"title": "Crop Specialist", "salary": "₹5-18 LPA", "demand": "High", "growth": "12%", "category": "agriculture"},
            {"title": "Farm Manager", "salary": "₹4-16 LPA", "demand": "High", "growth": "15%", "category": "agriculture"},
        ],
        "organic": [
            {"title": "Organic Certification Specialist", "salary": "₹5-15 LPA", "demand": "High", "growth": "22%", "category": "agriculture"},
            {"title": "Sustainable Agriculture Expert", "salary": "₹6-20 LPA", "demand": "Very High", "growth": "25%", "category": "agriculture"},
            {"title": "Organic Food Business Owner", "salary": "₹5-30 LPA", "demand": "High", "growth": "28%", "category": "agriculture"},
            {"title": "Organic Farming Consultant", "salary": "₹5-18 LPA", "demand": "High", "growth": "20%", "category": "agriculture"},
            {"title": "Permaculture Designer", "salary": "₹4-15 LPA", "demand": "Medium", "growth": "18%", "category": "agriculture"},
        ],
        "sports": [
            {"title": "Sports Coach", "salary": "₹4-20 LPA", "demand": "High", "growth": "15%", "category": "sports"},
            {"title": "Sports Physiotherapist", "salary": "₹5-18 LPA", "demand": "High", "growth": "18%", "category": "sports"},
            {"title": "Sports Manager", "salary": "₹6-25 LPA", "demand": "Medium", "growth": "12%", "category": "sports"},
            {"title": "Fitness Trainer", "salary": "₹3-15 LPA", "demand": "Very High", "growth": "20%", "category": "sports"},
            {"title": "Sports Nutritionist", "salary": "₹5-18 LPA", "demand": "High", "growth": "16%", "category": "sports"},
        ],
        "music": [
            {"title": "Music Producer", "salary": "₹4-25 LPA", "demand": "Medium", "growth": "15%", "category": "arts"},
            {"title": "Music Teacher", "salary": "₹3-12 LPA", "demand": "High", "growth": "10%", "category": "arts"},
            {"title": "Sound Engineer", "salary": "₹4-18 LPA", "demand": "Medium", "growth": "12%", "category": "arts"},
            {"title": "Session Musician", "salary": "₹3-20 LPA", "demand": "Medium", "growth": "8%", "category": "arts"},
            {"title": "Music Therapist", "salary": "₹4-15 LPA", "demand": "High", "growth": "18%", "category": "arts"},
        ],
        "cooking": [
            {"title": "Executive Chef", "salary": "₹5-25 LPA", "demand": "High", "growth": "12%", "category": "culinary"},
            {"title": "Food Entrepreneur", "salary": "₹4-30 LPA", "demand": "Very High", "growth": "22%", "category": "culinary"},
            {"title": "Culinary Instructor", "salary": "₹4-15 LPA", "demand": "Medium", "growth": "10%", "category": "culinary"},
            {"title": "Food Scientist", "salary": "₹5-18 LPA", "demand": "High", "growth": "15%", "category": "culinary"},
            {"title": "Restaurant Manager", "salary": "₹4-18 LPA", "demand": "High", "growth": "12%", "category": "culinary"},
        ],
        "travel": [
            {"title": "Travel Blogger", "salary": "₹3-20 LPA", "demand": "High", "growth": "25%", "category": "travel"},
            {"title": "Tourism Manager", "salary": "₹5-18 LPA", "demand": "High", "growth": "15%", "category": "travel"},
            {"title": "Travel Consultant", "salary": "₹4-15 LPA", "demand": "High", "growth": "12%", "category": "travel"},
            {"title": "Tour Guide", "salary": "₹3-12 LPA", "demand": "High", "growth": "18%", "category": "travel"},
            {"title": "Hotel Manager", "salary": "₹5-22 LPA", "demand": "High", "growth": "14%", "category": "travel"},
        ],
    }
    
    # Check for expanded keywords first
    for keyword, careers in expanded_careers.items():
        if keyword in all_inputs:
            logger.info(f"Fallback matched keyword: {keyword}")
            return careers
    
    # Then try static categories
    categories = match_categories_static(request.interests, request.skills, request.hobbies)
    return get_careers_for_categories_static(categories, limit=5)


def match_categories_static(interests: List[str], skills: List[str], hobbies: List[str]) -> List[str]:
    """Static category matching (used as fallback only)."""
    all_inputs = [x.lower() for x in interests + skills + hobbies]
    input_text = " ".join(all_inputs)
    
    category_scores = {}
    
    for category, data in CAREER_CATEGORIES.items():
        score = 0
        for keyword in data["keywords"]:
            if keyword in input_text:
                score += 2
            for inp in all_inputs:
                if keyword in inp or inp in keyword:
                    score += 1
        category_scores[category] = score
    
    sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
    result = [cat for cat, score in sorted_categories[:3] if score > 0]
    
    if not result:
        result = ["business", "technology"]
    
    return result


def get_careers_for_categories_static(categories: List[str], limit: int = 5) -> List[Dict]:
    """Get careers from static categories (fallback only)."""
    careers = []
    seen_titles = set()
    demand_order = {"Very High": 4, "High": 3, "Medium": 2, "Low": 1}
    
    for cat_priority, category in enumerate(categories):
        if category in CAREER_CATEGORIES:
            category_careers = sorted(
                CAREER_CATEGORIES[category]["careers"],
                key=lambda x: (demand_order.get(x.get("demand", "Medium"), 2),
                               float(x.get("growth", "0%").replace("%", ""))),
                reverse=True
            )
            
            for career in category_careers:
                if career["title"] not in seen_titles:
                    careers.append({**career, "category": category, "_priority": cat_priority})
                    seen_titles.add(career["title"])
    
    careers.sort(key=lambda x: (
        x.get("_priority", 99),
        -demand_order.get(x.get("demand", "Medium"), 2),
        -float(x.get("growth", "0%").replace("%", ""))
    ))
    
    for career in careers:
        career.pop("_priority", None)
    
    return careers[:limit]

async def generate_llm_recommendation(request: CareerQueryRequest, matched_careers: List[Dict]) -> Dict:
    """Generate dynamic, personalized recommendation using LLM based on matched careers."""
    
    # Prepare context for LLM
    career_list = ", ".join([c["title"] for c in matched_careers])
    top_career = matched_careers[0]["title"] if matched_careers else "Career Consultant"
    top_category = matched_careers[0].get("category", "general") if matched_careers else "general"
    interests_str = ", ".join(request.interests)
    skills_str = ", ".join(request.skills) if request.skills else "Not specified"
    hobbies_str = ", ".join(request.hobbies) if request.hobbies else "Not specified"
    
    system_prompt = f"""You are an expert career counselor with deep knowledge of the job market.
You are helping someone interested in {top_career} which is in the {top_category} field.
Their interests include: {interests_str}
Provide personalized, actionable career advice that directly relates to their stated interests.
Focus ONLY on {top_career} and related careers in the {top_category} field."""
    
    prompt = f"""Based on this profile, provide a detailed career analysis for {top_career}:

PROFILE:
- Education: {request.educationLevel}
- Interests: {interests_str}
- Skills: {skills_str}
- Hobbies: {hobbies_str}
- Personality: {", ".join(request.personalityTraits) if request.personalityTraits else "Not specified"}
- Additional Info: {request.extraInfo if request.extraInfo else "None"}

RECOMMENDED CAREER: {top_career} (in {top_category} field)
OTHER OPTIONS in {top_category}: {career_list}

Respond with JSON in this exact format (focus ONLY on {top_career} and {top_category} field, NOT unrelated fields):
{{
    "topCareer": "{top_career}",
    "whyThisFits": "Detailed 2-3 sentence explanation of why {top_career} fits this person's interest in {interests_str}",
    "dayInLife": "Brief description of a typical day as a {top_career}",
    "challenges": "Main challenges in {top_career} and how to overcome them",
    "salaryProgression": "Entry-level to senior salary progression for {top_career} in India",
    "requiredSkills": ["skill1", "skill2", "skill3", "skill4", "skill5"],
    "marketOutlook": "Current market demand and future prospects for {top_career}",
    "alternativeCareers": ["alt1", "alt2"]
}}"""
    
    if check_ollama_available():
        llm_response = call_ollama_json(prompt, system_prompt)
        if llm_response:
            return llm_response
    
    # Fallback if LLM unavailable
    top_career = matched_careers[0] if matched_careers else {"title": "Career Consultant", "salary": "₹5-15 LPA"}
    return {
        "topCareer": top_career["title"],
        "whyThisFits": f"Based on your interests in {interests_str}, this career aligns well with your profile and offers strong growth potential in the current market.",
        "dayInLife": f"A typical day involves applying your skills in {interests_str[:2] if len(interests_str) > 2 else interests_str} to solve real-world problems.",
        "challenges": "The main challenge is continuous skill development. Stay updated through courses and networking.",
        "salaryProgression": top_career.get("salary", "₹5-25 LPA"),
        "requiredSkills": ["Communication", "Problem Solving", "Technical Skills", "Teamwork", "Adaptability"],
        "marketOutlook": f"{top_career.get('demand', 'High')} demand with {top_career.get('growth', '10%')} growth expected",
        "alternativeCareers": [c["title"] for c in matched_careers[1:3]]
    }

async def generate_dynamic_courses(career: str, education_level: str) -> List[Dict]:
    """Generate dynamic course recommendations using LLM."""
    
    system_prompt = f"You are an education expert who recommends specific, real courses for becoming a {career}. Focus ONLY on courses relevant to {career}."
    
    prompt = f"""Recommend 6 specific courses for someone wanting to become a {career} with {education_level} education.
The courses must be specifically for {career}, NOT for technology/AI/programming unless {career} requires it.

Respond with JSON array format:
[
    {{
        "name": "Specific Course Name for {career}",
        "provider": "Coursera/Udemy/edX/YouTube/LinkedIn Learning/Skillshare",
        "duration": "X weeks/months",
        "level": "Beginner/Intermediate/Advanced",
        "description": "Brief description of what you'll learn for {career}"
    }}
]

Include a mix of:
1-2 foundational courses for {career}
2-3 core skill courses for {career}
1-2 advanced/specialization courses for {career}"""
    
    if check_ollama_available():
        llm_response = call_ollama(prompt, system_prompt, temperature=0.5)
        try:
            # Try to parse JSON from response
            cleaned = re.sub(r'```json?\s*', '', llm_response)
            cleaned = re.sub(r'```\s*', '', cleaned)
            match = re.search(r'\[[\s\S]*\]', cleaned)
            if match:
                courses = json.loads(match.group())
                return courses[:6]
        except:
            pass
    
    # Fallback courses
    return [
        {"name": f"Introduction to {career}", "provider": "Coursera", "duration": "4 weeks", 
         "level": "Beginner", "description": f"Fundamentals and basics of {career}"},
        {"name": f"{career} Fundamentals", "provider": "Udemy", "duration": "6 weeks",
         "level": "Beginner", "description": "Core concepts and practical skills"},
        {"name": f"Advanced {career} Skills", "provider": "edX", "duration": "8 weeks",
         "level": "Intermediate", "description": "Deep dive into professional skills"},
        {"name": f"{career} Projects & Portfolio", "provider": "LinkedIn Learning", "duration": "4 weeks",
         "level": "Intermediate", "description": "Build real-world projects"},
        {"name": f"{career} Career Masterclass", "provider": "Udemy", "duration": "10 weeks",
         "level": "Advanced", "description": "Expert-level training and career guidance"},
        {"name": f"Industry Trends in {career}", "provider": "YouTube", "duration": "2 weeks",
         "level": "All Levels", "description": "Latest trends and future outlook"},
    ]

# Career-specific phase templates for truly unique roadmaps
CAREER_PHASE_TEMPLATES = {
    "online course creator": {
        "phases": [
            {
                "title": "Foundation: Subject Expertise & Teaching Basics", 
                "focus": "In this foundational phase, you will focus on building deep expertise in your chosen subject area while developing essential teaching skills. Start by identifying your unique knowledge and passion areas that can translate into valuable course content. Study successful online educators in your niche to understand their content strategies, presentation styles, and audience engagement techniques. Complete a teaching fundamentals course to understand how adults learn differently from children, including concepts like active learning, spaced repetition, and practical application. Begin creating sample lesson plans and practice explaining complex topics in simple terms. Document your learning journey as this authentic content will later resonate with your students. Join online communities of course creators to network, learn from their experiences, and understand common pitfalls to avoid.",
                "milestones": ["Choose your niche/subject area", "Complete teaching fundamentals course", "Create sample lesson plans", "Study top creators in your niche"]
            },
            {
                "title": "Content Creation & Production Skills", 
                "focus": "This phase focuses on mastering the technical aspects of video production and content creation. Set up a professional home recording studio within a budget of ₹15-30K, including a quality microphone, proper lighting (ring light or softbox), and a clean background. Learn video editing using software like Adobe Premiere Pro or DaVinci Resolve, understanding concepts like cuts, transitions, audio leveling, and color correction. Create at least 5 practice videos covering different formats such as talking head, screen recording, whiteboard animation, and slide presentations. Share these videos with test viewers to gather honest feedback on your presentation style, audio quality, and content clarity. Work on your on-camera presence, voice modulation, and ability to explain concepts engagingly. Study thumbnail design, video titles, and hooks that capture viewer attention in the first few seconds.",
                "milestones": ["Set up home recording studio (₹15-30K budget)", "Learn video editing (Premiere/DaVinci)", "Create 5 practice videos", "Get feedback from 10+ test viewers"]
            },
            {
                "title": "Platform Mastery & Course Design", 
                "focus": "Learn instructional design principles using the ADDIE model (Analysis, Design, Development, Implementation, Evaluation) to create structured, effective courses. Master course platforms like Udemy, Teachable, Skillshare, or Unacademy, understanding each platform's unique requirements, audience demographics, and revenue sharing models. Complete an instructional design certification to understand learning objectives, assessment design, and curriculum sequencing. Design your course curriculum with clear learning outcomes for each module, ensuring progressive skill building from beginner to advanced levels. Create a comprehensive course outline with 20+ lessons, including intro videos, core content, practice exercises, quizzes, and a capstone project. Develop supplementary materials like downloadable resources, cheat sheets, and community discussion prompts. Plan your pricing strategy considering market research, competitor analysis, and value proposition.",
                "milestones": ["Complete instructional design certification", "Choose platform (Udemy/Teachable/own website)", "Design curriculum with ADDIE model", "Create course outline with 20+ lessons"]
            },
            {
                "title": "Launch & Monetization", 
                "focus": "Execute a strategic course launch to maximize initial enrollment and reviews. Develop a pre-launch marketing strategy including building an email list, creating free preview content, and leveraging social media platforms like YouTube, Instagram, and LinkedIn. Launch your first complete course with all modules, quizzes, and resources in place. Focus on getting your first 100 students through promotional pricing, referral programs, and leveraging your existing network. Actively engage with students to resolve doubts, gather feedback, and encourage course reviews, aiming for a 4.5+ star rating. Optimize your course based on student feedback and completion analytics. Diversify revenue through upsells, course bundles, coaching programs, or corporate training packages. Build systems for continuous content updates, student support, and scaling to multiple courses generating ₹50K+ monthly revenue.",
                "milestones": ["Launch first complete course", "Reach 100 enrolled students", "Achieve 4.5+ star rating", "Generate ₹50K+ monthly revenue"]
            }
        ]
    },
    "edtech product manager": {
        "phases": [
            {
                "title": "Product Management Foundations", 
                "focus": "Build a solid foundation in product management core competencies essential for any PM role. Complete structured programs like Google's Product Management Certificate or Meta's Product Manager course to understand the PM lifecycle from ideation to launch. Master project management and collaboration tools including Jira for agile project tracking, Trello for kanban workflows, and Asana for team coordination. Learn to write comprehensive Product Requirement Documents (PRDs) that clearly communicate product vision, user stories, acceptance criteria, and success metrics to engineering and design teams. Understand agile and scrum frameworks including sprint planning, daily standups, retrospectives, and backlog grooming. Practice prioritization frameworks like RICE (Reach, Impact, Confidence, Effort) and MoSCoW (Must have, Should have, Could have, Won't have) to make data-driven product decisions.",
                "milestones": ["Complete Google/Meta PM certificate", "Master Jira/Trello/Asana", "Learn PRD writing", "Understand agile/scrum frameworks"]
            },
            {
                "title": "EdTech Domain Expertise", 
                "focus": "Develop deep expertise in the education technology landscape, particularly in the Indian context. Study the National Education Policy (NEP) 2020 to understand its implications for digital learning, skill development, and technology adoption in education. Analyze the top 10 Indian edtech applications including BYJU'S, Unacademy, Vedantu, upGrad, and others to understand their product strategies, user experience patterns, and business models. Learn about learning science concepts including cognitive load theory, spaced repetition, gamification, and personalized learning pathways. Understand learning analytics and how data can be used to improve student outcomes, identify at-risk learners, and optimize content delivery. Network with at least 20 edtech professionals through LinkedIn, industry events, and online communities to build relationships and gain insider perspectives on industry challenges and opportunities.",
                "milestones": ["Study NEP 2020 implications", "Analyze top 10 Indian edtech apps", "Understand learning analytics", "Network with 20+ edtech professionals"]
            },
            {
                "title": "Technical & Analytics Skills", 
                "focus": "Develop technical literacy to communicate effectively with engineering teams and make data-driven product decisions. Learn SQL basics to query databases independently, extract user behavior data, and create custom reports without relying entirely on data teams. Master product analytics platforms like Mixpanel, Amplitude, or Google Analytics to track user journeys, funnel conversions, feature adoption, and retention metrics. Understand API basics and system architecture to evaluate technical feasibility, estimate development efforts, and participate meaningfully in technical discussions. Complete A/B testing and experimentation courses to design statistically valid experiments, interpret results correctly, and make confident product decisions. Learn to create dashboards and reports that communicate insights effectively to stakeholders at various levels.",
                "milestones": ["Learn SQL basics", "Master product analytics (Mixpanel/Amplitude)", "Understand API basics", "Complete A/B testing course"]
            },
            {
                "title": "EdTech PM Specialization", 
                "focus": "Gain hands-on experience specifically in edtech product management through internships and real-world project work. Secure an internship at an edtech company, whether a startup or established player, to experience the unique challenges of building educational products. Ship at least 2 product features from concept to launch, experiencing the full PM lifecycle including user research, requirement gathering, design collaboration, engineering coordination, and launch management. Document your work as case studies that demonstrate your problem-solving approach, user-centricity, and measurable impact on product metrics. Build a portfolio website showcasing your edtech PM projects, product thinking, and domain expertise. Prepare for PM interviews with edtech-specific case studies, product critiques, and market analysis to land an Associate PM role at a leading edtech company.",
                "milestones": ["Complete internship at edtech company", "Ship 2+ product features", "Build case study portfolio", "Land Associate PM role at edtech"]
            }
        ]
    },
    "school teacher": {
        "phases": [
            {
                "title": "Academic Foundation (Class 11-12)", 
                "focus": "Complete your higher secondary education with careful stream selection aligned to your teaching aspirations. Choose your subject stream based on which subject you want to teach in the future, such as Science for teaching Physics, Chemistry, or Mathematics, Commerce for Business Studies and Accountancy, or Arts for languages, History, or Geography. Focus on scoring at least 60% in board examinations as this is typically the minimum eligibility for B.Ed admission. Start developing teaching skills early by volunteering as a tutor for younger students in your school, neighborhood, or through NGO teaching programs. Research B.Ed college requirements, entrance exams, and admission processes in your state. Observe effective teachers and note what makes their teaching engaging, including their explanation techniques, classroom management, and student interaction patterns. Begin building patience, communication skills, and subject matter depth required for teaching.",
                "milestones": ["Choose teaching subject stream", "Score 60%+ in board exams", "Volunteer as tutor", "Research B.Ed college requirements"]
            },
            {
                "title": "Bachelor's Degree in Subject", 
                "focus": "Complete a 3-year bachelor's degree (BA/BSc/BCom) in the subject you wish to teach to build deep content knowledge. Choose your specialization carefully as B.Ed admission and teaching positions often require a specific subject background. Maintain at least 50% aggregate marks throughout your degree as this is the minimum eligibility requirement for most B.Ed programs. Actively participate in education clubs, teaching initiatives, and academic activities in your college. Take up part-time tutoring for at least 5 students to gain practical teaching experience and understand diverse learning styles. Explore additional certifications or short courses in pedagogy, educational psychology, or technology-enhanced learning. Build relationships with professors who can provide guidance and recommendations for B.Ed applications.",
                "milestones": ["Complete 3-year bachelor's degree", "Maintain 50%+ aggregate (B.Ed eligibility)", "Join education clubs", "Tutor 5+ students part-time"]
            },
            {
                "title": "B.Ed & Teacher Certification", 
                "focus": "Complete the Bachelor of Education (B.Ed) degree, which is mandatory for teaching in recognized schools from Class 6 onwards. Secure admission in a recognized B.Ed college through entrance exams like the state B.Ed CET or university-level tests. The 2-year B.Ed program covers educational psychology, pedagogy, curriculum development, and assessment methods. Complete the mandatory 4-month school internship with dedication, treating it as your first real teaching experience. Practice lesson planning, classroom management, and diverse teaching methodologies. Clear the CTET (Central Teacher Eligibility Test) Paper I for Classes 1-5 or Paper II for Classes 6-8, which is mandatory for central government schools. Also clear your State TET for eligibility in state government schools. Focus on child psychology, inclusive education, and subject-specific pedagogy as these are major exam components.",
                "milestones": ["Get admission in recognized B.Ed college", "Complete 4-month school internship", "Clear CTET Paper I or II", "Clear State TET exam"]
            },
            {
                "title": "Teaching Career Launch", 
                "focus": "Begin your formal teaching career by applying for positions in government and private schools. For government positions, monitor vacancy notifications on state education department websites, apply through proper channels, and prepare for written tests and interviews. Create a comprehensive teaching portfolio including demo teaching videos, lesson plans you've developed, student testimonials from tutoring, and any awards or recognitions. For private schools, approach institutions directly with your resume, portfolio, and CTET/TET scores. Be prepared for demonstration classes as part of the interview process. Complete your probation period successfully by meeting all teaching responsibilities, maintaining student engagement, building relationships with parents and colleagues, and contributing to school activities beyond the classroom.",
                "milestones": ["Apply for government teacher vacancies", "Create teaching portfolio with demo videos", "Get hired at school", "Complete probation period successfully"]
            },
            {
                "title": "Professional Growth & Specialization", 
                "focus": "Invest in continuous professional development to grow from a good teacher to an exceptional educator. Complete at least 3 NCERT or CBSE-organized workshops on updated teaching methodologies, curriculum changes, and assessment reforms. Become a Google Certified Educator or Microsoft Innovative Educator to integrate technology effectively in your classroom. Mentor junior teachers and student-teachers during their internships to develop leadership skills. Consider pursuing M.Ed (Master of Education) if you aspire to principal or educational leadership positions. Stay updated with the latest in educational research, pedagogical innovations, and policy changes. Contribute to curriculum development committees, question paper setting, or textbook review processes if opportunities arise. Build your reputation as a subject matter expert through teacher communities, conferences, and educational publications.",
                "milestones": ["Complete 3+ NCERT/CBSE workshops", "Become Google Certified Educator", "Mentor junior teachers", "Consider M.Ed for principal track"]
            }
        ]
    },
    "corporate trainer": {
        "phases": [
            {
                "title": "Domain Expertise Building", 
                "focus": "Develop deep expertise in a specific corporate domain that will become your training specialization. Identify your training focus area based on your strengths and market demand, whether it's soft skills like communication and leadership, technical training in IT or engineering, sales and marketing excellence, or HR and organizational development. Spend 2-3 years working in your chosen domain to gain practical, credible experience that will make your training authentic and valuable. Complete relevant domain certifications to establish your credentials, such as SHRM for HR, PMP for project management, or relevant technical certifications. Build a reputation as a subject matter expert through presentations, articles, and by being the go-to person for questions in your area. Document case studies, success stories, and lessons learned from your industry experience to use as training content.",
                "milestones": ["Identify training specialization", "Get 2-3 years industry experience", "Complete domain certifications", "Build reputation as subject expert"]
            },
            {
                "title": "Training & Facilitation Skills", 
                "focus": "Master the art and science of corporate training delivery and adult learning facilitation. Complete a recognized Train-the-Trainer (ToT) certification program that covers adult learning principles, training methodologies, and facilitation techniques. Understand andragogy (adult learning theory) and how it differs from pedagogy, including concepts like self-directed learning, experience-based learning, and immediate application needs. Master presentation tools like PowerPoint, Canva, and Prezi to create visually engaging training materials. Practice extensively, aiming for at least 50 hours of training delivery in various settings to develop your unique facilitation style. Get NSDC (National Skill Development Corporation) trainer certification if you plan to work with government skill development programs. Develop skills in managing group dynamics, handling difficult participants, and creating interactive learning experiences.",
                "milestones": ["Complete Train-the-Trainer certification", "Master PowerPoint/Canva for presentations", "Practice with 50+ hours of delivery", "Get NSDC trainer certification"]
            },
            {
                "title": "Instructional Design & Content", 
                "focus": "Learn to design effective, outcome-oriented training programs from scratch. Master instructional design models like ADDIE (Analysis, Design, Development, Implementation, Evaluation) and SAM (Successive Approximation Model) to create structured learning experiences. Understand how to conduct training needs analysis (TNA) to identify skill gaps and design targeted interventions. Create at least 3 complete training modules with participant workbooks, facilitator guides, presentation decks, and assessment tools. Learn to work with Learning Management Systems (LMS) like Moodle, Cornerstone, or SAP SuccessFactors for blended learning delivery and tracking. Build a library of training content including icebreakers, energizers, case studies, role-plays, and simulations that you can adapt for different audiences. Understand how to measure training effectiveness using Kirkpatrick's four levels of evaluation.",
                "milestones": ["Learn ADDIE/SAM design models", "Create 3 complete training modules", "Master LMS platforms (Moodle/Cornerstone)", "Build training content library"]
            },
            {
                "title": "Enterprise Training Delivery", 
                "focus": "Deliver training at the corporate level and establish your reputation as a professional trainer. Accumulate experience training 500+ participants across various companies, levels, and program formats. Aim for consistent feedback ratings of 4.5 out of 5 or higher by continuously refining your delivery based on participant feedback. Pursue professional certifications from global bodies like ATD (Association for Talent Development) or become a Certified Professional in Training Management (CPTM). Build relationships with corporate HR and L&D teams to become a preferred training vendor. Develop expertise in multiple delivery formats including in-person workshops, virtual training (using Zoom, Teams, or Webex), and hybrid programs. Create a strong LinkedIn presence showcasing your training work, participant testimonials, and thought leadership content.",
                "milestones": ["Deliver training to 500+ participants", "Achieve 4.5+ feedback rating", "Get certified by ATD/CPTM", "Build network of corporate clients"]
            },
            {
                "title": "Training Consultancy & Leadership", 
                "focus": "Establish yourself as a training consultant or take on L&D leadership roles in organizations. Choose your path: either start your own training consultancy business or become the L&D Head or Chief Learning Officer at a company. If starting a consultancy, establish your business legally, create service packages, develop a client acquisition strategy, and build a team of associate trainers. Design enterprise-wide training programs that align with business strategy, address skill gaps at scale, and create measurable business impact. Learn to measure and communicate training ROI in business terms that resonate with senior leadership. Target revenue of ₹15 lakhs or more annually through corporate contracts, consulting assignments, and potentially licensing your training content to other trainers or organizations.",
                "milestones": ["Start training consultancy OR become L&D Head", "Design enterprise-wide training programs", "Measure ROI and business impact", "Generate ₹15L+ annual revenue/salary"]
            }
        ]
    },
    "education consultant": {
        "phases": [
            {
                "title": "Education Sector Foundation", 
                "focus": "Build comprehensive understanding of the Indian education system, its policies, and key stakeholders. Study the National Education Policy (NEP) 2020 in depth, understanding its implications for curriculum reform, assessment changes, technology integration, and skill development. Learn the Right to Education (RTE) Act provisions regarding school recognition, student-teacher ratios, and compliance requirements. Understand the differences between various education boards (CBSE, ICSE, State Boards, IB, Cambridge) including their philosophies, curriculum approaches, and assessment patterns. Complete courses on education policy and governance from reputed institutions. Familiarize yourself with regulatory bodies like NCERT, NCTE, UGC, NAAC, and their roles in shaping educational standards. Build foundational knowledge about global education trends and how they apply to the Indian context.",
                "milestones": ["Study NEP 2020 in depth", "Understand RTE Act provisions", "Learn about CBSE/ICSE/State board differences", "Complete education policy course"]
            },
            {
                "title": "Specialized Domain Development", 
                "focus": "Develop deep expertise in a specific education consulting niche based on your interests and market demand. Choose your specialization area: school improvement and accreditation, curriculum design and development, edtech advisory and digital transformation, education policy and research, or career counseling and student guidance. Gain 3+ years of hands-on experience in the education sector through teaching, educational administration, or edtech roles. Pursue higher education in the form of M.Ed (Master of Education) or MA in Education to deepen your theoretical understanding and build credibility. Develop expertise in assessment design, including formative and summative assessments, rubric development, and learning outcome measurement. Build a reputation in your chosen niche through publications, presentations, and professional network contributions.",
                "milestones": ["Choose specialization area", "Get 3+ years education sector experience", "Complete M.Ed or MA Education", "Build expertise in assessment design"]
            },
            {
                "title": "Consulting Skills & Credentials", 
                "focus": "Develop the consulting methodologies, business skills, and professional credentials needed for independent consulting work. Learn structured problem-solving and consulting frameworks similar to those used by McKinsey, BCG, and other top consulting firms. Complete project management certification (PMP or Prince2) to manage complex consulting engagements effectively. Master data analysis techniques for education, including student performance analysis, school data interpretation, and research methodology. Build a professional network of 100+ educators including school principals, education administrators, policy makers, and fellow consultants. Develop proposal writing skills to articulate project scope, methodology, deliverables, and pricing. Learn client relationship management and stakeholder communication skills essential for consulting success.",
                "milestones": ["Learn consulting frameworks (McKinsey style)", "Complete project management certification", "Master data analysis for education", "Build professional network of 100+ educators"]
            },
            {
                "title": "Practice Building & Client Work", 
                "focus": "Start taking consulting projects and establish your reputation in the education ecosystem. Complete at least 5 school consulting projects covering areas like school improvement plans, curriculum audits, teacher professional development, or technology integration strategies. Get registered as a consultant with relevant bodies like CBSE for school affiliation consulting or NAAC for higher education accreditation. Publish at least 2 research papers or articles in education journals or reputable platforms to establish thought leadership. Speak at 3 or more education conferences, seminars, or webinars to build visibility and credibility. Develop case studies from your successful projects to use in marketing and client acquisition. Build relationships with school chains, education trusts, and government education departments for larger consulting opportunities.",
                "milestones": ["Complete 5+ school consulting projects", "Get registered as CBSE/NAAC consultant", "Publish 2+ education research papers", "Speak at 3+ education conferences"]
            },
            {
                "title": "Established Consultancy", 
                "focus": "Scale your consulting practice and become a recognized education expert in your domain. Build a team of 3 or more associate consultants to handle larger projects and diversify service offerings. Expand your client base to 20+ schools or educational institutions with ongoing relationships. Get empanelled with state education departments or central government bodies like MHRD, NCERT, or state SCERTs for policy and implementation projects. Target annual consulting revenue of ₹25 lakhs or more through a mix of project-based work, retainer relationships, and training programs. Consider developing proprietary frameworks, tools, or methodologies that can be licensed to other consultants. Build a sustainable business model with recurring revenue streams rather than relying solely on one-time projects.",
                "milestones": ["Build team of 3+ consultants", "Work with 20+ schools/institutions", "Get empanelled with state education dept", "Generate ₹25L+ annual consulting revenue"]
            }
        ]
    }
}

# Education level to years mapping (Indian education system)
EDUCATION_LEVELS = {
    "10th": {"years_completed": 10, "next_step": "11th & 12th Class", "years_to_degree": 5},
    "10th class": {"years_completed": 10, "next_step": "11th & 12th Class", "years_to_degree": 5},
    "12th": {"years_completed": 12, "next_step": "Bachelor's Degree", "years_to_degree": 3},
    "12th class": {"years_completed": 12, "next_step": "Bachelor's Degree", "years_to_degree": 3},
    "high school": {"years_completed": 12, "next_step": "Bachelor's Degree", "years_to_degree": 3},
    "bachelor": {"years_completed": 15, "next_step": "Skill Building / Master's", "years_to_degree": 0},
    "bachelor's": {"years_completed": 15, "next_step": "Skill Building / Master's", "years_to_degree": 0},
    "undergraduate": {"years_completed": 15, "next_step": "Skill Building / Master's", "years_to_degree": 0},
    "master": {"years_completed": 17, "next_step": "Industry Experience", "years_to_degree": 0},
    "master's": {"years_completed": 17, "next_step": "Industry Experience", "years_to_degree": 0},
    "postgraduate": {"years_completed": 17, "next_step": "Industry Experience", "years_to_degree": 0},
    "phd": {"years_completed": 20, "next_step": "Research / Leadership", "years_to_degree": 0},
    "doctorate": {"years_completed": 20, "next_step": "Research / Leadership", "years_to_degree": 0},
}

def get_education_info(education_level: str) -> Dict:
    """Get education level details."""
    level_lower = education_level.lower().strip()
    for key, info in EDUCATION_LEVELS.items():
        if key in level_lower or level_lower in key:
            return info
    # Default to bachelor's if not found
    return {"years_completed": 15, "next_step": "Skill Building", "years_to_degree": 0}


# Career-specific course and degree recommendations
CAREER_EDUCATION_MAP = {
    "ux/ui designer": {
        "degrees": ["B.Des in Interaction Design", "BFA in Visual Communication", "B.Tech + Design Minor"],
        "streams": ["Arts with Computer Science", "Science with Design electives"],
        "skills": ["Figma", "Adobe XD", "User Research", "Prototyping", "Design Systems"],
        "certifications": ["Google UX Design Certificate", "Nielsen Norman UX Certification", "Interaction Design Foundation"],
        "courses": [
            {"name": "Google UX Design Professional Certificate", "provider": "Coursera", "duration": "6 months", "level": "Beginner", "description": "Complete UX design process from research to prototyping"},
            {"name": "UI/UX Design Specialization", "provider": "CalArts", "duration": "4 months", "level": "Intermediate", "description": "Advanced UI design principles and visual design"},
            {"name": "Figma UI/UX Design Essentials", "provider": "Udemy", "duration": "8 weeks", "level": "Beginner", "description": "Master Figma for professional UI design"},
            {"name": "Design Thinking for Innovation", "provider": "Coursera", "duration": "4 weeks", "level": "Intermediate", "description": "Human-centered design thinking methodology"}
        ]
    },
    "graphic designer": {
        "degrees": ["BFA in Graphic Design", "B.Des in Communication Design", "Bachelor in Visual Arts"],
        "streams": ["Arts/Humanities", "Commerce with Design"],
        "skills": ["Adobe Photoshop", "Illustrator", "InDesign", "Typography", "Brand Design"],
        "certifications": ["Adobe Certified Professional", "Canva Design Certification", "HubSpot Content Marketing"],
        "courses": [
            {"name": "Graphic Design Specialization", "provider": "CalArts via Coursera", "duration": "6 months", "level": "Beginner", "description": "Fundamentals of graphic design and visual communication"},
            {"name": "Adobe Illustrator CC Masterclass", "provider": "Udemy", "duration": "10 weeks", "level": "Beginner", "description": "Vector graphics and illustration techniques"},
            {"name": "Typography Fundamentals", "provider": "Skillshare", "duration": "4 weeks", "level": "Intermediate", "description": "Type design, pairing, and layout principles"},
            {"name": "Brand Identity Design", "provider": "LinkedIn Learning", "duration": "6 weeks", "level": "Intermediate", "description": "Create complete brand identity systems"}
        ]
    },
    "content creator": {
        "degrees": ["BA in Mass Communication", "BMS in Digital Media", "BA in Journalism"],
        "streams": ["Arts/Humanities", "Commerce"],
        "skills": ["Video Editing", "Content Writing", "SEO", "Social Media Marketing", "Storytelling"],
        "certifications": ["HubSpot Content Marketing", "Google Digital Marketing", "YouTube Creator Academy"],
        "courses": [
            {"name": "Content Strategy for Professionals", "provider": "Northwestern via Coursera", "duration": "4 months", "level": "Intermediate", "description": "Strategic content planning and execution"},
            {"name": "Video Editing with Premiere Pro", "provider": "Udemy", "duration": "8 weeks", "level": "Beginner", "description": "Professional video editing techniques"},
            {"name": "SEO Fundamentals", "provider": "Semrush Academy", "duration": "4 weeks", "level": "Beginner", "description": "Search engine optimization basics"},
            {"name": "Social Media Marketing Specialization", "provider": "Coursera", "duration": "6 months", "level": "Beginner", "description": "Build and grow social media presence"}
        ]
    },
    "animator": {
        "degrees": ["BFA in Animation", "B.Des in Animation & VFX", "BSc in Multimedia"],
        "streams": ["Arts with Computer Applications", "Science with Animation electives"],
        "skills": ["2D Animation", "3D Animation", "Maya/Blender", "After Effects", "Character Design"],
        "certifications": ["Autodesk Maya Certified", "Adobe After Effects Certified", "Unity Certified"],
        "courses": [
            {"name": "3D Animation with Blender", "provider": "Udemy", "duration": "12 weeks", "level": "Beginner", "description": "Complete 3D modeling and animation"},
            {"name": "Character Animation Fundamentals", "provider": "AnimationMentor", "duration": "3 months", "level": "Intermediate", "description": "Bring characters to life with motion"},
            {"name": "Motion Graphics with After Effects", "provider": "School of Motion", "duration": "8 weeks", "level": "Intermediate", "description": "Create stunning motion graphics"},
            {"name": "Storyboarding for Animation", "provider": "Skillshare", "duration": "4 weeks", "level": "Beginner", "description": "Visual storytelling and planning"}
        ]
    },
    "game designer": {
        "degrees": ["B.Tech in Game Development", "B.Des in Game Design", "BSc in Computer Science"],
        "streams": ["Science with Computer Science", "Mathematics + Physics"],
        "skills": ["Unity/Unreal Engine", "Game Mechanics", "Level Design", "C#/C++", "3D Modeling"],
        "certifications": ["Unity Certified Developer", "Unreal Engine Certified", "Game Design Document Writing"],
        "courses": [
            {"name": "Game Design & Development Specialization", "provider": "Michigan State via Coursera", "duration": "6 months", "level": "Beginner", "description": "Complete game design fundamentals"},
            {"name": "Complete C# Unity Game Developer", "provider": "Udemy", "duration": "16 weeks", "level": "Beginner", "description": "Build games with Unity and C#"},
            {"name": "Unreal Engine 5 Masterclass", "provider": "Udemy", "duration": "12 weeks", "level": "Intermediate", "description": "AAA game development with Unreal"},
            {"name": "Level Design for Games", "provider": "GDC Vault", "duration": "4 weeks", "level": "Intermediate", "description": "Create engaging game levels"}
        ]
    },
    "data scientist": {
        "degrees": ["B.Tech in Computer Science", "BSc in Statistics", "BE in IT"],
        "streams": ["Science with Mathematics", "Computer Science + Statistics"],
        "skills": ["Python", "Machine Learning", "SQL", "Data Visualization", "Statistics"],
        "certifications": ["IBM Data Science Professional", "Google Data Analytics", "AWS Machine Learning"],
        "courses": [
            {"name": "IBM Data Science Professional Certificate", "provider": "Coursera", "duration": "6 months", "level": "Beginner", "description": "Complete data science workflow"},
            {"name": "Machine Learning by Andrew Ng", "provider": "Coursera", "duration": "3 months", "level": "Intermediate", "description": "ML algorithms and implementation"},
            {"name": "Python for Data Science", "provider": "DataCamp", "duration": "8 weeks", "level": "Beginner", "description": "Python programming for analytics"},
            {"name": "Deep Learning Specialization", "provider": "DeepLearning.AI", "duration": "4 months", "level": "Advanced", "description": "Neural networks and deep learning"}
        ]
    },
    "software developer": {
        "degrees": ["B.Tech in Computer Science", "BCA", "BE in Information Technology"],
        "streams": ["Science with Computer Science", "Mathematics"],
        "skills": ["Programming (Java/Python/JS)", "Data Structures", "System Design", "Git", "APIs"],
        "certifications": ["AWS Developer Associate", "Meta Front-End Developer", "Oracle Java Certified"],
        "courses": [
            {"name": "CS50: Introduction to Computer Science", "provider": "Harvard via edX", "duration": "12 weeks", "level": "Beginner", "description": "Foundational computer science concepts"},
            {"name": "Full Stack Web Development", "provider": "Meta via Coursera", "duration": "8 months", "level": "Beginner", "description": "Frontend and backend development"},
            {"name": "Data Structures and Algorithms", "provider": "Udemy", "duration": "10 weeks", "level": "Intermediate", "description": "Essential DSA for interviews"},
            {"name": "System Design Interview Prep", "provider": "Educative", "duration": "6 weeks", "level": "Advanced", "description": "Design scalable systems"}
        ]
    },
    "product manager": {
        "degrees": ["MBA", "B.Tech + MBA", "BBA in Product Management"],
        "streams": ["Any stream (Commerce/Science preferred)"],
        "skills": ["Product Strategy", "User Research", "Agile/Scrum", "Data Analysis", "Roadmapping"],
        "certifications": ["Google Project Management", "Pragmatic Marketing Certified", "Scrum Product Owner"],
        "courses": [
            {"name": "Digital Product Management", "provider": "University of Virginia via Coursera", "duration": "4 months", "level": "Intermediate", "description": "End-to-end product lifecycle"},
            {"name": "Product Management Fundamentals", "provider": "Udemy", "duration": "6 weeks", "level": "Beginner", "description": "Core PM skills and frameworks"},
            {"name": "Agile with Atlassian Jira", "provider": "Coursera", "duration": "4 weeks", "level": "Beginner", "description": "Agile project management"},
            {"name": "Data-Driven Product Management", "provider": "LinkedIn Learning", "duration": "4 weeks", "level": "Intermediate", "description": "Use data for product decisions"}
        ]
    },
    "online course creator": {
        "degrees": ["BA in Education", "B.Ed", "Any domain expertise degree"],
        "streams": ["Any stream based on teaching subject"],
        "skills": ["Instructional Design", "Video Production", "LMS Platforms", "Public Speaking", "Curriculum Design"],
        "certifications": ["Certified Instructional Designer", "Articulate Storyline Certified", "Teachable Creator"],
        "courses": [
            {"name": "Instructional Design MasterTrack", "provider": "University of Illinois via Coursera", "duration": "4 months", "level": "Intermediate", "description": "Design effective learning experiences"},
            {"name": "Create Engaging Online Courses", "provider": "Udemy", "duration": "6 weeks", "level": "Beginner", "description": "Build and launch online courses"},
            {"name": "Video Production for eLearning", "provider": "LinkedIn Learning", "duration": "4 weeks", "level": "Beginner", "description": "Professional video for courses"},
            {"name": "Learning Experience Design", "provider": "IDEO U", "duration": "8 weeks", "level": "Intermediate", "description": "Human-centered course design"}
        ]
    },
    "school teacher": {
        "degrees": ["B.Ed", "BA + B.Ed", "D.El.Ed"],
        "streams": ["Any stream + Teacher Training"],
        "skills": ["Pedagogy", "Classroom Management", "Subject Expertise", "Assessment Design", "EdTech Tools"],
        "certifications": ["CTET/State TET", "Cambridge Teaching Certificate", "Google Certified Educator"],
        "courses": [
            {"name": "Foundations of Teaching for Learning", "provider": "Commonwealth via Coursera", "duration": "6 months", "level": "Beginner", "description": "Core teaching methodologies"},
            {"name": "Classroom Management Strategies", "provider": "Udemy", "duration": "4 weeks", "level": "Beginner", "description": "Effective classroom control"},
            {"name": "Technology for Teachers", "provider": "Google for Education", "duration": "4 weeks", "level": "Beginner", "description": "Integrate tech in teaching"},
            {"name": "Differentiated Instruction", "provider": "edX", "duration": "6 weeks", "level": "Intermediate", "description": "Teach diverse learners"}
        ]
    },
    "edtech product manager": {
        "degrees": ["MBA in Education Tech", "B.Tech + MBA", "MA in Education + Tech Skills"],
        "streams": ["Science/Commerce + Education interest"],
        "skills": ["Product Management", "EdTech Trends", "Learning Analytics", "User Research", "Agile"],
        "certifications": ["Certified Product Manager", "Learning Engineering Certificate", "Google PM Certificate"],
        "courses": [
            {"name": "EdTech Product Management", "provider": "Product School", "duration": "8 weeks", "level": "Intermediate", "description": "Build educational technology products"},
            {"name": "Learning Engineering Fundamentals", "provider": "Carnegie Learning via Coursera", "duration": "3 months", "level": "Intermediate", "description": "Science of learning design"},
            {"name": "Digital Product Management", "provider": "University of Virginia", "duration": "4 months", "level": "Beginner", "description": "Product lifecycle management"},
            {"name": "Analytics for EdTech", "provider": "LinkedIn Learning", "duration": "4 weeks", "level": "Intermediate", "description": "Measure learning outcomes"}
        ]
    },
    "corporate trainer": {
        "degrees": ["MBA in HR", "MA in Organizational Psychology", "BBA + Professional Certifications"],
        "streams": ["Commerce/Arts with Management focus"],
        "skills": ["Training Needs Analysis", "Presentation Skills", "Facilitation", "LMS Management", "Assessment Design"],
        "certifications": ["CPTM (Certified Professional in Training Management)", "ATD Master Trainer", "NSDC Certified Trainer"],
        "courses": [
            {"name": "Training & Development Professional Certificate", "provider": "ATD via LinkedIn Learning", "duration": "3 months", "level": "Intermediate", "description": "Corporate training fundamentals and adult learning theory"},
            {"name": "Instructional Design for Corporate Training", "provider": "Udemy", "duration": "6 weeks", "level": "Beginner", "description": "Design effective corporate training programs"},
            {"name": "Facilitation Skills Masterclass", "provider": "Coursera", "duration": "4 weeks", "level": "Intermediate", "description": "Lead engaging training sessions"},
            {"name": "Learning Analytics & ROI", "provider": "LinkedIn Learning", "duration": "4 weeks", "level": "Advanced", "description": "Measure training effectiveness and business impact"}
        ]
    },
    "education consultant": {
        "degrees": ["MA in Education Policy", "MBA in Education Management", "M.Ed + Consulting Experience"],
        "streams": ["Any stream + Education specialization"],
        "skills": ["Education Policy Analysis", "Curriculum Development", "School Improvement", "Data Analysis", "Stakeholder Management"],
        "certifications": ["Certified Education Planner (CEP)", "School Accreditation Consultant", "NEP 2020 Specialist"],
        "courses": [
            {"name": "Education Policy & Planning", "provider": "Harvard via edX", "duration": "4 months", "level": "Intermediate", "description": "Analyze and develop education policies"},
            {"name": "School Leadership & Management", "provider": "Coursera", "duration": "3 months", "level": "Intermediate", "description": "Lead educational institutions effectively"},
            {"name": "Curriculum Design & Assessment", "provider": "UNESCO IIEP", "duration": "6 weeks", "level": "Advanced", "description": "Create aligned curriculum and assessments"},
            {"name": "Education Consulting Skills", "provider": "Udemy", "duration": "4 weeks", "level": "Beginner", "description": "Build a successful education consulting practice"}
        ]
    }
}

def get_career_education_info(career: str) -> Dict:
    """Get career-specific education recommendations."""
    career_lower = career.lower().strip()
    
    # Try exact match first
    if career_lower in CAREER_EDUCATION_MAP:
        return CAREER_EDUCATION_MAP[career_lower]
    
    # Try partial match
    for key, info in CAREER_EDUCATION_MAP.items():
        if key in career_lower or career_lower in key:
            return info
        # Check for key words
        key_words = key.split()
        if any(word in career_lower for word in key_words if len(word) > 3):
            return info
    
    # Default generic info
    return {
        "degrees": ["Bachelor's in relevant field", "Professional certifications"],
        "streams": ["Choose based on career interest"],
        "skills": ["Domain expertise", "Communication", "Problem solving", "Digital literacy"],
        "certifications": ["Industry-specific certifications", "Online course completions"],
        "courses": [
            {"name": f"Introduction to {career}", "provider": "Coursera", "duration": "4 weeks", "level": "Beginner", "description": f"Fundamentals and basics of {career} profession"},
            {"name": f"{career} Fundamentals", "provider": "Udemy", "duration": "6 weeks", "level": "Beginner", "description": f"Core concepts and practical skills for {career}"},
            {"name": f"Advanced {career} Skills", "provider": "LinkedIn Learning", "duration": "8 weeks", "level": "Intermediate", "description": f"Deep dive into professional {career} skills"},
            {"name": "Professional Development", "provider": "edX", "duration": "4 weeks", "level": "All Levels", "description": "Career growth and industry best practices"}
        ]
    }

def generate_education_based_roadmap(career: str, education_level: str) -> List[Dict]:
    """Generate truly unique roadmap phases based on career-specific templates and education level."""
    
    edu_info = get_education_info(education_level)
    career_info = get_career_education_info(career)
    career_lower = career.lower().strip()
    level_lower = education_level.lower()
    phases = []
    phase_num = 1
    
    # Get career-specific courses
    all_courses = career_info.get("courses", [])
    
    # Check if we have career-specific phase templates
    career_template = None
    for key in CAREER_PHASE_TEMPLATES:
        if key in career_lower or career_lower in key:
            career_template = CAREER_PHASE_TEMPLATES[key]
            break
    
    # EDUCATION-FOCUSED CAREERS with specialized templates
    if career_template:
        template_phases = career_template.get("phases", [])
        
        # Determine starting phase based on education level
        start_phase_idx = 0
        if "10th" in level_lower:
            start_phase_idx = 0  # Start from beginning
        elif "12th" in level_lower or "high school" in level_lower:
            # Skip pre-degree phases if any
            start_phase_idx = 0 if "school teacher" not in career_lower else 1
        elif "bachelor" in level_lower or "undergraduate" in level_lower:
            # Skip degree phases
            if "school teacher" in career_lower:
                start_phase_idx = 2  # Jump to B.Ed phase
            else:
                start_phase_idx = min(1, len(template_phases) - 1)
        elif "master" in level_lower or "postgraduate" in level_lower:
            start_phase_idx = min(2, len(template_phases) - 1)
        
        # Generate phases from template
        for i, template in enumerate(template_phases[start_phase_idx:], 1):
            # Calculate duration based on phase position
            if "school teacher" in career_lower:
                durations = ["2 years", "3 years", "2 years", "6 months", "Ongoing"]
            elif "corporate trainer" in career_lower:
                durations = ["2-3 years", "6 months", "6 months", "1 year", "Ongoing"]
            elif "education consultant" in career_lower:
                durations = ["6 months", "3-4 years", "6 months", "1-2 years", "Ongoing"]
            elif "edtech product manager" in career_lower:
                durations = ["4-6 months", "3-4 months", "3 months", "1 year"]
            else:
                durations = ["3-4 months", "4-6 months", "4-6 months", "6-12 months"]
            
            duration = durations[min(i-1, len(durations)-1)]
            
            # Distribute courses across phases
            course_idx = min(i-1, len(all_courses)-1) if all_courses else -1
            phase_courses = [all_courses[course_idx]] if course_idx >= 0 else []
            
            phases.append({
                "phase": f"Phase {i}",
                "title": template["title"],
                "duration": duration,
                "details": template["focus"],
                "milestones": template["milestones"],
                "courses": phase_courses
            })
        
        return phases
    
    # GENERIC CAREER ROADMAP (for non-education careers)
    # For 10th class students - need academic foundation phases
    if "10th" in level_lower:
        phases.append({
            "phase": f"Phase {phase_num}",
            "title": f"Higher Secondary for {career} Track",
            "duration": "2 years",
            "details": f"Complete your higher secondary education (11th and 12th) with subjects strategically aligned to your goal of becoming a {career}. The recommended streams for this career path include {', '.join(career_info.get('streams', ['Science/Arts'])[:2])}. During these two years, focus on building strong academic fundamentals while exploring the field through online resources, YouTube tutorials, and beginner courses. Research the entrance exams you'll need to clear for admission to relevant bachelor's programs. Connect with seniors or professionals in the field through social media to understand the career path better. Maintain disciplined study habits and aim for scores that will open doors to top colleges. Start developing relevant skills early by taking free online courses and working on small projects.",
            "milestones": [
                f"Choose stream: {career_info.get('streams', ['Relevant stream'])[0]}",
                "Score 70%+ in 12th board exams",
                "Research entrance exams for target colleges",
                "Complete 1-2 free online courses in the field"
            ],
            "courses": [all_courses[0]] if all_courses else []
        })
        phase_num += 1
        
        phases.append({
            "phase": f"Phase {phase_num}",
            "title": f"Bachelor's Degree in {career.split()[0] if ' ' in career else career}",
            "duration": "3-4 years",
            "details": f"Pursue a bachelor's degree aligned with your career goals. Recommended programs include {', '.join(career_info.get('degrees', ['Relevant Bachelor degree'])[:2])}. During this phase, focus on building strong academic fundamentals while gaining practical experience through internships, projects, and extracurricular activities. Join relevant college clubs and student organizations to network with like-minded peers. Participate in competitions, hackathons, or industry events to gain exposure and build your resume. Start building your professional portfolio with academic projects and personal initiatives. Aim for a minimum CGPA of 7.5 to remain competitive for campus placements and higher studies. Use semester breaks for internships at companies in your target industry to gain real-world experience and understand industry expectations.",
            "milestones": [
                f"Get admission in {career_info.get('degrees', ['Bachelor program'])[0]}",
                "Maintain 7.5+ CGPA",
                "Complete 2 internships during college",
                "Build portfolio with 3-5 projects"
            ],
            "courses": [all_courses[1]] if len(all_courses) > 1 else []
        })
        phase_num += 1
        
    # For 12th class students
    elif "12th" in level_lower or "high school" in level_lower:
        phases.append({
            "phase": f"Phase {phase_num}",
            "title": f"Bachelor's Degree for {career}",
            "duration": "3-4 years",
            "details": f"Pursue a bachelor's degree that provides the foundation for your career as a {career}. Recommended degree programs include {', '.join(career_info.get('degrees', ['Relevant Bachelor degree'])[:2])}. Focus on building strong academic fundamentals while actively seeking practical experience through internships and projects. Join relevant clubs, participate in competitions, and attend industry events to expand your network. Start early with skill development by taking online courses alongside your degree. Build relationships with professors and industry professionals who can mentor you. Use vacation periods for internships to gain hands-on experience and understand industry expectations. Maintain a strong academic record while developing the practical skills employers value.",
            "milestones": [
                "Clear entrance exams (JEE/NIFT/NID as applicable)",
                f"Complete {career_info.get('degrees', ['Bachelor degree'])[0]}",
                "Complete 2-3 internships",
                "Build initial portfolio"
            ],
            "courses": [all_courses[0]] if all_courses else []
        })
        phase_num += 1
    
    # Core skill development phase (for all)
    skill_list = career_info.get("skills", ["Core skills"])[:4]
    phases.append({
        "phase": f"Phase {phase_num}",
        "title": f"Master {career} Core Skills",
        "duration": "6-12 months",
        "details": f"This phase focuses on developing deep expertise in the essential skills required for a successful career as a {career}. The core skills you need to master include {', '.join(skill_list)}. Invest in industry-recognized certifications to validate your skills and stand out to potential employers. Create a learning schedule that balances theoretical knowledge with hands-on practice. Build a strong portfolio showcasing 3-5 quality projects that demonstrate your abilities. Focus on real-world applications rather than just tutorials. Join online communities and forums related to your field to learn from experienced professionals. Participate in challenges, contribute to open-source projects, or take on freelance work to apply your skills in real scenarios. Create a professional online presence through LinkedIn and relevant platforms.",
        "milestones": [
            f"Master: {skill_list[0] if skill_list else 'Primary skill'}",
            f"Get certified: {career_info.get('certifications', ['Industry certification'])[0]}",
            "Build 3-5 portfolio projects",
            "Create professional LinkedIn profile with 500+ connections"
        ],
        "courses": all_courses[1:3] if len(all_courses) > 2 else all_courses
    })
    phase_num += 1
    
    # Practical experience phase
    phases.append({
        "phase": f"Phase {phase_num}",
        "title": f"Build Real {career} Experience",
        "duration": "6-12 months",
        "details": f"Transition from learning to doing by gaining hands-on professional experience as a {career}. Actively seek internships at companies that align with your career goals, whether startups for broad exposure or established companies for structured learning. Work on real client projects through freelancing platforms to build your reputation and portfolio. Contribute to open-source projects or collaborative initiatives in your field. Build your professional network by attending industry meetups, webinars, and conferences. Connect with professionals on LinkedIn and seek informational interviews to learn about their career paths. Request recommendations from supervisors and colleagues to strengthen your profile. Document your projects and contributions to update your portfolio with substantial work examples.",
        "milestones": [
            f"Complete internship at a company hiring {career}s",
            "Work on 2-3 client/real-world projects",
            "Get 3+ professional recommendations",
            "Build network of 200+ industry connections"
        ],
        "courses": [all_courses[2]] if len(all_courses) > 2 else []
    })
    phase_num += 1
    
    # Career launch phase
    phases.append({
        "phase": f"Phase {phase_num}",
        "title": f"Launch Your {career} Career",
        "duration": "3-6 months",
        "details": f"Execute a strategic job search to land your first role as a {career}. Polish your resume and portfolio to highlight your skills, projects, and achievements. Prepare for interviews by researching common questions, practicing with peers or mentors, and understanding what employers look for. Apply strategically to positions that match your skills and career goals, targeting at least 50 relevant openings. Leverage your network for referrals, which significantly increase your chances of getting interviews. Follow up professionally with recruiters and hiring managers. Be open to entry-level positions that offer learning opportunities and clear growth paths. Once you land a role, focus on exceeding expectations during your probation period and continue learning on the job.",
        "milestones": [
            "Finalize resume and portfolio",
            "Practice mock interviews (10+ sessions)",
            "Apply to 50+ relevant positions",
            f"Land your first {career} role"
        ],
        "courses": [all_courses[3]] if len(all_courses) > 3 else []
    })
    
    return phases
    
    return phases

async def generate_dynamic_roadmap(career: str, education_level: str) -> List[Dict]:
    """Generate a dynamic learning roadmap using LLM."""
    
    edu_info = get_education_info(education_level)
    
    # Generate base roadmap based on education level and career
    base_roadmap = generate_education_based_roadmap(career, education_level)
    
    system_prompt = f"""You are a career counselor in India who creates realistic career roadmaps.
The student's current education: {education_level}
Target career: {career}
Create phases that start from their CURRENT education level."""
    
    prompt = f"""Create a personalized career roadmap for becoming a {career}.

STUDENT PROFILE:
- Current Education: {education_level}
- Target Career: {career}
- Country: India

Create {len(base_roadmap)} phases starting from their current level. Be SPECIFIC about:
1. If 10th class: Include completing 11th-12th, then college, then skills
2. If 12th class: Start with college admission, then skills
3. If Bachelor's: Focus on skills, internships, job prep

Respond with JSON array:
[
    {{
        "phase": "Phase 1",
        "title": "Specific title for {education_level} student",
        "duration": "X years/months",
        "details": "Detailed steps specific to becoming {career} from {education_level}",
        "milestones": ["specific milestone 1", "specific milestone 2", "specific milestone 3", "specific milestone 4"]
    }}
]

IMPORTANT: 
- First phase must address their IMMEDIATE next step from {education_level}
- Include estimated time to reach {career} from {education_level}
- Be realistic about timelines (10th → professional takes 5-6 years)"""
    
    roadmap = base_roadmap  # Start with education-based roadmap
    
    if check_ollama_available():
        llm_response = call_ollama(prompt, system_prompt, temperature=0.5)
        try:
            cleaned = re.sub(r'```json?\s*', '', llm_response)
            cleaned = re.sub(r'```\s*', '', cleaned)
            match = re.search(r'\[[\s\S]*\]', cleaned)
            if match:
                parsed_roadmap = json.loads(match.group())
                # Ensure all fields are strings
                for item in parsed_roadmap:
                    if 'phase' in item:
                        item['phase'] = str(item['phase']) if not isinstance(item['phase'], str) else item['phase']
                        if not item['phase'].lower().startswith('phase'):
                            item['phase'] = f"Phase {item['phase']}"
                    if 'title' in item:
                        item['title'] = str(item['title'])
                    if 'duration' in item:
                        item['duration'] = str(item['duration'])
                    if 'details' in item:
                        item['details'] = str(item['details'])
                    if 'milestones' in item and isinstance(item['milestones'], list):
                        item['milestones'] = [str(m) for m in item['milestones']]
                # Use LLM roadmap if valid
                if len(parsed_roadmap) >= 3:
                    roadmap = parsed_roadmap
        except Exception as e:
            logger.error(f"Roadmap parsing error: {e}")
            pass
    
    # The roadmap already has courses from generate_education_based_roadmap
    # Just ensure all phases have a courses array
    for phase in roadmap:
        if "courses" not in phase:
            phase["courses"] = []
    
    return roadmap

# ============= Google News RSS Integration =============

def fetch_google_news(query: str, num_results: int = 5) -> List[Dict]:
    """Fetch news from Google News RSS feed."""
    try:
        # Encode query for URL
        encoded_query = query.replace(" ", "+")
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}+jobs+careers&hl=en-IN&gl=IN&ceid=IN:en"
        
        feed = feedparser.parse(rss_url)
        
        articles = []
        for entry in feed.entries[:num_results]:
            # Clean up the title (remove source suffix)
            title = entry.title
            source = "Google News"
            
            # Try to extract source from title
            if " - " in title:
                parts = title.rsplit(" - ", 1)
                title = parts[0]
                source = parts[1] if len(parts) > 1 else "Google News"
            
            articles.append({
                "title": title,
                "link": entry.link,
                "source": source,
                "published": entry.get("published", "Recent"),
                "summary": entry.get("summary", "")[:200] + "..." if entry.get("summary") else ""
            })
        
        return articles
    except Exception as e:
        logger.error(f"News fetch error: {e}")
        return []

async def generate_news_insights(career: str, articles: List[Dict]) -> str:
    """Generate insights from news articles using LLM."""
    
    if not articles:
        return f"Stay updated on {career} industry trends through professional networks and industry publications."
    
    headlines = " | ".join([a["title"] for a in articles[:5]])
    
    system_prompt = "You are a career market analyst who provides brief, actionable insights."
    prompt = f"""Based on these recent headlines about {career}:
{headlines}

Provide a 2-3 sentence market insight summary for job seekers. Be specific and actionable."""
    
    if check_ollama_available():
        insight = call_ollama(prompt, system_prompt, temperature=0.7)
        if insight:
            return insight[:500]
    
    return f"The {career} field shows active hiring with evolving skill requirements. Focus on continuous learning and industry networking to stay competitive."

# ============= API Endpoints =============

# Query ID counter (in-memory for simplicity)
query_counter = {"id": 0}

@app.get("/api/health")
async def health_check():
    ollama_status = "connected" if check_ollama_available() else "unavailable"
    return {
        "status": "healthy",
        "version": "3.0.0",
        "llm": ollama_status,
        "features": ["dynamic_careers", "news_feed", "smart_chat", "course_recommendations"]
    }

@app.post("/api/recommend", response_model=CareerRecommendationResponse)
async def get_recommendation(request: CareerQueryRequest):
    """Generate LLM-powered career recommendation based on user inputs."""
    try:
        # Use LLM to dynamically find relevant careers based on actual user inputs
        logger.info(f"User interests: {request.interests}, skills: {request.skills}, hobbies: {request.hobbies}")
        
        # Get careers directly from LLM based on user's actual inputs
        matched_careers = await get_careers_from_llm(request)
        
        logger.info(f"LLM matched careers: {[c.get('title') for c in matched_careers]}")
        
        if not matched_careers:
            matched_careers = [{"title": "Career Consultant", "salary": "₹5-15 LPA", 
                               "demand": "Medium", "growth": "10%", "category": "general"}]
        
        # Generate LLM-powered analysis
        llm_analysis = await generate_llm_recommendation(request, matched_careers)
        
        # Generate dynamic roadmap for TOP career (main roadmap)
        main_roadmap = await generate_dynamic_roadmap(matched_careers[0]["title"], request.educationLevel)
        
        # Fetch news insights
        news_articles = fetch_google_news(matched_careers[0]["title"])
        news_insight = await generate_news_insights(matched_careers[0]["title"], news_articles)
        
        # Build landscape data with INDIVIDUAL roadmaps for each career
        landscape = []
        for i, career in enumerate(matched_careers):
            # Generate roadmap for each career (use cached for first one)
            if i == 0:
                career_roadmap = main_roadmap
            else:
                career_roadmap = generate_education_based_roadmap(career["title"], request.educationLevel)
            
            landscape.append({
                "title": career["title"],
                "salary": career.get("salary", "₹5-20 LPA"),
                "demand": career.get("demand", "Medium"),
                "description": f"Excellent fit for your interests in {', '.join(request.interests[:2])}. Growth rate: {career.get('growth', '10%')}",
                "requiredSkills": llm_analysis.get("requiredSkills", [])[:3],
                "growthRate": career.get("growth", "10%"),
                "roadmap": career_roadmap  # Individual roadmap for each career
            })
        
        # Build featured career
        top_career = matched_careers[0]
        # Build featured career - ALWAYS use the matched top career, not LLM override
        featured = {
            "title": top_career["title"],  # Always use matched career, not LLM
            "alignment": llm_analysis.get("whyThisFits", f"Your profile strongly aligns with {top_career['title']}"),
            "passion": llm_analysis.get("dayInLife", "This role offers daily opportunities to apply your skills and interests."),
            "outlook": llm_analysis.get("marketOutlook", f"{top_career.get('demand', 'High')} demand in the current market"),
            "dayInLife": llm_analysis.get("dayInLife", ""),
            "challenges": llm_analysis.get("challenges", "")
        }
        
        # Build action steps
        steps = [
            f"Research {top_career['title']} roles on LinkedIn and Naukri",
            f"Start with foundational courses on Coursera or Udemy",
            "Build 2-3 portfolio projects to showcase your skills",
            "Network with professionals in the field on LinkedIn",
            "Apply for internships or entry-level positions",
            "Join relevant communities and attend industry events"
        ]
        
        # Increment query ID
        query_counter["id"] += 1
        
        # Build structured data
        structured_data = {
            "landscape": landscape,
            "featured": featured,
            "roadmap": main_roadmap,  # Main roadmap for featured career
            "steps": steps,
            "marketInsights": [news_insight] + [a["title"] for a in news_articles[:3]]
        }
        
        # Build markdown recommendation
        recommendation_md = f"""# Career Recommendation: {featured['title']}

## Why This Career Fits You
{featured['alignment']}

## A Day in the Life
{featured['passion']}

## Market Outlook
{featured['outlook']}

## Challenges & How to Overcome Them
{llm_analysis.get('challenges', 'Focus on continuous learning and building practical experience.')}

## Required Skills
{chr(10).join(['- ' + skill for skill in llm_analysis.get('requiredSkills', ['Communication', 'Problem Solving'])])}

## Alternative Career Paths
{chr(10).join(['- ' + alt for alt in llm_analysis.get('alternativeCareers', [c['title'] for c in matched_careers[1:3]])])}

## Market News & Insights
{news_insight}
"""
        
        return CareerRecommendationResponse(
            queryId=query_counter["id"],
            recommendation=recommendation_md,
            structuredData=StructuredData(**structured_data),
            llmPowered=check_ollama_available()
        )
        
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news/{career}", response_model=NewsResponse)
async def get_career_news(career: str):
    """Get latest news and insights for a specific career."""
    try:
        articles = fetch_google_news(career, num_results=8)
        insights = await generate_news_insights(career, articles)
        
        return NewsResponse(
            career=career,
            articles=[NewsItem(**a) for a in articles],
            insights=insights
        )
    except Exception as e:
        logger.error(f"News error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= Off-Topic Detection =============

OFF_TOPIC_KEYWORDS = [
    "capital of india", "capital of usa", "president of", "prime minister of", 
    "weather today", "movie review", "film release", "song lyrics", "cricket score",
    "football score", "actor biography", "actress age", "recipe for", "how to cook",
    "game score", "politics news", "election result", "religion", "temple timings", 
    "church service", "mosque", "festival date", "celebrity news", "gossip",
    "dating tips", "relationship advice", "marriage", "divorce", "tell me a joke", 
    "funny video", "meme", "stock price today", "bitcoin price", "crypto price", 
    "lottery result", "betting odds", "gambling"
]

def is_off_topic(message: str, conversation_history: list = None) -> bool:
    """Check if message is off-topic (not career-related)."""
    msg_lower = message.lower().strip()
    
    # Very short messages like "in guntur" are usually follow-ups - NOT off-topic
    if len(msg_lower.split()) <= 3:
        # Check if it's a clear off-topic phrase
        clear_off_topic = ["tell me a joke", "what's the weather", "who won"]
        if not any(phrase in msg_lower for phrase in clear_off_topic):
            return False  # Assume it's a follow-up question
    
    # Career-related keywords - if present, it's on-topic
    career_keywords = ["career", "job", "salary", "skill", "course", "college", "university", 
                       "interview", "resume", "work", "profession", "industry", "hire", "intern",
                       "education", "degree", "certification", "training", "experience", "role",
                       "company", "placement", "aptitude", "qualification", "study", "learn",
                       "best", "top", "how to", "what", "which", "where", "path", "roadmap",
                       "program", "institute", "admission", "fee", "eligibility", "scope"]
    
    if any(kw in msg_lower for kw in career_keywords):
        return False
    
    # Location names are usually career-related (asking about colleges in a city)
    # Don't flag these as off-topic
    location_indicators = ["in ", "at ", "near ", "around ", "from "]
    if any(msg_lower.startswith(loc) or f" {loc}" in msg_lower for loc in location_indicators):
        return False  # Probably asking about colleges/jobs in a location
    
    # Check for clearly off-topic keywords (must match exactly)
    for keyword in OFF_TOPIC_KEYWORDS:
        if keyword in msg_lower:
            return True
    
    # Check if it's a general knowledge question NOT about careers
    if re.search(r"what is the (capital|president|population) of", msg_lower):
        return True
    if re.search(r"who (is|was) the (president|prime minister|king)", msg_lower):
        return True
    
    return False

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Intelligent chat endpoint with role-based context."""
    
    message = request.message
    context = request.context or ""
    selected_role = request.selectedRole or ""
    history = request.conversationHistory or []
    
    # Check for off-topic questions FIRST
    if is_off_topic(message):
        role_text = f"<span style=\"color:#7c3aed;font-weight:bold\">{selected_role}</span>" if selected_role else "your career path"
        return ChatResponse(
            response=f"""Hey! I'm your <span style="color:#7c3aed;font-weight:bold">Career Advisor</span> 🎯

I focus on helping you with {role_text}! Ask me about:
• <span style="color:#059669;font-weight:bold">Skills</span> you need
• <span style="color:#059669;font-weight:bold">Education</span> requirements
• <span style="color:#059669;font-weight:bold">Salary</span> expectations
• <span style="color:#059669;font-weight:bold">How to get started</span>

What career question can I help with? 🚀""",
            suggestedQuestions=[
                f"What skills do I need for {selected_role or 'this career'}?",
                "What's the salary range?",
                "How do I get started?"
            ]
        )
    
    # Build conversation context
    conversation_context = ""
    if history:
        conversation_context = "\n".join([f"{m['role']}: {m['content']}" for m in history[-5:]])
    
    system_prompt = f"""You are a friendly, energetic career mentor who gives SHORT, punchy advice.

CRITICAL RULES:
1. ONLY answer questions about CAREERS, JOBS, SKILLS, EDUCATION, INTERVIEWS, SALARIES, COURSES, COLLEGES
2. Location-based questions ARE VALID if about colleges, jobs, or career opportunities (e.g., "colleges in Guntur", "jobs in Hyderabad")
3. If user asks about unrelated topics (politics, movies, sports scores, recipes), say: "I'm your Career Advisor! Let's focus on your career. What would you like to know?"
4. Keep response UNDER 100 words - be direct and conversational
5. Use numbered steps (1. 2. 3.) for action items - max 4 steps
6. Use <span style="color:#7c3aed;font-weight:bold">purple text</span> for important terms
7. Use <span style="color:#059669;font-weight:bold">green text</span> for positive things
8. Use <span style="color:#dc2626;font-weight:bold">red text</span> for warnings
9. NO markdown headers (no # or ###)
10. Be conversational, friendly, encouraging
11. If the user mentions a city/location, answer about colleges/jobs in that location

{'Focused on: ' + selected_role if selected_role else ''}"""
    
    prompt = f"""{'Chat history:\n' + conversation_context if conversation_context else ''}

Question: {message}

IMPORTANT: Location questions about colleges/jobs are VALID career questions - answer them!
Give a SHORT response (under 100 words). Use colored HTML spans."""
    
    if check_ollama_available():
        response = call_ollama(prompt, system_prompt, temperature=0.7)
        if response:
            # Generate follow-up questions
            followup_prompt = f"Based on this conversation about {selected_role or 'careers'}, suggest 3 brief follow-up questions the user might ask. Return as JSON array: [\"q1\", \"q2\", \"q3\"]"
            followup_response = call_ollama(followup_prompt, "Respond with JSON array only", temperature=0.8)
            
            suggestions = []
            try:
                match = re.search(r'\[[\s\S]*?\]', followup_response)
                if match:
                    suggestions = json.loads(match.group())[:3]
            except:
                pass
            
            if not suggestions:
                suggestions = [
                    f"What skills should I focus on first?",
                    f"How do I build a portfolio?",
                    f"What's the typical salary progression?"
                ]
            
            return ChatResponse(response=response, suggestedQuestions=suggestions)
    
    # Fallback responses - SHORT and interactive with colors
    message_lower = message.lower()
    role_text = f'<span style="color:#7c3aed;font-weight:bold">{selected_role}</span>' if selected_role else 'this role'
    
    if "salary" in message_lower or "pay" in message_lower:
        response = f"""Here's the salary range for {role_text}:

1. <span style="color:#059669;font-weight:bold">Entry (0-2 yrs):</span> ₹4-8 LPA
2. <span style="color:#059669;font-weight:bold">Mid (3-5 yrs):</span> ₹8-18 LPA
3. <span style="color:#059669;font-weight:bold">Senior (5+ yrs):</span> ₹18-35+ LPA

<span style="color:#dc2626">Pro tip:</span> Product companies & metros pay 30-50% more! 💰"""

    elif "skill" in message_lower:
        response = f"""<span style="color:#7c3aed;font-weight:bold">Key skills</span> you need:

1. <span style="color:#059669;font-weight:bold">Core domain</span> expertise
2. <span style="color:#059669;font-weight:bold">Problem-solving</span> mindset  
3. <span style="color:#059669;font-weight:bold">Communication</span> skills

Start with YouTube/Coursera courses, then <span style="color:#7c3aed;font-weight:bold">build 2-3 projects</span>. That's what matters! 🚀"""

    elif "start" in message_lower or "begin" in message_lower or "how to" in message_lower:
        response = f"""Getting into {role_text}? Here's your roadmap:

1. <span style="color:#7c3aed;font-weight:bold">Learn basics</span> (Coursera/YouTube) - 2 months
2. <span style="color:#7c3aed;font-weight:bold">Build projects</span> - Show don't tell!
3. <span style="color:#7c3aed;font-weight:bold">Get internship</span> or freelance
4. <span style="color:#059669;font-weight:bold">Network on LinkedIn</span>

<span style="color:#059669">You've got this!</span> Start today! 💪"""

    elif "interview" in message_lower:
        response = f"""<span style="color:#7c3aed;font-weight:bold">Interview prep</span> checklist:

1. Know your <span style="color:#059669;font-weight:bold">projects inside-out</span>
2. Practice on <span style="color:#7c3aed">Pramp/LeetCode</span>
3. Research the company
4. Prepare <span style="color:#059669;font-weight:bold">STAR stories</span>

<span style="color:#dc2626">Don't skip:</span> Mock interviews with friends! Good luck! 🎯"""

    elif "education" in message_lower or "class" in message_lower or "10th" in message_lower or "12th" in message_lower:
        response = f"""After 10th for {role_text}:

1. <span style="color:#7c3aed;font-weight:bold">12th Science</span> (PCM/PCB based on field)
2. <span style="color:#7c3aed;font-weight:bold">Bachelor's degree</span> in relevant field
3. <span style="color:#059669;font-weight:bold">Internships</span> while studying
4. <span style="color:#059669;font-weight:bold">Master's/certifications</span> (optional but helpful)

Start exploring the field now - no need to wait! 📚"""

    else:
        response = f"""Hey! I can help you with {role_text}! 👋

Ask me about:
• <span style="color:#059669;font-weight:bold">Salary</span> expectations
• <span style="color:#7c3aed;font-weight:bold">Skills</span> needed
• <span style="color:#7c3aed;font-weight:bold">How to start</span>
• <span style="color:#059669;font-weight:bold">Interview</span> tips

What would you like to know? 🎯"""
    
    return ChatResponse(
        response=response,
        suggestedQuestions=[
            "What's the salary range?",
            "How do I get started?",
            "What skills do I need?"
        ]
    )

@app.get("/api/courses/{career}")
async def get_courses(career: str, education_level: str = "Undergraduate"):
    """Get dynamic course recommendations for a career."""
    try:
        courses = await generate_dynamic_courses(career, education_level)
        return {"career": career, "courses": courses}
    except Exception as e:
        logger.error(f"Courses error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/careers/explore")
async def explore_careers(category: Optional[str] = None):
    """Explore available career categories and options."""
    if category and category in CAREER_CATEGORIES:
        return {
            "category": category,
            "careers": CAREER_CATEGORIES[category]["careers"],
            "keywords": CAREER_CATEGORIES[category]["keywords"][:10]
        }
    
    return {
        "categories": list(CAREER_CATEGORIES.keys()),
        "total_careers": sum(len(c["careers"]) for c in CAREER_CATEGORIES.values())
    }

# ============= Main =============

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 Career Recommender API v3.0 - LLM Powered")
    print("=" * 60)
    print(f"📡 API: http://localhost:8000")
    print(f"📚 Docs: http://localhost:8000/docs")
    print(f"🤖 LLM: {'Connected' if check_ollama_available() else 'Not Available - using fallback'}")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
