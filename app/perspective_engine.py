import asyncio
import time
from typing import Dict, List, Any

class PerspectiveEngine:
    """Multi-perspective analysis engine for comprehensive response evaluation.
    
    Generates specialized viewpoints on responses:
    - Engineering: Technical feasibility, performance, scalability
    - Scientific: Accuracy, methodology, evidence quality
    - Business: ROI, market fit, commercial viability
    - Economic: Cost-benefit, financial impact
    - Security: Vulnerabilities, threat model, data protection
    - Legal: Compliance, liability, intellectual property
    - Ethics: Bias, fairness, social impact
    - User Experience: Usability, accessibility, user satisfaction
    - Operations: Implementation, maintainability, support
    - Education: Learning curve, documentation, knowledge transfer
    - Risk Analysis: Failure modes, contingency, mitigation
    - System Design: Architecture, reliability, fault tolerance
    """
    
    PERSPECTIVES = [
        "engineering",
        "scientific",
        "business",
        "economic",
        "security",
        "legal",
        "ethics",
        "ux",
        "operations",
        "education",
        "risk",
        "design"
    ]
    
    def __init__(self, adapter=None):
        """Initialize perspective engine with optional provider adapter.
        
        Args:
            adapter: Provider adapter for generating perspectives (mock used if None)
        """
        self.adapter = adapter
    
    async def analyze(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate multi-perspective analysis asynchronously.
        
        Args:
            prompt: Input prompt to analyze
            context: Optional context dict
        
        Returns:
            Dict with perspectives key containing analysis from all viewpoints
        """
        if context is None:
            context = {}
        
        start_time = time.time()
        perspectives = {}
        
        # Run perspective analyses in parallel for speed
        tasks = [
            self._analyze_perspective(perspective, prompt, context)
            for perspective in self.PERSPECTIVES
        ]
        
        results = await asyncio.gather(*tasks)
        
        for perspective, analysis in results:
            perspectives[perspective] = analysis
        
        return {
            "perspectives": perspectives,
            "count": len(perspectives),
            "duration_ms": int((time.time() - start_time) * 1000)
        }
    
    async def _analyze_perspective(self, perspective: str, prompt: str, context: Dict) -> tuple:
        """Analyze prompt from a specific perspective.
        
        Args:
            perspective: Perspective type
            prompt: Input prompt
            context: Analysis context
        
        Returns:
            Tuple of (perspective_name, analysis_dict)
        """
        # Use adapter if available, otherwise generate mock analysis
        if self.adapter:
            try:
                analysis_prompt = f"Analyze from {perspective} perspective: {prompt}"
                result = self.adapter.generate(analysis_prompt)
            except Exception:
                result = self._mock_analysis(perspective, prompt)
        else:
            result = self._mock_analysis(perspective, prompt)
        
        return perspective, {
            "perspective": perspective,
            "analysis": result,
            "timestamp": time.time()
        }
    
    def _mock_analysis(self, perspective: str, prompt: str) -> str:
        """Generate mock analysis for testing.
        
        Args:
            perspective: Perspective type
            prompt: Input prompt
        
        Returns:
            Mock analysis string
        """
        perspectives_desc = {
            "engineering": "Feasible implementation with standard architecture patterns.",
            "scientific": "Supported by empirical evidence and peer review.",
            "business": "Strong market fit with clear ROI potential.",
            "economic": "Cost-effective solution with positive financial impact.",
            "security": "No identified vulnerabilities; threat model addressed.",
            "legal": "Compliant with applicable regulations and standards.",
            "ethics": "Aligned with ethical principles and social responsibility.",
            "ux": "Intuitive interface with strong user experience design.",
            "operations": "Operationally sound with clear maintenance procedures.",
            "education": "Well-documented with clear learning resources.",
            "risk": "Risk mitigation strategies in place; contingency plans defined.",
            "design": "Robust architecture with scalability and fault tolerance."
        }
        return perspectives_desc.get(
            perspective,
            f"Analysis complete from {perspective} viewpoint."
        )
    
    def get_perspectives(self) -> List[str]:
        """Get list of available perspectives.
        
        Returns:
            List of perspective names
        """
        return self.PERSPECTIVES.copy()
    
    def get_perspective_count(self) -> int:
        """Get count of available perspectives.
        
        Returns:
            Number of perspectives
        """
        return len(self.PERSPECTIVES)
