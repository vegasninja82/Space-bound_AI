class MergeEngine:
    def merge(self, track_outputs):
        # deterministic merge: prefer 'direct' > 'perspective' > first
        if not track_outputs:
            return {"answer": "", "sources": []}
        mapping = {t['track']: t for t in track_outputs}
        if 'direct' in mapping:
            chosen = mapping['direct']
        elif 'perspective' in mapping:
            chosen = mapping['perspective']
        else:
            chosen = track_outputs[0]
        return {"answer": chosen['answer'], "sources": [t['track'] for t in track_outputs]}
