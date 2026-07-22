from app.reality_feed import RealityFeed


class ZeroHourGate:
    def __init__(self, reality_feed: RealityFeed | None = None):
        self.reality_feed = reality_feed or RealityFeed()

    async def verify_and_transmit(
        self, synthesized_payload: dict, execution_target
    ) -> dict:
        actual = await self.reality_feed.get_live_actuality()

        veto_reason = None
        assumptions = synthesized_payload.get("assumptions", [])
        for assumption in assumptions:
            actual_value = actual.get(assumption)
            if actual_value is False:
                veto_reason = f"{assumption}_INVERTED"
                break

        if veto_reason is not None:
            return {
                "response": f"Z-12 HALT: {veto_reason} — assumption invalidated by reality feed.",
                "assumptions": assumptions,
                "metadata": {
                    "execution_status": "EXCEPTION_INTERCEPTED",
                    "veto_reason": veto_reason,
                },
                "confidence": 0.0,
            }

        await execution_target.transmit(synthesized_payload)
        return synthesized_payload
