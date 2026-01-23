"""
Internet Fetcher Module for Career Data
Fetches real-time career information, salary data, and job market insights.
Supports India and USA salary data.
"""
import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# Comprehensive salary data for India and USA (2026 estimates)
SALARY_DATABASE = {
    "software_engineer": {
        "usa": {"min": 85000, "max": 200000, "avg": 130000, "currency": "USD"},
        "india": {"min": 600000, "max": 4000000, "avg": 1800000, "currency": "INR"},
        "growth": "25% annually", "demand": "Very High"
    },
    "data_scientist": {
        "usa": {"min": 95000, "max": 200000, "avg": 140000, "currency": "USD"},
        "india": {"min": 700000, "max": 4500000, "avg": 2000000, "currency": "INR"},
        "growth": "30% annually", "demand": "Very High"
    },
    "registered_nurse": {
        "usa": {"min": 60000, "max": 120000, "avg": 85000, "currency": "USD"},
        "india": {"min": 250000, "max": 800000, "avg": 450000, "currency": "INR"},
        "growth": "15% annually", "demand": "High"
    },
    "surgeon": {
        "usa": {"min": 300000, "max": 600000, "avg": 420000, "currency": "USD"},
        "india": {"min": 1500000, "max": 8000000, "avg": 4000000, "currency": "INR"},
        "growth": "8% annually", "demand": "High"
    },
    "general_practitioner": {
        "usa": {"min": 180000, "max": 280000, "avg": 220000, "currency": "USD"},
        "india": {"min": 800000, "max": 3000000, "avg": 1500000, "currency": "INR"},
        "growth": "10% annually", "demand": "High"
    },
    "pharmacist": {
        "usa": {"min": 100000, "max": 160000, "avg": 128000, "currency": "USD"},
        "india": {"min": 300000, "max": 1200000, "avg": 600000, "currency": "INR"},
        "growth": "5% annually", "demand": "Moderate"
    },
    "lawyer": {
        "usa": {"min": 80000, "max": 300000, "avg": 150000, "currency": "USD"},
        "india": {"min": 500000, "max": 5000000, "avg": 1500000, "currency": "INR"},
        "growth": "8% annually", "demand": "Moderate"
    },
    "judge": {
        "usa": {"min": 120000, "max": 220000, "avg": 160000, "currency": "USD"},
        "india": {"min": 1000000, "max": 3000000, "avg": 1800000, "currency": "INR"},
        "growth": "3% annually", "demand": "Stable"
    },
    "financial_analyst": {
        "usa": {"min": 65000, "max": 150000, "avg": 95000, "currency": "USD"},
        "india": {"min": 500000, "max": 2500000, "avg": 1200000, "currency": "INR"},
        "growth": "12% annually", "demand": "High"
    },
    "accountant": {
        "usa": {"min": 55000, "max": 120000, "avg": 78000, "currency": "USD"},
        "india": {"min": 300000, "max": 1500000, "avg": 700000, "currency": "INR"},
        "growth": "6% annually", "demand": "Stable"
    },
    "mba_consultant": {
        "usa": {"min": 90000, "max": 250000, "avg": 150000, "currency": "USD"},
        "india": {"min": 1200000, "max": 6000000, "avg": 2500000, "currency": "INR"},
        "growth": "10% annually", "demand": "High"
    },
    "marketing_manager": {
        "usa": {"min": 70000, "max": 180000, "avg": 115000, "currency": "USD"},
        "india": {"min": 600000, "max": 3000000, "avg": 1400000, "currency": "INR"},
        "growth": "10% annually", "demand": "High"
    },
    "civil_engineer": {
        "usa": {"min": 65000, "max": 130000, "avg": 90000, "currency": "USD"},
        "india": {"min": 400000, "max": 1800000, "avg": 800000, "currency": "INR"},
        "growth": "8% annually", "demand": "Moderate"
    },
    "mechanical_engineer": {
        "usa": {"min": 65000, "max": 130000, "avg": 92000, "currency": "USD"},
        "india": {"min": 400000, "max": 1600000, "avg": 750000, "currency": "INR"},
        "growth": "7% annually", "demand": "Moderate"
    },
    "electrical_engineer": {
        "usa": {"min": 70000, "max": 140000, "avg": 100000, "currency": "USD"},
        "india": {"min": 450000, "max": 2000000, "avg": 900000, "currency": "INR"},
        "growth": "9% annually", "demand": "High"
    },
    "automobile_engineer": {
        "usa": {"min": 70000, "max": 160000, "avg": 105000, "currency": "USD"},
        "india": {"min": 500000, "max": 2500000, "avg": 1000000, "currency": "INR"},
        "growth": "15% annually", "demand": "Very High"
    },
    "architect": {
        "usa": {"min": 60000, "max": 150000, "avg": 95000, "currency": "USD"},
        "india": {"min": 400000, "max": 2000000, "avg": 900000, "currency": "INR"},
        "growth": "5% annually", "demand": "Moderate"
    },
    "interior_designer": {
        "usa": {"min": 45000, "max": 100000, "avg": 65000, "currency": "USD"},
        "india": {"min": 300000, "max": 1500000, "avg": 600000, "currency": "INR"},
        "growth": "8% annually", "demand": "Moderate"
    },
    "graphic_designer": {
        "usa": {"min": 45000, "max": 95000, "avg": 60000, "currency": "USD"},
        "india": {"min": 250000, "max": 1200000, "avg": 500000, "currency": "INR"},
        "growth": "5% annually", "demand": "Moderate"
    },
    "teacher": {
        "usa": {"min": 45000, "max": 85000, "avg": 62000, "currency": "USD"},
        "india": {"min": 200000, "max": 800000, "avg": 400000, "currency": "INR"},
        "growth": "5% annually", "demand": "Stable"
    },
    "agricultural_scientist": {
        "usa": {"min": 55000, "max": 110000, "avg": 75000, "currency": "USD"},
        "india": {"min": 400000, "max": 1500000, "avg": 700000, "currency": "INR"},
        "growth": "10% annually", "demand": "Growing"
    },
    "agricultural_farmer": {
        "usa": {"min": 30000, "max": 150000, "avg": 70000, "currency": "USD"},
        "india": {"min": 150000, "max": 1000000, "avg": 400000, "currency": "INR"},
        "growth": "5% annually", "demand": "Stable"
    },
    "veterinarian": {
        "usa": {"min": 80000, "max": 180000, "avg": 110000, "currency": "USD"},
        "india": {"min": 400000, "max": 1500000, "avg": 700000, "currency": "INR"},
        "growth": "12% annually", "demand": "High"
    },
    "environmental_scientist": {
        "usa": {"min": 55000, "max": 120000, "avg": 78000, "currency": "USD"},
        "india": {"min": 400000, "max": 1400000, "avg": 650000, "currency": "INR"},
        "growth": "15% annually", "demand": "Growing"
    },
    "psychiatrist": {
        "usa": {"min": 200000, "max": 350000, "avg": 260000, "currency": "USD"},
        "india": {"min": 1200000, "max": 4000000, "avg": 2200000, "currency": "INR"},
        "growth": "15% annually", "demand": "Very High"
    },
    "cloud_architect": {
        "usa": {"min": 120000, "max": 220000, "avg": 165000, "currency": "USD"},
        "india": {"min": 1500000, "max": 5000000, "avg": 2800000, "currency": "INR"},
        "growth": "28% annually", "demand": "Very High"
    },
    "devops_engineer": {
        "usa": {"min": 100000, "max": 180000, "avg": 135000, "currency": "USD"},
        "india": {"min": 1000000, "max": 4000000, "avg": 2200000, "currency": "INR"},
        "growth": "25% annually", "demand": "Very High"
    },
    "cybersecurity_analyst": {
        "usa": {"min": 90000, "max": 170000, "avg": 120000, "currency": "USD"},
        "india": {"min": 800000, "max": 3500000, "avg": 1800000, "currency": "INR"},
        "growth": "30% annually", "demand": "Very High"
    },
    "product_manager": {
        "usa": {"min": 100000, "max": 200000, "avg": 145000, "currency": "USD"},
        "india": {"min": 1500000, "max": 5000000, "avg": 2800000, "currency": "INR"},
        "growth": "15% annually", "demand": "High"
    },
    "ux_designer": {
        "usa": {"min": 75000, "max": 150000, "avg": 105000, "currency": "USD"},
        "india": {"min": 600000, "max": 2500000, "avg": 1200000, "currency": "INR"},
        "growth": "18% annually", "demand": "High"
    },
    "ml_engineer": {
        "usa": {"min": 110000, "max": 220000, "avg": 160000, "currency": "USD"},
        "india": {"min": 1200000, "max": 5000000, "avg": 2500000, "currency": "INR"},
        "growth": "35% annually", "demand": "Very High"
    },
    "biomedical_engineer": {
        "usa": {"min": 70000, "max": 140000, "avg": 98000, "currency": "USD"},
        "india": {"min": 500000, "max": 2000000, "avg": 900000, "currency": "INR"},
        "growth": "12% annually", "demand": "High"
    },
    "renewable_energy_engineer": {
        "usa": {"min": 75000, "max": 150000, "avg": 105000, "currency": "USD"},
        "india": {"min": 600000, "max": 2200000, "avg": 1100000, "currency": "INR"},
        "growth": "20% annually", "demand": "Very High"
    },
    "economist": {
        "usa": {"min": 75000, "max": 180000, "avg": 115000, "currency": "USD"},
        "india": {"min": 600000, "max": 2500000, "avg": 1200000, "currency": "INR"},
        "growth": "8% annually", "demand": "Moderate"
    },
    "police_officer": {
        "usa": {"min": 45000, "max": 100000, "avg": 65000, "currency": "USD"},
        "india": {"min": 300000, "max": 800000, "avg": 500000, "currency": "INR"},
        "growth": "5% annually", "demand": "Stable"
    },
    "sales_executive": {
        "usa": {"min": 50000, "max": 200000, "avg": 95000, "currency": "USD"},
        "india": {"min": 400000, "max": 2500000, "avg": 1000000, "currency": "INR"},
        "growth": "8% annually", "demand": "Stable"
    },
}

