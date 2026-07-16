class Scheduler:
    def __init__(self, config):
        self.config = config
    def schedule(self):
        # For MVP, schedule all configured tracks in parallel
        return list(self.config.tracks.keys())
