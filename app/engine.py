import asyncio, time
from app.baseline import BaselineBuilder
from app.scheduler import Scheduler
from app.merge import MergeEngine
from app.validator import Validator
from app.metrics import MetricsRecorder
from app.perspective_engine import PerspectiveEngine
from app.crucible import ZeroHourGate

class Engine:
    def __init__(self, config, adapter, logger):
        self.config = config
        self.adapter = adapter
        self.logger = logger
        self.baseline = BaselineBuilder()
        self.scheduler = Scheduler(config)
        self.merge = MergeEngine()
        self.validator = Validator()
        self.metrics = MetricsRecorder()
        self.perspective_engine = PerspectiveEngine(adapter=adapter)
        self.zero_hour_gate = ZeroHourGate()

    async def run_track(self, track_name, ctx):
        """Execute a single reasoning track.
        
        Args:
            track_name: Name of the track (direct, validation, perspective)
            ctx: Baseline context with request and metadata
        
        Returns:
            Dict with track name and answer
        """
        if track_name == "perspective":
            # Perspective track uses the perspective engine for multi-viewpoint analysis
            try:
                perspective_result = await self.perspective_engine.analyze(
                    ctx['request'],
                    context=ctx
                )
                # Format perspective output as answer
                perspectives_summary = ", ".join(
                    f"{p}: {perspective_result['perspectives'][p]['analysis']}"
                    for p in list(perspective_result['perspectives'].keys())[:3]  # Top 3 perspectives
                )
                return {"track": track_name, "answer": perspectives_summary}
            except Exception as e:
                # Fallback to basic adapter if perspective analysis fails
                answer = self.adapter.generate(f"{track_name}:{ctx['request']}")
                return {"track": track_name, "answer": answer}
        else:
            # Direct and validation tracks use the adapter
            answer = self.adapter.generate(f"{track_name}:{ctx['request']}")
            return {"track": track_name, "answer": answer}

    async def run(self, request_text):
        """Execute the full orchestration pipeline.
        
        Orchestrates multiple tracks, validates results, applies perspective analysis,
        and enforces ZeroHourGate collision detection before returning the final response.
        
        Args:
            request_text: User prompt/request
        
        Returns:
            Dict with answer, validation metrics, timing, and execution status
        """
        start = time.time()
        
        # Stage 1: Build baseline context
        ctx = self.baseline.build(request_text)
        
        # Stage 2: Schedule and execute tracks in parallel
        tracks = list(self.config.tracks.keys())
        tasks = [self.run_track(t, ctx) for t in tracks]
        results = await asyncio.gather(*tasks)
        
        # Stage 3: Merge results with track prioritization
        merged = self.merge.merge(results)
        
        # Stage 4: Validate synthesized response
        validation = self.validator.validate(merged)
        
        # Stage 5: Apply ZeroHourGate collision detection
        try:
            # Create a mock execution target (in production, this would be an actual service)
            class ExecutionTarget:
                async def transmit(self, payload):
                    return payload
            
            execution_target = ExecutionTarget()
            
            # Prepare payload with assumptions for ZeroHourGate verification
            synthesized_payload = {
                "response": merged["answer"],
                "assumptions": ["system_nominal", "green_light"],  # Example safety assumptions
                "metadata": {"execution_status": "PENDING"},
                "confidence": validation["confidence"]
            }
            
            # Verify and potentially veto execution
            final_output = await self.zero_hour_gate.verify_and_transmit(
                synthesized_payload=synthesized_payload,
                execution_target=execution_target
            )
            
            # Use ZeroHourGate's response if it vetoed, otherwise use merged answer
            if final_output.get("metadata", {}).get("execution_status") == "EXCEPTION_INTERCEPTED":
                merged["answer"] = final_output["response"]
                validation["confidence"] = final_output.get("confidence", 0)
                validation["notes"].append(f"ZeroHourGate veto: {final_output.get('metadata', {}).get('veto_reason', 'unknown')}")
        except Exception as e:
            # If ZeroHourGate fails, continue with merged answer
            validation["notes"].append(f"ZeroHourGate skipped: {str(e)}")
        
        # Calculate total execution time
        total_ms = int((time.time() - start) * 1000)
        
        # Stage 6: Record metrics
        try:
            self.metrics.record({
                "validation": validation,
                "timing": {"total_ms": total_ms},
                "tracks_executed": len(results),
                "sources": merged.get("sources", [])
            })
        except Exception:
            pass
        
        return {
            "answer": merged["answer"],
            "validation": validation,
            "timing": {"total_ms": total_ms},
            "tracks": len(results),
            "sources": merged.get("sources", [])
        }