# Career path information
CAREER_PATHS = {
    "software_engineer": {
        "entry_level": "Junior Developer / Software Engineer I",
        "mid_level": "Software Engineer II / Senior Developer",
        "senior_level": "Staff Engineer / Tech Lead",
        "leadership": "Engineering Manager / Principal Engineer",
        "executive": "VP of Engineering / CTO",
        "timeline": "Entry → Mid (2-3 yrs) → Senior (3-5 yrs) → Lead (5-8 yrs) → Executive (10+ yrs)",
        "skills_progression": [
            "Year 1-2: Master core programming, version control, testing",
            "Year 3-4: System design, code review, mentoring juniors",
            "Year 5-7: Architecture, cross-team collaboration, technical decisions",
            "Year 8+: Strategy, organization-wide impact, thought leadership"
        ],
        "certifications": ["AWS Certified", "Google Cloud Professional", "Kubernetes Certified"]
    },
    "data_scientist": {
        "entry_level": "Junior Data Analyst / Data Scientist I",
        "mid_level": "Data Scientist II / Senior Data Scientist",
        "senior_level": "Lead Data Scientist / Principal Data Scientist",
        "leadership": "Data Science Manager / Head of Analytics",
        "executive": "Chief Data Officer / VP of Data",
        "timeline": "Entry → Mid (2-3 yrs) → Senior (3-5 yrs) → Lead (5-8 yrs) → Executive (10+ yrs)",
        "skills_progression": [
            "Year 1-2: Python/R, SQL, statistics, basic ML",
            "Year 3-4: Advanced ML, deep learning, A/B testing",
            "Year 5-7: MLOps, model deployment, cross-functional leadership",
            "Year 8+: Strategy, research direction, business impact"
        ],
        "certifications": ["Google Data Analytics", "AWS ML Specialty", "TensorFlow Developer"]
    },
    "registered_nurse": {
        "entry_level": "Staff Nurse / RN I",
        "mid_level": "Senior Nurse / Charge Nurse",
        "senior_level": "Nurse Manager / Clinical Nurse Specialist",
        "leadership": "Director of Nursing / Nurse Executive",
        "executive": "Chief Nursing Officer (CNO)",
        "timeline": "Entry → Senior (3-5 yrs) → Manager (5-8 yrs) → Director (10+ yrs) → CNO (15+ yrs)",
        "skills_progression": [
            "Year 1-3: Clinical skills, patient care, protocols",
            "Year 4-6: Specialization, leadership, mentoring",
            "Year 7-10: Management, policy, quality improvement",
            "Year 10+: Executive leadership, strategy, advocacy"
        ],
        "certifications": ["CCRN", "Nurse Practitioner", "Specialty Certifications"]
    },
    "lawyer": {
        "entry_level": "Associate Attorney / Junior Counsel",
        "mid_level": "Senior Associate / Counsel",
        "senior_level": "Partner / Of Counsel",
        "leadership": "Managing Partner / General Counsel",
        "executive": "Chief Legal Officer / Judge",
        "timeline": "Associate (5-7 yrs) → Senior (3-5 yrs) → Partner (5-10 yrs) → Managing Partner",
        "skills_progression": [
            "Year 1-3: Legal research, drafting, court appearances",
            "Year 4-7: Case management, client relations, specialization",
            "Year 8-12: Business development, mentoring, firm leadership",
            "Year 12+: Strategic direction, thought leadership"
        ],
        "certifications": ["Bar Admission", "Specialization Certificates", "Mediation/Arbitration"]
    },
    "financial_analyst": {
        "entry_level": "Junior Analyst / Financial Analyst I",
        "mid_level": "Senior Analyst / Financial Analyst II",
        "senior_level": "Lead Analyst / Finance Manager",
        "leadership": "Director of Finance / VP Finance",
        "executive": "Chief Financial Officer (CFO)",
        "timeline": "Analyst (2-3 yrs) → Senior (3-4 yrs) → Manager (4-6 yrs) → Director (8+ yrs)",
        "skills_progression": [
            "Year 1-2: Financial modeling, Excel, reporting",
            "Year 3-5: Valuation, M&A support, strategic analysis",
            "Year 6-10: Team leadership, board presentations",
            "Year 10+: C-suite advisory, corporate strategy"
        ],
        "certifications": ["CFA", "CPA", "FRM"]
    },
}


