from __future__ import annotations

from typing import Dict, List


def grade_prioritization(actions: List[str]) -> float:
    """Grade task prioritization - must return score strictly in (0, 1) range."""
    if not actions:
        return 0.01  # Minimum score > 0
    
    # Score based on action sequence quality
    score = 0.5  # Base score
    
    # Email should be first (highest urgency initially)
    if actions[0] == "email":
        score += 0.2
    elif actions[0] == "bug":
        score += 0.1
    else:
        score -= 0.2
    
    # Check if all tasks were attempted
    unique_actions = set(actions)
    if len(unique_actions) >= 3:
        score += 0.2
    elif len(unique_actions) >= 2:
        score += 0.1
    else:
        score -= 0.1
    
    # Ensure strictly in (0, 1) range
    return max(0.01, min(0.99, score))


def grade_context_switching(actions: List[str]) -> float:
    """Grade context switching ability - must return score strictly in (0, 1) range."""
    target = ["email", "bug", "meeting"]
    if not actions:
        return 0.01  # Minimum score > 0
    
    # Base score for attempting
    score = 0.4
    
    # Check sequential matching
    matched = 0
    for i, t in enumerate(target):
        if i < len(actions) and actions[i] == t:
            matched += 1
    
    # Add score for matches
    score += (matched / 3) * 0.4
    
    # Bonus for completing all tasks even if out of order
    unique_actions = set(actions)
    if len(unique_actions) >= 3:
        score += 0.15
    
    # Ensure strictly in (0, 1) range
    return max(0.01, min(0.99, score))


def grade_crisis_management(state: Dict) -> float:
    """Grade crisis management - must return score strictly in (0, 1) range."""
    completed = len(state.get("completed", []))
    completion = completed / 3
    
    # Base score for attempting the crisis
    score = 0.3
    
    # Completion component
    score += completion * 0.35
    
    # Emotional intelligence component
    mood = state.get("mood", "normal")
    if mood == "recovered":
        score += 0.25  # Best outcome
    elif mood == "angry_client":
        score += 0.05  # Didn't recover
    else:
        score += 0.15  # Normal, no crisis triggered
    
    # Recovery bonus
    if state.get("recovery_used", False):
        score += 0.05
    
    # Ensure strictly in (0, 1) range
    return max(0.01, min(0.99, score))

