from storage.database import Database

class MetricsRecorder:
    def __init__(self):
        self.db = Database()
    def record(self, data):
        # data is a dict; store under metrics table
        self.db.insert(data)
