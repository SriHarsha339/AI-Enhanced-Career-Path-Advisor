"""
Pydantic schemas for request/response validation.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class EducationInput(BaseModel):
    """User education details."""
    degree: str = Field(..., description="e.g., 10th, 12th, Bachelor's, Master's")
    field: Optional[str] = Field(None, description="e.g., Science, Engineering")
    year: Optional[int] = Field(None, description="Year of passing/current")
    cgpa: Optional[float] = Field(None, ge=0, le=10)


class PreferencesInput(BaseModel):
    """User preferences."""
    preferred_domain: Optional[str] = None
    country: Optional[str] = None
    remote_preference: Optional[str] = None  # hybrid/remote/onsite
    timeframe: Optional[str] = None  # months to transition
    budget: Optional[str] = None


class ProfileRequest(BaseModel):
    """Main request schema for career recommendation."""
    name: Optional[str] = None
    education: EducationInput
    skills: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    projects: Optional[List[str]] = Field(default_factory=list)
    preferences: Optional[PreferencesInput] = None


class ScoreBreakdown(BaseModel):
    """Score breakdown for a career."""
    skill_match: float
    interest_match: float
    education_match: float
    market_demand: float
    penalty: float


class SkillGap(BaseModel):
    """Missing skill information."""
    skill: str
    reason: str
    priority: str  # high|med|low


class RoadmapStep(BaseModel):
    """Roadmap step for career transition."""
    step: str
    duration: Optional[str] = None
    resources: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)


class Evidence(BaseModel):
    """Evidence snippet from RAG."""
    snippet: str
    source: str
    chunk_id: str


class CareerRecommendation(BaseModel):
    """Single career recommendation."""
    career_id: str
    title: str
    category: Optional[str] = None
    score: float = Field(ge=0, le=1)
    score_breakdown: ScoreBreakdown
    why_fit: List[str]
    why_not_others: List[str] = Field(default_factory=list)
    skill_gaps: List[SkillGap]
    roadmap: List[RoadmapStep]
    evidence: List[Evidence] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class RecommendationResponse(BaseModel):
    """Final response with all recommendations."""
    top_recommendations: List[CareerRecommendation]
    missing_info_questions: List[str]
    notes: List[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)
