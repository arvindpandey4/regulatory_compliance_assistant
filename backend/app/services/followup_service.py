import json
import os
from typing import List, Optional

class FollowUpService:
    """Service to manage and retrieve contextual follow-up questions"""
    
    def __init__(self, followup_kb_path: str = "data/followup_questions.json"):
        self.followup_kb_path = followup_kb_path
        self.followup_data = None
        self._load_followup_kb()
    
    def _load_followup_kb(self):
        """Load the follow-up questions knowledge base"""
        try:
            if os.path.exists(self.followup_kb_path):
                with open(self.followup_kb_path, 'r', encoding='utf-8') as f:
                    self.followup_data = json.load(f)
                print(f"[FollowUpService] Loaded {len(self.followup_data.get('followup_mappings', []))} follow-up mappings")
            else:
                print(f"[FollowUpService] Warning: {self.followup_kb_path} not found")
                self.followup_data = {"followup_mappings": [], "general_followups": {"questions": []}}
        except Exception as e:
            print(f"[FollowUpService] Error loading follow-up KB: {e}")
            self.followup_data = {"followup_mappings": [], "general_followups": {"questions": []}}
    
    def get_followup_questions(self, kb_entry_id: Optional[str] = None, max_questions: int = 3) -> List[str]:
        """
        Retrieve follow-up questions for a given KB entry ID
        
        Args:
            kb_entry_id: The ID of the KB entry (e.g., "KB_DEF_001")
            max_questions: Maximum number of questions to return
            
        Returns:
            List of follow-up questions
        """
        if not self.followup_data:
            return []
        
        # If we have a specific KB entry ID, try to find matching follow-ups
        if kb_entry_id:
            for mapping in self.followup_data.get("followup_mappings", []):
                if mapping.get("kb_entry_id") == kb_entry_id:
                    questions = mapping.get("questions", [])
                    return questions[:max_questions]
        
        # Fallback to general follow-up questions
        general_questions = self.followup_data.get("general_followups", {}).get("questions", [])
        return general_questions[:max_questions]
    
    def get_followup_by_category(self, category: str, max_questions: int = 3) -> List[str]:
        """
        Retrieve follow-up questions by category
        
        Args:
            category: The category (e.g., "definition", "process")
            max_questions: Maximum number of questions to return
            
        Returns:
            List of follow-up questions
        """
        if not self.followup_data:
            return []
        
        for mapping in self.followup_data.get("followup_mappings", []):
            if mapping.get("category") == category:
                questions = mapping.get("questions", [])
                return questions[:max_questions]
        
        # Fallback to general
        general_questions = self.followup_data.get("general_followups", {}).get("questions", [])
        return general_questions[:max_questions]

# Singleton instance
followup_service = FollowUpService()
