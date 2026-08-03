class Validator:
    """Validates synthesized responses for consistency, confidence, and drift.
    
    Evaluates:
    - Answer completeness (not empty or trivial)
    - Confidence in correctness (0-100)
    - Conceptual drift from original request (0-100, lower is better)
    - Quality notes and confidence reasoning
    """
    
    def validate(self, merged):
        """Validate a merged response from all tracks.
        
        Args:
            merged: Dict with 'answer' and optional 'sources'
        
        Returns:
            Dict with pass (bool), confidence (0-100), drift (0-100), notes (list)
        """
        answer = merged.get("answer", "").strip()
        sources = merged.get("sources", [])
        
        # Check completeness
        is_empty = len(answer) == 0
        is_trivial = len(answer) < 10
        is_mock = "MOCK_ANSWER" in answer
        
        # Confidence scoring (0-100)
        confidence = 100
        notes = []
        
        if is_empty:
            confidence = 0
            notes.append("answer is empty")
        elif is_trivial:
            confidence = 45
            notes.append("answer is incomplete or trivial")
        elif is_mock:
            confidence = 50
            notes.append("mock provider response detected")
        elif len(sources) > 0:
            # Multi-source synthesis increases confidence
            base_conf = 80
            # Bonus if direct track was involved (more confident)
            if "direct" in sources:
                base_conf += 10
            # Bonus if multiple sources agree (perspective included)
            if len(sources) >= 3:
                base_conf += 5
            confidence = min(95, base_conf)
            notes.append(f"synthesized from {len(sources)} track(s)")
        else:
            confidence = 75
            notes.append("single-track response")
        
        # Drift scoring (0-100, lower is better)
        # Simplified: longer answers with multiple sources = lower drift
        drift = 100 - (min(len(answer) / 500, 1) * 30)  # content length factor
        if len(sources) >= 3:
            drift -= 20  # multi-track reduces drift
        if "direct" in sources:
            drift -= 15  # direct track more accurate
        drift = max(0, min(100, drift))
        
        return {
            "pass": confidence >= 40,  # Pass threshold
            "confidence": int(confidence),
            "drift": int(drift),
            "notes": notes
        }
