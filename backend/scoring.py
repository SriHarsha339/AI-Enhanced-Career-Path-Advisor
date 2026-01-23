"""
Deterministic scoring system for career ranking.
Enhanced with fuzzy matching for better accuracy across all career domains.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Set
from backend.config import CAREERS_FILE, SCORE_WEIGHTS, BASELINE_CONFIDENCE, STRONG_MATCH_BONUS, CATEGORY_MATCH_BONUS
from backend.normalize import ProfileNormalizer
from backend.schemas import ScoreBreakdown, CareerRecommendation, SkillGap, RoadmapStep, Evidence

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# Semantic similarity mappings for fuzzy matching across domains
INTEREST_SYNONYMS = {
    # Healthcare & Medicine
    "healthcare": ["medicine", "health", "medical", "patient care", "helping people", "caregiving"],
    "medicine": ["healthcare", "medical", "doctor", "physician", "clinical", "health"],
    "helping people": ["caregiving", "social work", "nursing", "patient care", "counseling", "empathy"],
    "science": ["research", "biology", "chemistry", "physics", "scientific", "discovery"],
    "biology": ["science", "life sciences", "genetics", "medicine", "research"],
    "chemistry": ["science", "pharmacy", "medicine", "research", "laboratory"],
    
    # Legal
    "law": ["legal", "justice", "court", "legislation", "advocacy", "debate"],
    "justice": ["law", "legal", "ethics", "fairness", "rights", "advocacy"],
    "debate": ["argumentation", "public speaking", "law", "advocacy", "communication"],
    
    # Business & Finance (expanded)
    "business": ["commerce", "entrepreneurship", "management", "finance", "economics", "strategy", "mba", "consulting", "corporate"],
    "finance": ["accounting", "economics", "banking", "investment", "money", "business", "financial", "stocks", "markets", "trading", "financial_analyst", "portfolio"],
    "economics": ["finance", "business", "markets", "policy", "analysis", "statistics", "economic", "economist", "economic_research"],
    "management": ["leadership", "business", "strategy", "organization", "administration", "consultant", "consulting", "mba"],
    "accounting": ["finance", "financial_reporting", "tax", "auditing", "bookkeeping", "accountant", "cpa"],
    "investment": ["finance", "banking", "stocks", "portfolio", "trading", "wealth", "assets", "markets"],
    "banking": ["finance", "investment", "money", "loans", "financial", "economics"],
    "consulting": ["management", "business", "strategy", "mba", "analysis", "problem solving", "advisory"],
    "markets": ["finance", "trading", "stocks", "investment", "economics", "financial_analyst"],
    
    # Technology - SOFTWARE ENGINEERING (CRITICAL - must match Python/coding skills)
    # IMPORTANT: Keep "technology" separate from generic "engineering" (civil, mechanical, etc.)
    "technology": ["tech", "computers", "software", "it", "digital", "innovation", "coding", "programming", "developer", "software development", "software_engineer", "data_scientist"],
    "software development": ["software", "programming", "coding", "developer", "software_engineer", "technology", "python", "java", "javascript", "code", "apps"],
    "software": ["programming", "coding", "development", "technology", "computers", "apps", "applications", "software development", "developer", "software_engineer"],
    "programming": ["coding", "software", "development", "technology", "computers", "developer", "software_engineer", "code", "python", "java", "javascript", "c++"],
    "coding": ["programming", "software", "development", "technology", "developer", "software_engineer", "code", "python", "java"],
    "python": ["programming", "coding", "software", "developer", "software_engineer", "technology"],
    "java": ["programming", "coding", "software", "developer", "software_engineer", "technology"],
    "javascript": ["programming", "coding", "software", "developer", "software_engineer", "web development"],
    
    # Technology - DATA SCIENCE & AI (CRITICAL - must match data/AI interests)
    # Keep "data science" separate from generic "data"
    "data science": ["machine learning", "ai", "artificial intelligence", "data_scientist", "ml", "analytics", "python", "statistics", "deep learning"],
    "data": ["analytics", "statistics", "analysis", "research"],  # Generic data - NOT linked to data_scientist
    "ai": ["artificial intelligence", "machine learning", "ml", "data science", "deep learning", "neural networks", "data_scientist", "ai engineer"],
    "artificial intelligence": ["ai", "machine learning", "ml", "data science", "deep learning", "neural networks", "data_scientist", "technology"],
    "machine learning": ["ml", "ai", "artificial intelligence", "data science", "deep learning", "data_scientist", "python"],
    "ml": ["machine learning", "ai", "artificial intelligence", "data science", "data_scientist", "deep learning"],
    
    # Technology - General
    "innovation": ["technology", "creativity", "invention", "startups", "entrepreneurship", "problem_solving"],
    
    # Agriculture & Environment (expanded)
    "agriculture": ["farming", "crops", "animals", "rural", "food", "sustainability", "agricultural", "agronomy", "horticulture", "livestock", "agricultural_scientist"],
    "environment": ["sustainability", "ecology", "climate", "conservation", "green", "environmental", "environmental_scientist", "nature", "wildlife"],
    "nature": ["environment", "outdoors", "animals", "plants", "ecology", "wildlife", "conservation", "farming"],
    "farming": ["agriculture", "crops", "livestock", "rural", "agricultural", "agronomy", "food production"],
    "sustainability": ["environment", "ecology", "green", "renewable", "conservation", "climate"],
    "wildlife": ["animals", "nature", "conservation", "environment", "veterinary", "ecology"],
    
    # Creative & Design
    "design": ["creativity", "art", "visual", "aesthetics", "ux", "ui"],
    "creativity": ["art", "design", "innovation", "imagination", "expression"],
    "art": ["creativity", "design", "visual", "expression", "aesthetics"],
    
    # Education
    "teaching": ["education", "training", "mentoring", "knowledge", "learning"],
    "education": ["teaching", "learning", "training", "academia", "knowledge"],
    
    # Engineering (SEPARATE from technology - civil, mechanical, electrical are NOT tech)
    "engineering": ["technical", "building", "construction", "systems", "mechanics", "design"],
    "mechanics": ["engineering", "machinery", "automobiles", "systems"],
    "electronics": ["electrical", "circuits", "hardware"],
    
    # General
    "problem solving": ["analytical thinking", "critical thinking", "analysis", "logic", "troubleshooting", "algorithms", "programming"],
    "communication": ["writing", "speaking", "presentation", "interpersonal", "social"],
    "leadership": ["management", "team lead", "organization", "strategy", "decision making"],
    "research": ["analysis", "investigation", "study", "science", "discovery"],
}

# Skill category mappings for cross-domain matching
SKILL_CATEGORIES = {
    "analytical": ["analysis", "data analysis", "research", "statistics", "problem solving", "critical thinking", "analytical thinking", "investigation"],
    "communication": ["communication", "writing", "presentation", "public speaking", "interpersonal", "negotiation", "counseling", "teaching"],
    "technical": ["programming", "coding", "software", "engineering", "technical", "computers", "technology", "systems"],
    "scientific": ["science", "research", "biology", "chemistry", "physics", "laboratory", "medical knowledge", "clinical"],
    "creative": ["design", "creativity", "art", "innovation", "visual", "aesthetics", "ux", "ui"],
    "leadership": ["leadership", "management", "team lead", "strategy", "organization", "decision making", "project management"],
    "empathy": ["empathy", "patient care", "helping people", "caregiving", "counseling", "social work", "understanding"],
}

# CRITICAL: Skill synonyms for direct skill matching
# Keep these TIGHT - only closely related skills
SKILL_SYNONYMS = {
    # Programming Languages -> programming skill (DIRECT MATCHES)
    "python": ["programming", "coding", "software", "development"],
    "java": ["programming", "coding", "software", "development"],
    "javascript": ["programming", "coding", "software", "development", "web"],
    "c++": ["programming", "coding", "software"],
    "c#": ["programming", "coding", "software"],
    "r": ["programming", "statistics"],
    "sql": ["database", "data", "programming"],
    "go": ["programming", "coding", "software"],
    "rust": ["programming", "coding", "software"],
    
    # DSA and algorithms
    "data structures": ["programming", "problem_solving", "algorithms", "coding", "system_design"],
    "data structures & algorithms": ["programming", "problem_solving", "algorithms", "coding", "system_design"],
    "dsa": ["programming", "problem_solving", "algorithms", "coding", "system_design"],
    "algorithms": ["programming", "problem_solving", "coding", "system_design"],
    
    # Data Science / ML skills (DIRECT MATCHES)
    "data science": ["machine learning", "data analysis", "python", "statistics", "analytics", "ml", "ai"],
    "machine learning": ["ml", "ai", "python", "data science", "deep learning"],
    "ml": ["machine learning", "ai", "python", "data science"],
    "ai": ["machine learning", "artificial intelligence", "ml", "data science", "deep learning"],
    "artificial intelligence": ["machine learning", "ai", "ml", "data science"],
    "deep learning": ["machine learning", "ai", "neural networks", "ml"],
    "data analysis": ["analytics", "statistics", "data", "data science"],
    "statistics": ["data analysis", "mathematics", "data science"],
    "data visualization": ["data analysis", "analytics", "data science"],
    
    # Software skills
    "git": ["version control", "software", "development"],
    "docker": ["devops", "cloud", "containerization"],
    "kubernetes": ["devops", "cloud", "containerization"],
    "aws": ["cloud", "cloud_platforms", "devops"],
    "azure": ["cloud", "cloud_platforms", "devops"],
    "gcp": ["cloud", "cloud_platforms", "devops"],
    
    # General skills
    "problem solving": ["analytical thinking", "critical thinking", "algorithms"],
    "communication": ["presentation", "writing", "interpersonal"],
    "leadership": ["management", "team lead", "project management"],
}


class DeterministicScorer:
    """Score careers based on deterministic algorithm with enhanced fuzzy matching."""

    def __init__(self, careers_file: Path = CAREERS_FILE):
        """Load careers taxonomy."""
        with open(careers_file, "r") as f:
            self.careers = json.load(f)
        
        self.normalizer = ProfileNormalizer()
        self.career_by_id = {c["career_id"]: c for c in self.careers}
        
        # Build expanded synonym lookup
        self._build_synonym_lookup()

    def _build_synonym_lookup(self):
        """Build expanded lookup for fuzzy matching."""
        self.interest_expansion = {}
        for key, synonyms in INTEREST_SYNONYMS.items():
            key_lower = key.lower()
            self.interest_expansion[key_lower] = set(s.lower() for s in synonyms)
            self.interest_expansion[key_lower].add(key_lower)
            # Add reverse mappings
            for syn in synonyms:
                syn_lower = syn.lower()
                if syn_lower not in self.interest_expansion:
                    self.interest_expansion[syn_lower] = set()
                self.interest_expansion[syn_lower].add(key_lower)
        
        # Build skill synonym lookup
        self.skill_expansion = {}
        for key, synonyms in SKILL_SYNONYMS.items():
            key_lower = key.lower()
            self.skill_expansion[key_lower] = set(s.lower() for s in synonyms)
            self.skill_expansion[key_lower].add(key_lower)
            for syn in synonyms:
                syn_lower = syn.lower()
                if syn_lower not in self.skill_expansion:
                    self.skill_expansion[syn_lower] = set()
                self.skill_expansion[syn_lower].add(key_lower)

    def _get_expanded_skills(self, skill: str) -> Set[str]:
        """Get expanded set of related skills."""
        skill_lower = skill.lower().strip().replace("_", " ")
        expanded = {skill_lower}
        
        # Add direct synonyms from skill expansion
        if skill_lower in self.skill_expansion:
            expanded.update(self.skill_expansion[skill_lower])
        
        # Check partial matches
        for key, synonyms in SKILL_SYNONYMS.items():
            key_lower = key.lower()
            if skill_lower in key_lower or key_lower in skill_lower:
                expanded.add(key_lower)
                expanded.update(s.lower() for s in synonyms)
        
        # Also check interest expansion for skills like "technology"
        if skill_lower in self.interest_expansion:
            expanded.update(self.interest_expansion[skill_lower])
        
        return expanded

    def _get_expanded_terms(self, term: str) -> Set[str]:
        """Get expanded set of related terms for fuzzy matching."""
        term_lower = term.lower().strip()
        expanded = {term_lower}
        
        # Add direct synonyms
        if term_lower in self.interest_expansion:
            expanded.update(self.interest_expansion[term_lower])
        
        # Check for partial matches
        for key, synonyms in self.interest_expansion.items():
            if term_lower in key or key in term_lower:
                expanded.add(key)
                expanded.update(synonyms)
            for syn in synonyms:
                if term_lower in syn or syn in term_lower:
                    expanded.add(key)
                    expanded.update(synonyms)
                    break
        
        return expanded

    def _fuzzy_match_score(self, user_terms: List[str], career_terms: List[str]) -> float:
        """Compute fuzzy match score using semantic expansion."""
        if not career_terms:
            return 0.5
        if not user_terms:
            return 0.0
        
        # Expand user terms
        user_expanded = set()
        for term in user_terms:
            user_expanded.update(self._get_expanded_terms(term))
        
        # Expand career terms
        career_expanded = set()
        for term in career_terms:
            career_expanded.update(self._get_expanded_terms(term.lower()))
        
        # Direct matches
        direct_overlap = len(set(t.lower() for t in user_terms) & set(t.lower() for t in career_terms))
        
        # Expanded matches
        expanded_overlap = len(user_expanded & career_expanded)
        
        # Combined score: direct matches weighted higher
        if direct_overlap > 0:
            direct_score = min(direct_overlap / len(career_terms), 1.0)
        else:
            direct_score = 0.0
        
        if expanded_overlap > 0:
            expanded_score = min(expanded_overlap / (len(career_expanded) + 1), 1.0)
        else:
            expanded_score = 0.0
        
        # Weight: 60% direct, 40% expanded
        final_score = 0.6 * direct_score + 0.4 * expanded_score
        return min(final_score, 1.0)

    def compute_skill_score(
        self,
        user_skills: List[str],
        required_skills: List[str],
        preferred_skills: List[str]
    ) -> float:
        """
        Compute skill match score with ENHANCED fuzzy matching.
        Properly matches Python -> programming, DSA -> algorithms, etc.
        - Required skills weighted 60%
        - Preferred skills weighted 40%
        """
        if not user_skills:
            return 0.3  # Base score for no skills (allow interest-based matching)
        
        # Normalize user skills
        user_skill_set = set()
        for s in user_skills:
            normalized = s.lower().strip().replace("_", " ")
            user_skill_set.add(normalized)
        
        # Normalize required/preferred skills
        required_set = set(s.lower().replace("_", " ").strip() for s in required_skills)
        preferred_set = set(s.lower().replace("_", " ").strip() for s in preferred_skills)

        # Direct match count
        required_direct = len(user_skill_set & required_set)
        preferred_direct = len(user_skill_set & preferred_set)
        
        # ENHANCED: Expand user skills using skill synonyms
        user_expanded = set()
        for skill in user_skills:
            user_expanded.update(self._get_expanded_skills(skill))
        
        # Expand required skills
        required_expanded = set()
        for skill in required_skills:
            required_expanded.update(self._get_expanded_skills(skill))
        
        # Expand preferred skills
        preferred_expanded = set()
        for skill in preferred_skills:
            preferred_expanded.update(self._get_expanded_skills(skill))
        
        # Count expanded matches (skill-to-skill mapping)
        required_fuzzy = len(user_expanded & required_expanded)
        preferred_fuzzy = len(user_expanded & preferred_expanded)
        
        # Check for STRONG matches (user skill expands to career required skill)
        strong_matches = 0
        for user_skill in user_skills:
            user_exp = self._get_expanded_skills(user_skill)
            for req_skill in required_skills:
                req_normalized = req_skill.lower().replace("_", " ")
                if req_normalized in user_exp:
                    strong_matches += 1
        
        # Calculate scores with higher weight for strong matches
        if required_set:
            # Strong matches count double
            required_score = min((required_direct * 1.0 + strong_matches * 0.8 + required_fuzzy * 0.2) / len(required_set), 1.0)
        else:
            required_score = 0.5
        
        if preferred_set:
            preferred_score = min((preferred_direct * 1.0 + preferred_fuzzy * 0.3) / len(preferred_set), 1.0)
        else:
            preferred_score = 0.5

        skill_score = 0.6 * required_score + 0.4 * preferred_score
        return min(skill_score, 1.0)

    def compute_interest_score(
        self,
        user_interests: List[str],
        career_interests: List[str]
    ) -> float:
        """Compute interest alignment score with ENHANCED semantic fuzzy matching."""
        if not career_interests:
            return 0.5
        if not user_interests:
            return 0.0
        
        # Normalize interests
        user_normalized = [i.lower().strip().replace("_", " ") for i in user_interests]
        career_normalized = [i.lower().strip().replace("_", " ") for i in career_interests]
        
        # Direct matches
        direct_matches = 0
        for u_int in user_normalized:
            for c_int in career_normalized:
                if u_int == c_int or u_int in c_int or c_int in u_int:
                    direct_matches += 1
                    break
        
        # Expanded matches using synonyms
        user_expanded = set()
        for interest in user_interests:
            user_expanded.update(self._get_expanded_terms(interest))
        
        career_expanded = set()
        for interest in career_interests:
            career_expanded.update(self._get_expanded_terms(interest.replace("_", " ")))
        
        expanded_overlap = len(user_expanded & career_expanded)
        
        # Calculate score
        if direct_matches > 0:
            direct_score = min(direct_matches / len(career_interests), 1.0)
        else:
            direct_score = 0.0
        
        if expanded_overlap > 0:
            expanded_score = min(expanded_overlap / (len(career_expanded) / 2 + 1), 1.0)
        else:
            expanded_score = 0.0
        
        # Weight: 50% direct, 50% expanded (interests benefit more from semantic matching)
        final_score = 0.5 * direct_score + 0.5 * expanded_score
        return min(final_score, 1.0)

    def compute_education_score(
        self,
        user_degree: str,
        prerequisites: List[str],
        career: Dict = None
    ) -> float:
        """Compute education prerequisite satisfaction with category awareness."""
        degree_map = {
            "10th": 1,
            "12th": 2,
            "diploma": 2.5,
            "bachelor's": 3,
            "bachelors": 3,
            "bachelor": 3,
            "master's": 4,
            "masters": 4,
            "master": 4,
            "phd": 5,
            "doctorate": 5
        }
        
        user_level = degree_map.get(user_degree.lower().strip(), 2)
        
        # Check career category for field matching
        field_bonus = 0.0
        if career:
            category = career.get("category", "").lower()
            title = career.get("title", "").lower()
            
            # Add bonus if user's education field aligns with career
            # This helps match healthcare students to healthcare careers, etc.
            if "healthcare" in category or "medicine" in category:
                if user_level >= 3:  # Bachelor's or higher
                    field_bonus = 0.1
            elif "legal" in category or "law" in category:
                if user_level >= 3:
                    field_bonus = 0.1
            elif "technology" in category or "engineering" in category:
                if user_level >= 3:
                    field_bonus = 0.1
        
        if not prerequisites:
            base_score = 0.7 + field_bonus
            return min(base_score, 1.0)
        
        prereq_text = " ".join(prerequisites).lower()
        
        # Heuristics for education level requirements
        if "phd" in prereq_text or "doctorate" in prereq_text:
            base_score = 1.0 if user_level >= 5 else (0.5 if user_level >= 4 else 0.3)
        elif "master" in prereq_text or "mbbs" in prereq_text or "md" in prereq_text:
            base_score = 1.0 if user_level >= 4 else (0.6 if user_level >= 3 else 0.4)
        elif "bachelor" in prereq_text or "degree" in prereq_text or "graduate" in prereq_text:
            base_score = 1.0 if user_level >= 3 else (0.6 if user_level >= 2 else 0.4)
        elif "diploma" in prereq_text or "certification" in prereq_text:
            base_score = 1.0 if user_level >= 2.5 else 0.6
        elif "experience" in prereq_text or "years" in prereq_text:
            base_score = 0.6 if user_level >= 3 else 0.4
        else:
            base_score = 0.7
        
        return min(base_score + field_bonus, 1.0)

    def compute_market_score(
        self,
        user_interests: List[str],
        career_keywords: List[str],
        career: Dict = None
    ) -> float:
        """Compute market demand score with category and trend awareness."""
        base_score = 0.5
        
        # Check career growth rating
        if career:
            growth = career.get("growth", "medium").lower()
            if growth == "very high":
                base_score = 0.8
            elif growth == "high":
                base_score = 0.7
            elif growth == "medium":
                base_score = 0.5
            else:
                base_score = 0.4
        
        # Add bonus for keyword matching
        if user_interests and career_keywords:
            user_set = set(u.lower() for u in user_interests)
            keyword_set = set(k.lower().replace("_", " ") for k in career_keywords)
            
            # Also check career title
            if career:
                title_words = set(career.get("title", "").lower().split())
                keyword_set.update(title_words)
                category_words = set(career.get("category", "").lower().replace("-", " ").split())
                keyword_set.update(category_words)
            
            # Direct matches
            direct_overlap = len(user_set & keyword_set)
            
            # Fuzzy matches
            user_expanded = set()
            for interest in user_interests:
                user_expanded.update(self._get_expanded_terms(interest))
            
            expanded_overlap = len(user_expanded & keyword_set)
            
            if direct_overlap > 0:
                base_score += min(0.2, direct_overlap * 0.05)
            if expanded_overlap > 0:
                base_score += min(0.1, expanded_overlap * 0.02)
        
        return min(base_score, 1.0)

    def score_career(
        self,
        career: Dict,
        user_skills: List[str],
        user_interests: List[str],
        user_degree: str
    ) -> Tuple[float, ScoreBreakdown]:
        """
        Compute BALANCED score for a single career.
        All careers scored fairly based on profile match.
        
        Returns: (final_score, breakdown)
        """
        skill_score = self.compute_skill_score(
            user_skills,
            career.get("required_skills", []),
            career.get("preferred_skills", [])
        )
        
        interest_score = self.compute_interest_score(
            user_interests,
            career.get("interests", [])
        )
        
        education_score = self.compute_education_score(
            user_degree,
            career.get("prerequisites", career.get("entry_points", [])),
            career
        )
        
        market_score = self.compute_market_score(
            user_interests,
            career.get("keywords", []),
            career
        )
        
        # === INTEREST-FIRST SCORING ===
        # User's stated interest is the PRIMARY factor
        # If user says "Law", they should get legal careers, NOT tech careers
        
        category = career.get("category", "").lower()
        title = career.get("title", "").lower()
        user_interest_lower = [i.lower().strip() for i in user_interests]
        user_interest_joined = " ".join(user_interest_lower)
        
        # === DEFINE CAREER CATEGORIES ===
        tech_keywords = {"technology", "software", "data", "ai", "machine learning", 
                        "programming", "coding", "developer", "tech", "data science",
                        "cloud", "devops", "cybersecurity"}
        
        law_keywords = {"law", "legal", "lawyer", "advocate", "attorney", "justice",
                       "court", "litigation", "paralegal"}
        
        healthcare_keywords = {"healthcare", "medical", "medicine", "doctor", "nurse",
                              "hospital", "health", "clinical", "patient care"}
        
        education_keywords = {"education", "teaching", "teacher", "professor", "academic",
                             "school", "training", "instructor"}
        
        finance_keywords = {"finance", "banking", "investment", "accounting", "financial",
                           "economics", "trading", "wealth"}
        
        creative_keywords = {"art", "design", "creative", "music", "fashion", "media",
                            "photography", "film", "writing", "content"}
        
        engineering_keywords = {"engineering", "engineer", "mechanical", "civil", "electrical",
                               "automobile", "aerospace", "chemical"}
        
        social_keywords = {"social work", "counseling", "psychology", "helping people",
                          "community", "advocacy", "nonprofit", "ngo"}
        
        # === DETECT USER'S INTEREST CATEGORY ===
        user_wants_tech = any(kw in user_interest_joined for kw in tech_keywords)
        user_wants_law = any(kw in user_interest_joined for kw in law_keywords)
        user_wants_healthcare = any(kw in user_interest_joined for kw in healthcare_keywords)
        user_wants_education = any(kw in user_interest_joined for kw in education_keywords)
        user_wants_finance = any(kw in user_interest_joined for kw in finance_keywords)
        user_wants_creative = any(kw in user_interest_joined for kw in creative_keywords)
        user_wants_engineering = any(kw in user_interest_joined for kw in engineering_keywords)
        user_wants_social = any(kw in user_interest_joined for kw in social_keywords)
        
        # === DETECT CAREER CATEGORY ===
        is_tech_career = any(kw in category or kw in title for kw in tech_keywords)
        is_law_career = any(kw in category or kw in title for kw in law_keywords)
        is_healthcare_career = any(kw in category or kw in title for kw in healthcare_keywords)
        is_education_career = any(kw in category or kw in title for kw in education_keywords)
        is_finance_career = any(kw in category or kw in title for kw in finance_keywords)
        is_creative_career = any(kw in category or kw in title for kw in creative_keywords)
        is_engineering_career = any(kw in category or kw in title for kw in engineering_keywords)
        is_social_career = any(kw in category or kw in title for kw in social_keywords)
        
        # === CALCULATE CATEGORY MATCH ===
        category_match = False
        category_mismatch = False
        
        if user_wants_law:
            category_match = is_law_career or is_social_career
            category_mismatch = is_tech_career or is_engineering_career
        elif user_wants_tech:
            category_match = is_tech_career
            category_mismatch = is_law_career or is_healthcare_career or is_education_career
        elif user_wants_healthcare:
            category_match = is_healthcare_career
            category_mismatch = is_tech_career or is_law_career or is_engineering_career
        elif user_wants_education:
            category_match = is_education_career
            category_mismatch = is_tech_career or is_engineering_career
        elif user_wants_finance:
            category_match = is_finance_career
            category_mismatch = is_tech_career or is_healthcare_career
        elif user_wants_creative:
            category_match = is_creative_career
            category_mismatch = is_tech_career or is_engineering_career
        elif user_wants_engineering:
            category_match = is_engineering_career
            category_mismatch = is_law_career or is_healthcare_career
        elif user_wants_social:
            category_match = is_social_career or is_law_career or is_education_career
            category_mismatch = is_tech_career or is_engineering_career
        
        # === BASE SCORE CALCULATION ===
        # Interest match is now the PRIMARY factor (40%)
        weighted_score = (
            0.40 * interest_score +   # Interest is MOST important
            0.30 * skill_score +      # Skills second
            0.15 * market_score +     # Market third
            0.15 * education_score    # Education fourth
        )
        
        # Scale to 40-90% range
        final_score = 0.40 + (weighted_score * 0.50)
        
        # === CATEGORY MATCHING BONUSES/PENALTIES ===
        if category_match:
            final_score += 0.20  # +20% for matching user's interest category
            logger.debug(f"  ✅ {title}: +20% (category match)")
        
        if category_mismatch:
            final_score -= 0.30  # -30% for completely wrong category
            logger.debug(f"  ❌ {title}: -30% (category mismatch)")
        
        # CRITICAL: Penalize careers with ZERO interest alignment
        if interest_score < 0.10:
            final_score -= 0.15  # Heavy penalty for no interest match
            logger.debug(f"  ⚠️ {title}: -15% (zero interest match)")
        
        # Bonus for high skill + interest alignment
        if skill_score >= 0.5 and interest_score >= 0.4:
            final_score += 0.05  # Both skills and interests align
        
        # Cap the score
        final_score = min(0.95, max(0.30, final_score))
        
        breakdown = ScoreBreakdown(
            skill_match=round(skill_score, 3),
            interest_match=round(interest_score, 3),
            education_match=round(education_score, 3),
            market_demand=round(market_score, 3),
            penalty=0.0
        )
        
        return round(final_score, 3), breakdown

    def rank_careers(
        self,
        user_skills: List[str],
        user_interests: List[str],
        user_degree: str,
        top_n: int = 5
    ) -> List[Tuple[Dict, float, ScoreBreakdown]]:
        """
        Rank all careers and return top N with diversity.
        Includes detailed logging for debugging.
        """
        logger.info("=" * 60)
        logger.info("🚀 CAREER RANKING ENGINE STARTED")
        logger.info("=" * 60)
        logger.info(f"📋 User Profile:")
        logger.info(f"   Skills: {user_skills}")
        logger.info(f"   Interests: {user_interests}")
        logger.info(f"   Education: {user_degree}")
        logger.info("-" * 60)
        
        scored_careers = []
        
        logger.info(f"📊 Scoring {len(self.careers)} careers...")
        
        for career in self.careers:
            score, breakdown = self.score_career(
                career,
                user_skills,
                user_interests,
                user_degree
            )
            scored_careers.append((career, score, breakdown))
        
        # Sort by score descending
        scored_careers.sort(key=lambda x: x[1], reverse=True)
        
        logger.info("-" * 60)
        logger.info("🏆 TOP 10 SCORED CAREERS:")
        for i, (career, score, bd) in enumerate(scored_careers[:10], 1):
            logger.info(f"   {i:2}. {career['title']:25} | Score: {score:.1%} | Skill: {bd.skill_match:.1%} | Interest: {bd.interest_match:.1%}")
        
        # Ensure category diversity in top results
        selected = []
        categories_seen = {}
        
        for career, score, breakdown in scored_careers:
            category = career.get("category", "Unknown").split(" - ")[0]
            
            # Allow max 3 from same main category in top 5 (increased for tech users)
            if categories_seen.get(category, 0) < 3:
                selected.append((career, score, breakdown))
                categories_seen[category] = categories_seen.get(category, 0) + 1
                
                if len(selected) >= top_n:
                    break
        
        # If we don't have enough, fill from remaining
        if len(selected) < top_n:
            for career, score, breakdown in scored_careers:
                if (career, score, breakdown) not in selected:
                    selected.append((career, score, breakdown))
                    if len(selected) >= top_n:
                        break
        
        logger.info("-" * 60)
        logger.info(f"✅ FINAL RECOMMENDATIONS (Top {top_n}):")
        for i, (career, score, bd) in enumerate(selected[:top_n], 1):
            logger.info(f"   #{i} {career['title']} - {score:.1%} match")
        logger.info("=" * 60)
        
        return selected[:top_n]

    def generate_skill_gaps(
        self,
        user_skills: List[str],
        required_skills: List[str]
    ) -> List[SkillGap]:
        """Generate skill gaps for a career."""
        user_set = set(user_skills)
        required_set = set(s.lower() for s in required_skills)
        
        gaps = required_set - user_set
        
        # Assign priorities
        skill_gaps = []
        for i, skill in enumerate(sorted(gaps)):
            priority = "high" if i < 2 else "med" if i < 4 else "low"
            skill_gaps.append(
                SkillGap(
                    skill=skill,
                    reason=f"Required skill for this role",
                    priority=priority
                )
            )
        
        return skill_gaps[:5]  # Top 5 gaps

    def generate_roadmap(self, career: Dict) -> List[RoadmapStep]:
        """Generate a basic roadmap for career transition."""
        difficulty = career.get("difficulty", 2)
        
        steps = []
        
        if difficulty <= 2:
            steps = [
                RoadmapStep(
                    step="Learn foundational concepts",
                    duration="2-4 months",
                    resources=["Online courses", "YouTube tutorials", "Certifications"],
                    projects=["Personal projects", "Mini hackathons", "Side projects"]
                ),
                RoadmapStep(
                    step="Build portfolio with real projects",
                    duration="2-3 months",
                    resources=["Github", "Portfolio website", "Behance/Dribbble"],
                    projects=["2-3 end-to-end projects", "Case studies"]
                ),
                RoadmapStep(
                    step="Apply for entry-level positions",
                    duration="1-3 months",
                    resources=["LinkedIn", "Job boards", "Networking events"],
                    projects=["Open-source contributions", "Freelance work"]
                )
            ]
        elif difficulty <= 3:
            steps = [
                RoadmapStep(
                    step="Master core technical skills",
                    duration="4-6 months",
                    resources=["Advanced courses", "Books", "Industry certifications"],
                    projects=["Complex projects", "System design exercises"]
                ),
                RoadmapStep(
                    step="Gain hands-on production experience",
                    duration="3-6 months",
                    resources=["Internships", "Contract work", "Bootcamps"],
                    projects=["Real-world systems", "Scalable solutions"]
                ),
                RoadmapStep(
                    step="Develop professional expertise",
                    duration="6-12 months",
                    resources=["Advanced certifications", "Mentorship", "Conference talks"],
                    projects=["Leadership roles", "Tool/library development"]
                ),
                RoadmapStep(
                    step="Prepare for senior positions",
                    duration="2-3 months",
                    resources=["Interview prep", "Leadership training", "Networking"],
                    projects=["Mentoring others", "Architecture design"]
                )
            ]
        else:
            steps = [
                RoadmapStep(
                    step="Build deep expertise and specialization",
                    duration="12+ months",
                    resources=["PhD/Research", "Advanced roles", "Expert networks"],
                    projects=["Novel research", "Patent development", "Innovation labs"]
                ),
                RoadmapStep(
                    step="Publish and present findings",
                    duration="Ongoing",
                    resources=["Conferences", "Journals", "Speaking engagements"],
                    projects=["Academic papers", "Industry thought leadership"]
                ),
                RoadmapStep(
                    step="Lead transformational initiatives",
                    duration="Ongoing",
                    resources=["C-level roles", "Board positions", "Startup founding"],
                    projects=["Strategy", "Innovation", "Team building"]
                )
            ]
        
        return steps
