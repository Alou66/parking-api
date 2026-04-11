import json
import threading

class StorageError(Exception):
    pass

class ParkingStorage:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.lock = threading.Lock()

    def lire(self):
        with self.lock:
            try:
                with open(self.file_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                raise StorageError(str(e))

    def ecrire(self, data):
        with self.lock:
            try:
                with open(self.file_path, "w") as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                raise StorageError(str(e))