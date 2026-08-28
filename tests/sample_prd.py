"""A complete PRD payload used by tests. Mirrors the API response schema."""

SAMPLE_PRD = {
    "product_overview": "A marketplace that helps college students find and book tutors.",
    "problem_statement": "Students struggle to find affordable, trusted tutors quickly.",
    "target_users": ["College students", "Independent tutors"],
    "personas": [
        {
            "name": "Aisha",
            "role": "Undergraduate student",
            "goals": ["Find a calculus tutor this week"],
            "pain_points": ["Campus tutoring slots fill up too fast"],
        }
    ],
    "business_objectives": [
        "Help 1,000 students book a first session in the first term"
    ],
    "user_stories": [
        {
            "id": "US-001",
            "as_a": "student",
            "i_want": "to search tutors by subject",
            "so_that": "I can book help before my exam",
        }
    ],
    "functional_requirements": [
        {
            "id": "FR-001",
            "description": "Users can search tutors by subject and availability",
            "priority": "high",
        }
    ],
    "non_functional_requirements": [
        {
            "id": "NFR-001",
            "description": "Search results should load in under 2 seconds",
            "category": "performance",
        }
    ],
    "risks": ["Low tutor supply in niche subjects"],
    "assumptions": ["Students have access to a smartphone or laptop"],
    "future_enhancements": ["In-app video sessions"],
}