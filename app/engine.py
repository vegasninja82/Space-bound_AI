"""
Main orchestration engine. Wires together the adapter, scheduler,
validator, perspective engine, merge engine, and ZeroHourGate into the
full pipeline the /chat endpoint calls.

Now uses the function-based APIs from registry, validator, and
perspective_engine instead of the old class-based ones.
"""
from __future__ import annotations

import asyncio
import time

from app.adapters.base import ProviderAdapter
from app.baseline import BaselineBuilder
from app.crucible import ZeroHourGate
from app.merge import MergeEngine
from app.models import ValidationResult
from app.perspective_engine import analyze as run_perspectives
from app.perspective_engine import available_perspectives
from app.scheduler import Scheduler
from app.storage import MetricsRecorder
from app.validator import validate as run_validation


class Engine:
    def __init__(self, config, adapter: ProviderAdapter, logger=None):
        self.config = config
        self.adapter = adapter
        self.logger = logger
        self.baseline = BaselineBuilder()
        self.scheduler = Scheduler(config)
        self.merge = MergeEngine()
        self.metrics = MetricsRecorder()
        self.zero_hour_gate = ZeroHourGate()

    async def run_track(self, track_name: str, ctx: dict) -> dict:
        """Execute a single reasoning track."""
        request_text = ctx["request"]

        if track_name == "perspective":
            perspectives_cfg = getattr(self.config, "perspectives", {})
            mode = perspectives_cfg.get("mode", "subset")
            subset = perspectives_cfg.get("subset", [])
            results = await run_perspectives(
                request_text,
                self.adapter,
                mode=mode,
                subset=subset,
            )
            if not results:
                answer = await self.adapter.generate(f"perspective:{request_text}")
                return {"track": track_name, "answer": answer}
            summary_parts = [f"{r.name}: {r.summary}" for r in results[:3]]
            return {"track": track_name, "answer": "; ".join(summary_parts)}
        else:
            framing = f"{track_name} track" if track_name != "direct" else ""
            answer = await self.adapter.generate(request_text, framing=framing)
            return {"track": track_name, "answer": answer}

    async def run(self, request_text: str) -> dict:
        """Execute the full orchestration pipeline."""
        start = time.time()

        ctx = self.baseline.build(request_text)

        tracks = list(self.config.tracks.keys())
        tasks = [self.run_track(t, ctx) for t in tracks]
        results = await asyncio.gather(*tasks)

        merged = self.merge.merge(results)

        validation_cfg = getattr(self.config, "validation", {})
        validation = await run_validation(
            prompt=request_text,
            direct_text=merged["answer"],
            adapter=self.adapter,
            confidence_threshold=validation_cfg.get("confidence_threshold", 60),
            drift_threshold=validation_cfg.get("drift_threshold", 40.0),
            second_sample=validation_cfg.get("second_sample", True),
        )

        use_zero_hour_gate = self.config.base.get("enable_zero_hour_gate", False)

        if use_zero_hour_gate:
            try:
                class ExecutionTarget:
                    async def transmit(self, payload):
                        return payload

                execution_target = ExecutionTarget()
                synthesized_payload = {
                    "response": merged["answer"],
                    "assumptions": [],
                    "metadata": {"execution_status": "PENDING"},
                    "confidence": validation.confidence,
                }

                final_output = await self.zero_hour_gate.verify_and_transmit(
                    synthesized_payload=synthesized_payload,
                    execution_target=execution_target,
                )

                if final_output.get("metadata", {}).get("execution_status") == "EXCEPTION_INTERCEPTED":
                    merged["answer"] = final_output["response"]
                    validation = ValidationResult(
                        confidence=final_output.get("confidence", 0),
                        drift=validation.drift,
                        passed=False,
                        signals=validation.signals,
                        notes=validation.notes + [f"ZeroHourGate veto: {final_output.get('metadata', {}).get('veto_reason', 'unknown')}"],
                    )
            except Exception as e:
                validation = ValidationResult(
                    confidence=validation.confidence,
                    drift=validation.drift,
                    passed=validation.passed,
                    signals=validation.signals,
                    notes=validation.notes + [f"ZeroHourGate skipped: {str(e)}"],
                )

        total_ms = int((time.time() - start) * 1000)

        validation_dict = {
            "pass": validation.passed,
            "confidence": validation.confidence,
            "drift": validation.drift,
            "signals": validation.signals,
            "notes": validation.notes,
        }

        try:
            self.metrics.record({
                "validation": validation_dict,
                "timing": {"total_ms": total_ms},
                "tracks_executed": len(results),
                "sources": merged.get("sources", []),
            })
        except Exception:
            pass

        return {
            "answer": merged["answer"],
            "validation": validation_dict,
            "timing": {"total_ms": total_ms},
            "tracks": len(results),
            "sources": merged.get("sources", []),
        }
