"""
Offline evaluation of the recommendation system.
Run: python scripts/evaluate.py
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.schemas import ProfileRequest, EducationInput
from backend.recommend import RecommendationPipeline


def create_test_profiles():
    """Create diverse test profiles across all industries."""
    return [
        {
            "name": "Test 1: AI/ML Enthusiast",
            "education": {"degree": "Bachelor's", "field": "Engineering", "year": 2024, "cgpa": 3.8},
            "skills": ["Python", "Machine Learning", "TensorFlow", "Data Analysis"],
            "interests": ["AI", "Deep Learning", "Neural Networks", "Research"]
        },
        {
            "name": "Test 2: Web Developer",
            "education": {"degree": "Bachelor's", "field": "Science", "year": 2023, "cgpa": 3.5},
            "skills": ["JavaScript", "React", "Node.js", "CSS", "HTML"],
            "interests": ["Web Development", "UI/UX", "Frontend", "Creativity"]
        },
        {
            "name": "Test 3: Finance Analyst",
            "education": {"degree": "Bachelor's", "field": "Commerce", "year": 2022, "cgpa": 3.7},
            "skills": ["Excel", "SQL", "Statistics", "Financial Analysis"],
            "interests": ["Finance", "Markets", "Data Analysis", "Investment"]
        },
        {
            "name": "Test 4: Healthcare Professional",
            "education": {"degree": "Master's", "field": "Science", "year": 2023, "cgpa": 3.6},
            "skills": ["Research", "Data Analysis", "Problem Solving"],
            "interests": ["Healthcare", "Science", "Innovation", "Patient Care"]
        },
        {
            "name": "Test 5: Design & UX",
            "education": {"degree": "Bachelor's", "field": "Design", "year": 2024, "cgpa": 3.4},
            "skills": ["Figma", "User Research", "Prototyping", "UI Design"],
            "interests": ["Design", "UX", "Creativity", "User Experience"]
        }
    ]


def evaluate():
    """Run comprehensive evaluation."""
    print("=" * 70)
    print("CAREER RECOMMENDATION SYSTEM - EVALUATION SUITE")
    print("=" * 70)
    
    pipeline = RecommendationPipeline()
    test_profiles = create_test_profiles()
    
    results = []
    
    for test in test_profiles:
        print(f"\n📝 Evaluating: {test['name']}")
        
        try:
            profile = ProfileRequest(
                education=EducationInput(**test["education"]),
                skills=test["skills"],
                interests=test["interests"]
            )
            
            response = pipeline.recommend(profile, use_llm=False)
            
            if response.top_recommendations:
                top1 = response.top_recommendations[0]
                print(f"   ✅ Top recommendation: {top1.title}")
                print(f"      Score: {top1.score:.3f} | Confidence: {top1.confidence:.2%}")
                print(f"      Category: {top1.category}")
                
                results.append({
                    "test": test["name"],
                    "top_career": top1.title,
                    "score": top1.score,
                    "recommendations_count": len(response.top_recommendations),
                    "status": "success"
                })
            else:
                print(f"   ⚠️ No recommendations generated")
                results.append({
                    "test": test["name"],
                    "status": "no_results"
                })
        
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results.append({
                "test": test["name"],
                "status": "error",
                "error": str(e)
            })
    
    # Summary
    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)
    
    successful = sum(1 for r in results if r["status"] == "success")
    total = len(results)
    
    print(f"\n✅ Successful: {successful}/{total} ({successful*100//total}%)")
    print(f"⚠️  No results: {sum(1 for r in results if r['status'] == 'no_results')}")
    print(f"❌ Errors: {sum(1 for r in results if r['status'] == 'error')}")
    
    print("\nDetailed Results:")
    print("-" * 70)
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['test']}: {result['status'].upper()}")
        if "top_career" in result:
            print(f"   → {result['top_career']} (Score: {result['score']:.3f})")
    
    print("\n" + "=" * 70)
    print("✨ Evaluation Complete!")
    print("=" * 70)


if __name__ == "__main__":
    evaluate()
