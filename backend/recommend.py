"""
Orchestration: profile -> scoring -> RAG -> LLM -> response.
"""
from typing import List
from backend.schemas import (
    ProfileRequest,
    RecommendationResponse,
    CareerRecommendation,
    Evidence
)
from backend.normalize import ProfileNormalizer
from backend.scoring import DeterministicScorer
from backend.rag import RAGSystem
from backend.llm_engine import OllamaEngine


class RecommendationPipeline:
    """Main orchestration pipeline."""

    def __init__(self):
        self.normalizer = ProfileNormalizer()
        self.scorer = DeterministicScorer()
        self.rag = RAGSystem()
        self.llm = OllamaEngine()

    def recommend(self, profile: ProfileRequest, use_llm: bool = True) -> RecommendationResponse:
        """
        Full pipeline: normalize -> score -> retrieve evidence -> LLM explanation.
        """
        # Normalize profile
        normalized_skills = self.normalizer.normalize_list(profile.skills)
        normalized_interests = self.normalizer.normalize_list(profile.interests)
        normalized_degree = self.normalizer.normalize_education(profile.education.degree)

        # Score careers
        ranked_careers = self.scorer.rank_careers(
            normalized_skills,
            normalized_interests,
            normalized_degree,
            top_n=5
        )

        # Build recommendations with evidence
        recommendations = []
        evidence_by_career = {}

        for career_dict, score, breakdown in ranked_careers:
            # Retrieve evidence for this career
            evidence_list = self.rag.retrieve_for_career(
                career_dict.get("title", ""),
                career_dict.get("keywords", []),
                normalized_interests,
                top_k=5
            )
            
            evidence_by_career[career_dict["career_id"]] = evidence_list
            
            # Convert to Evidence objects
            evidence_objects = [
                Evidence(
                    snippet=e.get("text", "")[:300],
                    source=e.get("source", "Unknown"),
                    chunk_id=e.get("chunk_id", "")
                )
                for e in evidence_list[:3]
            ]

            # Generate skill gaps
            skill_gaps = self.scorer.generate_skill_gaps(
                normalized_skills,
                career_dict.get("required_skills", [])
            )

            # Generate roadmap
            roadmap = self.scorer.generate_roadmap(career_dict)

            # Why fit (based on scoring)
            why_fit = self._generate_why_fit(
                normalized_skills,
                normalized_interests,
                career_dict
            )

            recommendation = CareerRecommendation(
                career_id=career_dict["career_id"],
                title=career_dict.get("title", ""),
                category=career_dict.get("category", ""),
                score=score,
                score_breakdown=breakdown,
                why_fit=why_fit,
                skill_gaps=skill_gaps,
                roadmap=roadmap,
                evidence=evidence_objects,
                confidence=min(score + 0.1, 1.0)  # Slight boost based on score
            )

            recommendations.append(recommendation)

        # Use LLM for deeper insights if available
        missing_questions = ["What is your preferred work environment?", 
                           "How much relocation are you willing to do?",
                           "What is your target salary range?"]
        notes = [
            "Recommendations based on deterministic scoring of skills, interests, and education",
            "Consider gaining practical experience through projects and internships",
            "Keep learning - the job market evolves rapidly with emerging trends"
        ]

        if use_llm:
            try:
                llm_insights = self._get_llm_insights(
                    profile,
                    recommendations,
                    evidence_by_career
                )
                missing_questions = llm_insights.get("missing_questions", missing_questions)
                notes = llm_insights.get("system_notes", notes)
                
                # Update why_not_others
                why_not_list = llm_insights.get("why_not_others", [])
                if why_not_list and len(recommendations) > 0:
                    recommendations[0].why_not_others = why_not_list[:3]
            except Exception as e:
                print(f"LLM error (non-blocking): {e}")
                notes.append(f"Note: LLM insights unavailable ({str(e)})")

        return RecommendationResponse(
            top_recommendations=recommendations,
            missing_info_questions=missing_questions,
            notes=notes,
            metadata={
                "profile_skills": normalized_skills,
                "profile_interests": normalized_interests,
                "profile_degree": normalized_degree
            }
        )

    def _generate_why_fit(
        self,
        user_skills: List[str],
        user_interests: List[str],
        career: dict
    ) -> List[str]:
        """Generate explanation of why career fits."""
        reasons = []
        
        # Skill matches
        required = set(s.lower() for s in career.get("required_skills", []))
        matched_required = set(user_skills) & required
        if matched_required:
            reasons.append(f"You have {len(matched_required)} required skills: {', '.join(list(matched_required)[:3])}")
        
        # Interest matches
        career_interests = set(i.lower() for i in career.get("interests", []))
        matched_interests = set(user_interests) & career_interests
        if matched_interests:
            reasons.append(f"Your interests align with this path: {', '.join(list(matched_interests)[:3])}")
        
        # Category insight
        category = career.get("category", "")
        if category:
            reasons.append(f"Strong opportunity in the {category} sector")
        
        if not reasons:
            reasons.append("Career matches your profile based on overall score")
        
        return reasons

    def _get_llm_insights(
        self,
        profile: ProfileRequest,
        recommendations: List[CareerRecommendation],
        evidence_by_career: dict
    ) -> dict:
        """Get LLM insights on recommendations."""
        # Format for LLM
        top_careers_str = "\n".join([
            f"- {r.title} ({r.career_id}): Score {r.score} - {', '.join(r.why_fit[:2])}"
            for r in recommendations[:3]
        ])

        user_profile_str = f"""
        Skills: {', '.join(profile.skills[:5])}
        Interests: {', '.join(profile.interests[:5])}
        Education: {profile.education.degree}
        """

        evidence_str = "\n".join([
            f"- {r.title}: {evidence_by_career.get(r.career_id, [{}])[0].get('text', 'N/A')[:100]}"
            for r in recommendations[:3]
        ])

        return self.llm.generate_recommendations(
            top_careers_str,
            user_profile_str,
            evidence_str
        )