class InternetFetcher:
    """Fetch career data from internet and local database."""
    
    def __init__(self):
        self.salary_db = SALARY_DATABASE
        self.career_paths_db = CAREER_PATHS
    
    def get_salary_data(self, career_id: str) -> Dict[str, Any]:
        """Get salary data for India and USA."""
        # Normalize career_id
        career_id_normalized = career_id.lower().replace(" ", "_").replace("-", "_")
        
        # Try exact match first
        if career_id_normalized in self.salary_db:
            return self.salary_db[career_id_normalized]
        
        # Try partial match
        for key in self.salary_db:
            if key in career_id_normalized or career_id_normalized in key:
                return self.salary_db[key]
        
        # Return default estimate
        return {
            "usa": {"min": 50000, "max": 150000, "avg": 85000, "currency": "USD"},
            "india": {"min": 400000, "max": 2000000, "avg": 900000, "currency": "INR"},
            "growth": "Varies", "demand": "Moderate"
        }
    
    def get_career_path(self, career_id: str) -> Dict[str, Any]:
        """Get career progression path."""
        career_id_normalized = career_id.lower().replace(" ", "_").replace("-", "_")
        
        for key in self.career_paths_db:
            if key in career_id_normalized or career_id_normalized in key:
                return self.career_paths_db[key]
        
        # Generic path
        return {
            "entry_level": "Entry-level Position",
            "mid_level": "Mid-level Professional",
            "senior_level": "Senior Professional / Team Lead",
            "leadership": "Manager / Director",
            "executive": "Executive / C-Suite",
            "timeline": "Entry → Mid (2-4 yrs) → Senior (4-7 yrs) → Leadership (8+ yrs)",
            "skills_progression": [
                "Year 1-2: Learn fundamentals and industry practices",
                "Year 3-5: Develop expertise and specialization",
                "Year 6-10: Leadership and strategic thinking",
                "Year 10+: Executive skills and vision"
            ],
            "certifications": ["Industry-specific certifications recommended"]
        }
    
    def format_salary_display(self, career_id: str) -> str:
        """Format salary data for display."""
        data = self.get_salary_data(career_id)
        
        usa = data.get("usa", {})
        india = data.get("india", {})
        
        usa_range = f"${usa.get('min', 0):,} - ${usa.get('max', 0):,} (Avg: ${usa.get('avg', 0):,})"
        india_range = f"₹{india.get('min', 0):,} - ₹{india.get('max', 0):,} (Avg: ₹{india.get('avg', 0):,})"
        
        return f"""
🇺🇸 **USA Salary Range:**
   {usa_range} per year

🇮🇳 **India Salary Range:**
   {india_range} per year

📈 **Growth Rate:** {data.get('growth', 'N/A')}
📊 **Market Demand:** {data.get('demand', 'N/A')}
"""
    
    def format_career_path_display(self, career_id: str) -> str:
        """Format career path for display."""
        path = self.get_career_path(career_id)
        
        result = f"""
🚀 **Career Progression:**

1️⃣ **Entry Level:** {path.get('entry_level', 'Entry Position')}
2️⃣ **Mid Level:** {path.get('mid_level', 'Mid Position')}
3️⃣ **Senior Level:** {path.get('senior_level', 'Senior Position')}
4️⃣ **Leadership:** {path.get('leadership', 'Leadership Role')}
5️⃣ **Executive:** {path.get('executive', 'Executive Role')}

⏱️ **Timeline:** {path.get('timeline', 'Varies by individual')}

📚 **Skills Progression:**
"""
        for skill in path.get('skills_progression', []):
            result += f"• {skill}\n"
        
        result += f"\n🏆 **Recommended Certifications:**\n"
        for cert in path.get('certifications', []):
            result += f"• {cert}\n"
        
        return result
    
    def fetch_from_web(self, query: str) -> Optional[str]:
        """
        Attempt to fetch career information from the web.
        Uses DuckDuckGo Instant Answer API (no auth required).
        """
        try:
            # DuckDuckGo Instant Answer API
            url = f"https://api.duckduckgo.com/?q={query}+career+salary&format=json&no_html=1"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                abstract = data.get("AbstractText", "")
                if abstract:
                    return abstract[:500]  # Limit length
            return None
        except Exception as e:
            logger.warning(f"Web fetch failed: {e}")
            return None
    
    def get_comprehensive_career_info(self, career_title: str, career_id: str) -> Dict[str, Any]:
        """Get comprehensive career information including salaries and paths."""
        salary_data = self.get_salary_data(career_id)
        career_path = self.get_career_path(career_id)
        
        # Try to fetch additional info from web
        web_info = self.fetch_from_web(career_title)
        
        return {
            "salary": salary_data,
            "career_path": career_path,
            "salary_display": self.format_salary_display(career_id),
            "path_display": self.format_career_path_display(career_id),
            "web_info": web_info
        }


# Singleton instance
_fetcher = None

def get_fetcher() -> InternetFetcher:
    """Get singleton instance of InternetFetcher."""
    global _fetcher
    if _fetcher is None:
        _fetcher = InternetFetcher()
    return _fetcher
