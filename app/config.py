import os, yaml

class Config:
    def __init__(self):
        base_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
        # safe defaults
        self.base = {"provider": "mock"}
        self.tracks = {"direct": {"provider":"mock"}, "validation": {"provider":"mock"}, "perspective": {"provider":"mock"}}
        self.scheduler = {"type": "simple"}
        try:
            with open(os.path.join(base_dir, 'base.yml')) as f:
                self.base = yaml.safe_load(f) or self.base
        except Exception:
            pass
        try:
            with open(os.path.join(base_dir, 'tracks.yml')) as f:
                self.tracks = yaml.safe_load(f) or self.tracks
        except Exception:
            pass
        try:
            with open(os.path.join(base_dir, 'scheduler.yml')) as f:
                self.scheduler = yaml.safe_load(f) or self.scheduler
        except Exception:
            pass
