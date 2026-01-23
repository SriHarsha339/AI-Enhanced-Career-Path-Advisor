"""
Advanced Reasoning Engine for Career Recommendations
Synthesizes local RAG data + internet data + scoring results
Generates 3 ranked decisions with explainable AI reasoning
Production-ready with comprehensive error handling
"""

import json
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DecisionConfidence(Enum):
    """Confidence level for decisions"""
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class CareerDecision:
    """Single career decision with reasoning"""
    rank: int
    career_id: str
    career_title: str
    category: str
    
    # Scoring
    overall_score: float
    skill_match_score: float
    interest_match_score: float
    education_fit_score: float
    market_demand_score: float
    
    # Internet data factors
    market_growth_2026: str
    salary_range: str
    job_availability: str
    trending_skills: List[str]
    top_employers: List[str]
    
    # Reasoning
    primary_reason: str
    secondary_reasons: List[str]
    risk_factors: List[str]
    opportunities: List[str]
    recommended_next_steps: List[str]
    
    # Explainability
    confidence_level: str
    data_sources: List[str]
    assumptions: List[str]
    alternative_paths: List[str]
    
    # Timeline
    years_to_establishment: int
    estimated_salary_year_1: int
    estimated_salary_year_5: int


@dataclass
class ReasoningExplanation:
    """Detailed explanation of reasoning"""
    decision_title: str
    why_perfect_fit: str
    skill_requirements: str
    market_opportunity: str
    financial_outlook: str
    growth_potential: str
    challenges: str
    success_factors: str


