"""
Profile normalization: skill synonyms, lowercase, trimming.
"""
import json
from pathlib import Path
from typing import List, Set
from backend.config import SYNONYMS_FILE


class ProfileNormalizer:
    """Normalize user profiles (skills, interests, etc.)."""

    def __init__(self, synonyms_file: Path = SYNONYMS_FILE):
        """Load synonym mappings."""
        with open(synonyms_file, "r") as f:
            self.synonyms = json.load(f)
        
        # Build reverse mapping: synonym -> canonical form
        self.synonym_map = {}
        for canonical, synonyms in self.synonyms.items():
            canonical_lower = canonical.lower()
            self.synonym_map[canonical_lower] = canonical_lower
            for syn in synonyms:
                self.synonym_map[syn.lower()] = canonical_lower

    def normalize_list(self, items: List[str]) -> List[str]:
        """Normalize a list of items (skills, interests, etc.)."""
        if not items:
            return []
        
        normalized = set()
        for item in items:
            item_clean = item.strip().lower()
            if not item_clean:
                continue
            
            # Map via synonyms
            canonical = self.synonym_map.get(item_clean, item_clean)
            normalized.add(canonical)
        
        return sorted(list(normalized))

    def normalize_skill(self, skill: str) -> str:
        """Normalize a single skill."""
        skill_clean = skill.strip().lower()
        return self.synonym_map.get(skill_clean, skill_clean)

    def normalize_education(self, degree: str) -> str:
        """Normalize education degree."""
        return degree.lower().strip()
