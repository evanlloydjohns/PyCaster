import time


class Timer:
    def __init__(self):
        self.start_time = time.time()
        self.current_time = None
        self.last_time = None
        self.time_record = []

    # Returns time since last func call in ms
    def tick(self):
        if self.last_time is None:
            self.last_time = time.time()
        self.current_time = time.time()
        r_time = self.current_time - self.last_time
        self.last_time = time.time()
        self.time_record.append(r_time)
        return round(r_time * 1000, 2)

    def get_total_time(self):
        return round((time.time() - self.start_time) * 1000, 3)