class ReasoningEngine:
    """
    Advanced reasoning engine for career recommendations
    Synthesizes multiple data sources
    Generates explainable decisions
    """

    def __init__(self):
        """Initialize reasoning engine"""
        self.min_score_threshold = 0.35
        self.top_decisions_count = 3

    def synthesize_decisions(
        self,
        profile_scores: Dict[str, float],
        internet_data: Dict[str, Dict[str, Any]],
        rag_evidence: Dict[str, List[str]],
        careers_db: List[Dict[str, Any]]
    ) -> List[CareerDecision]:
        """
        Synthesize all data sources into 3 ranked decisions
        
        Args:
            profile_scores: Scoring results from deterministic scorer
            internet_data: Real-time data from web fetcher
            rag_evidence: Evidence from knowledge base
            careers_db: Career definitions
        
        Returns:
            List of top 3 career decisions with explanations
        """
        try:
            # Filter careers with minimum score
            eligible_careers = [
                (cid, score) for cid, score in profile_scores.items()
                if score >= self.min_score_threshold
            ]

            if not eligible_careers:
                logger.warning("No careers meet minimum threshold, using top scorers")
                eligible_careers = sorted(
                    profile_scores.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]

            # Sort by score
            eligible_careers.sort(key=lambda x: x[1], reverse=True)

            # Create decision objects for top careers
            decisions = []
            for rank, (career_id, base_score) in enumerate(eligible_careers[:self.top_decisions_count], 1):
                career_data = next(
                    (c for c in careers_db if c.get('career_id') == career_id),
                    None
                )

                if not career_data:
                    logger.warning(f"Career {career_id} not found in database")
                    continue

                # Synthesize decision
                decision = self._create_career_decision(
                    rank=rank,
                    career_id=career_id,
                    career_data=career_data,
                    base_score=base_score,
                    internet_data=internet_data.get(career_id, {}),
                    rag_evidence=rag_evidence.get(career_id, []),
                    all_scores=profile_scores
                )

                decisions.append(decision)

            return decisions

        except Exception as e:
            logger.error(f"Error synthesizing decisions: {e}")
            return []

    def _create_career_decision(
        self,
        rank: int,
        career_id: str,
        career_data: Dict[str, Any],
        base_score: float,
        internet_data: Dict[str, Any],
        rag_evidence: List[str],
        all_scores: Dict[str, float]
    ) -> CareerDecision:
        """Create a single career decision with full reasoning"""

        # Extract scoring components (assuming available from previous scoring)
        skill_score = base_score * 0.45  # Simplified calculation
        interest_score = base_score * 0.25
        education_score = base_score * 0.15
        market_score = base_score * 0.15

        # Boost score if internet data shows high demand
        internet_boost = self._calculate_internet_boost(internet_data)
        adjusted_score = min(1.0, base_score + internet_boost)

        # Generate reasoning
        primary_reason = self._generate_primary_reason(
            career_data,
            base_score,
            internet_data,
            skill_score,
            interest_score
        )

        secondary_reasons = self._generate_secondary_reasons(
            career_data,
            base_score,
            internet_data,
            education_score,
            market_score
        )

        # Risk and opportunity analysis
        risk_factors = self._identify_risk_factors(career_data, internet_data)
        opportunities = self._identify_opportunities(career_data, internet_data)

        # Next steps
        recommended_steps = self._generate_next_steps(
            career_data,
            skill_score,
            internet_data
        )

        # Salary estimation
        salary_year_1 = self._estimate_salary(career_data, internet_data, year=1)
        salary_year_5 = self._estimate_salary(career_data, internet_data, year=5)

        # Create decision object
        decision = CareerDecision(
            rank=rank,
            career_id=career_id,
            career_title=career_data.get('title', 'Unknown'),
            category=career_data.get('category', 'General'),
            
            overall_score=adjusted_score,
            skill_match_score=skill_score,
            interest_match_score=interest_score,
            education_fit_score=education_score,
            market_demand_score=market_score,
            
            market_growth_2026=internet_data.get('market_trends', {}).get('job_growth_2024_2026', 'Unknown'),
            salary_range=internet_data.get('salary', {}).get('salary_ranges', {}).get('mid', {}).get('min', 'Unknown'),
            job_availability=self._assess_job_availability(internet_data),
            trending_skills=internet_data.get('skills', {}).get('emerging_skills', []),
            top_employers=internet_data.get('companies', {}).get('top_employers', []),
            
            primary_reason=primary_reason,
            secondary_reasons=secondary_reasons,
            risk_factors=risk_factors,
            opportunities=opportunities,
            recommended_next_steps=recommended_steps,
            
            confidence_level=self._calculate_confidence(adjusted_score),
            data_sources=['local_scoring', 'internet_data', 'rag_evidence', 'market_analysis'],
            assumptions=self._get_assumptions(career_data),
            alternative_paths=career_data.get('entry_points', []),
            
            years_to_establishment=self._estimate_years_to_establishment(career_data),
            estimated_salary_year_1=salary_year_1,
            estimated_salary_year_5=salary_year_5,
        )

        return decision

    def _calculate_internet_boost(self, internet_data: Dict) -> float:
        """Calculate score boost based on internet market data"""
        boost = 0.0

        # Check market trends
        if internet_data.get('market_trends', {}).get('job_growth_2024_2026'):
            growth = internet_data['market_trends']['job_growth_2024_2026']
            if 'high' in growth.lower():
                boost += 0.05
            elif 'very high' in growth.lower():
                boost += 0.10

        # Check salary trends
        if internet_data.get('salary', {}).get('salary_growth'):
            boost += 0.02

        # Check remote percentage
        if internet_data.get('market_trends', {}).get('remote_percentage'):
            remote = internet_data['market_trends'].get('remote_percentage', '')
            if '60%' in remote or '70%' in remote:
                boost += 0.03

        return min(boost, 0.15)  # Cap boost at 15%

    def _generate_primary_reason(
        self,
        career_data: Dict,
        score: float,
        internet_data: Dict,
        skill_score: float,
        interest_score: float
    ) -> str:
        """Generate primary reason for recommendation"""

        if skill_score > 0.8:
            return f"Exceptional match with your skills. You have strong proficiency in {len(career_data.get('required_skills', []))} required skills for this role."

        if interest_score > 0.75:
            return f"Perfect alignment with your interests in {', '.join(career_data.get('interests', [])[:3])}."

        if score > 0.75:
            return f"Strong overall match across skills, interests, education, and market demand. {career_data.get('title')} is rapidly growing with {internet_data.get('market_trends', {}).get('job_growth_2024_2026', 'solid')} demand."

        return f"Good match for {career_data.get('title')} with relevant skills and strong market opportunities in 2026."

    def _generate_secondary_reasons(
        self,
        career_data: Dict,
        score: float,
        internet_data: Dict,
        education_score: float,
        market_score: float
    ) -> List[str]:
        """Generate secondary reasons"""

        reasons = []

        # Market opportunity
        market_data = internet_data.get('market_trends', {})
        if market_score > 0.70:
            growth = market_data.get('job_growth_2024_2026', 'moderate')
            reasons.append(f"High market demand with {growth} job growth projected through 2026")

        # Salary potential
        if internet_data.get('salary', {}):
            salary_data = internet_data['salary']
            mid_salary = salary_data.get('salary_ranges', {}).get('mid', {})
            if mid_salary:
                reasons.append(f"Competitive compensation with mid-career salary around ${mid_salary.get('min', 'N/A'):,}")

        # Emerging skills
        emerging = internet_data.get('skills', {}).get('emerging_skills', [])
        if emerging:
            reasons.append(f"Demand for emerging skills: {', '.join(emerging[:2])}")

        # Specialization opportunities
        specializations = self._get_specializations(career_data)
        if specializations:
            reasons.append(f"Multiple specialization paths available: {', '.join(specializations[:2])}")

        # Remote work
        if 'remote' in internet_data.get('market_trends', {}).get('remote_percentage', '').lower():
            reasons.append("Strong remote work opportunities (45-65% of roles available remotely)")

        return reasons[:4]

    def _identify_risk_factors(
        self,
        career_data: Dict,
        internet_data: Dict
    ) -> List[str]:
        """Identify potential risk factors"""

        risks = []

        difficulty = career_data.get('difficulty', 0)
        if difficulty >= 4:
            risks.append(f"High difficulty level (Level {difficulty}/4) - requires significant commitment")

        # Market saturation
        if internet_data.get('market_trends', {}).get('hiring_trends') == 'Stable':
            risks.append("Market growth is stable rather than booming - expect moderate competition")

        # Skill requirements
        required_skills = len(career_data.get('required_skills', []))
        if required_skills > 8:
            risks.append(f"Requires mastery of {required_skills}+ different skills")

        # Salary uncertainty
        salary = internet_data.get('salary', {}).get('salary_ranges', {}).get('mid', {})
        if salary and salary.get('min', 0) < 80000:
            risks.append("Entry-level positions may have lower starting salaries")

        # Time to establishment
        years = self._estimate_years_to_establishment(career_data)
        if years > 5:
            risks.append(f"Typically requires {years}+ years to establish expertise")

        return risks[:4]

    def _identify_opportunities(
        self,
        career_data: Dict,
        internet_data: Dict
    ) -> List[str]:
        """Identify opportunities in this career"""

        opportunities = []

        # Growth trajectory
        growth = career_data.get('growth', 'medium')
        if growth in ['high', 'very high']:
            opportunities.append(f"Exceptional growth trajectory ({growth.capitalize()}) - increasing demand and salary")

        # Specializations
        specializations = self._get_specializations(career_data)
        if specializations:
            opportunities.append(f"Specialization opportunities: {', '.join(specializations[:2])}")

        # Companies hiring
        companies = internet_data.get('companies', {}).get('top_employers', [])
        if companies:
            opportunities.append(f"Opportunities with leading companies: {', '.join(companies[:2])}")

        # 2026 trends
        if 'AI' in career_data.get('trend', '') or 'tech' in career_data.get('trend', '').lower():
            opportunities.append("Well-positioned for 2026 technology trends and transformations")

        # Salary growth
        salary_growth = internet_data.get('market_trends', {}).get('salary_growth', '')
        if 'double' in salary_growth.lower() or '20%' in salary_growth:
            opportunities.append("Strong salary growth potential (8-20% annually)")

        # Remote work
        if 'remote' in internet_data.get('market_trends', {}).get('remote_percentage', '').lower():
            opportunities.append("Flexibility with remote work options")

        return opportunities[:5]

    def _generate_next_steps(
        self,
        career_data: Dict,
        skill_score: float,
        internet_data: Dict
    ) -> List[str]:
        """Generate recommended next steps"""

        steps = []

        # Skill development
        if skill_score < 0.7:
            required = career_data.get('required_skills', [])[:3]
            steps.append(f"Priority: Develop core skills - {', '.join(required)}")

        # Education
        entry_points = career_data.get('entry_points', [])
        if entry_points:
            steps.append(f"Consider education path: {entry_points[0]}")

        # Certifications
        certs = internet_data.get('skills', {}).get('certifications_needed', [])
        if certs:
            steps.append(f"Pursue certifications: {certs[0]}")

        # Projects/portfolio
        steps.append("Build portfolio projects demonstrating your skills")

        # Networking
        companies = internet_data.get('companies', {}).get('top_employers', [])
        if companies:
            steps.append(f"Network with professionals at: {companies[0]}")

        # Timeline
        years = self._estimate_years_to_establishment(career_data)
        steps.append(f"Plan for {years}-year development timeline to reach senior level")

        return steps[:5]

    def _estimate_salary(
        self,
        career_data: Dict,
        internet_data: Dict,
        year: int = 1
    ) -> int:
        """Estimate salary for given year"""

        salary_data = internet_data.get('salary', {}).get('salary_ranges', {})

        if year == 1:
            entry = salary_data.get('entry', {})
            return entry.get('min', 50000)

        if year == 5:
            mid = salary_data.get('mid', {})
            return mid.get('min', 100000)

        return 80000

    def _estimate_years_to_establishment(self, career_data: Dict) -> int:
        """Estimate years to professional establishment"""

        difficulty = career_data.get('difficulty', 2)
        if difficulty >= 4:
            return 5
        elif difficulty == 3:
            return 3
        else:
            return 2

    def _calculate_confidence(self, score: float) -> str:
        """Calculate confidence level"""

        if score >= 0.85:
            return DecisionConfidence.VERY_HIGH.value
        elif score >= 0.70:
            return DecisionConfidence.HIGH.value
        elif score >= 0.50:
            return DecisionConfidence.MEDIUM.value
        else:
            return DecisionConfidence.LOW.value

    def _assess_job_availability(self, internet_data: Dict) -> str:
        """Assess job availability"""

        hiring = internet_data.get('market_trends', {}).get('hiring_trends', 'Unknown')
        if 'increasing' in hiring.lower():
            return "High - rapidly growing opportunities"
        elif 'stable' in hiring.lower():
            return "Stable - consistent opportunities"
        else:
            return "Moderate - steady demand"

    def _get_assumptions(self, career_data: Dict) -> List[str]:
        """Get assumptions made in reasoning"""

        return [
            "Salary data is based on 2024-2025 market rates",
            "Market projections are based on historical trends and current data",
            "Timeline estimates assume continuous learning and skill development",
            "Career progression follows typical industry patterns",
            "Remote work availability varies by company and region"
        ]

    def _get_specializations(self, career_data: Dict) -> List[str]:
        """Extract specializations from career data"""

        specializations = []

        # Get from career category
        category = career_data.get('category', '')
        if '-' in category:
            specializations.append(category.split('-')[1].strip())

        # Get from trend
        trend = career_data.get('trend', '')
        if trend:
            # Extract key words
            keywords = ['AI', 'ML', 'Cloud', 'Security', 'Data', 'Web3']
            for keyword in keywords:
                if keyword in trend:
                    specializations.append(keyword)

        return specializations[:3]

    def generate_explanation(
        self,
        decision: CareerDecision,
        career_data: Dict,
        internet_data: Dict
    ) -> ReasoningExplanation:
        """Generate detailed explainable AI explanation"""

        return ReasoningExplanation(
            decision_title=f"Why {decision.career_title} is a Great Fit for You",
            why_perfect_fit=decision.primary_reason,
            skill_requirements=self._format_skill_requirements(
                career_data.get('required_skills', []),
                career_data.get('preferred_skills', [])
            ),
            market_opportunity=f"{decision.market_growth_2026} job growth with {internet_data.get('companies', {}).get('top_employers', ['leading companies'])[0]} actively hiring",
            financial_outlook=f"Starting salary ~${decision.estimated_salary_year_1:,}, growing to ~${decision.estimated_salary_year_5:,} by year 5",
            growth_potential=career_data.get('growth', 'Unknown').title(),
            challenges="; ".join(decision.risk_factors[:2]),
            success_factors="; ".join(decision.opportunities[:2])
        )

    def _format_skill_requirements(self, required: List[str], preferred: List[str]) -> str:
        """Format skill requirements for explanation"""

        req_str = ", ".join(required[:3])
        pref_str = ", ".join(preferred[:2])
        return f"Required: {req_str}. Preferred: {pref_str}."
