import concurrent.futures
import queue
import subprocess
import threading
import time


class DataSync:
    def __init__(self):
        self.value = []
        self._lock = threading.Lock()

    def locked_update(self, new_value):
        with self._lock:
            local_copy = self.value
            local_copy.append(new_value)
            self.value = local_copy


def producer(queue, chk, target):
    # print(f"pro db.value = {db.value}")
    message = chk(target)
    queue.put(message)


def consumer(db, queue):
    # print(f"con db.value = {db.value}")
    message = queue.get()
    print(f"Consumer storing message: {message} (size={queue.qsize()})")
    db.locked_update(message)


def run_check(target):
    cmd = ["nc", "-z", "-w", f"{target['timeout']}", f"{target['address']}", f"{target['port']}"]
    rv = subprocess.run(cmd, check=False, capture_output=True)
    print(f"\nrv.returncode {rv.returncode} for {' '.join(cmd)}")
    if rv.returncode != 0:
        return "failure"
    else:
        return "success"


if __name__ == "__main__":
    pipeline = queue.Queue(maxsize=10)
    db = DataSync()
    targets = [{"address": "localhost", "port": "8080", "timeout": "3"},
               {"address": "localhost", "port": "8000", "timeout": "3"},
               {"address": "localhost", "port": "4200", "timeout": "3"},
               {"address": "localhost", "port": "90", "timeout": "3"}, ]
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        for target in targets:
            executor.submit(producer, pipeline, run_check, target)
            executor.submit(consumer, db, pipeline)

    duration = time.time() - start_time
    print(f"\nRan {len(targets)} check(s) in {duration} seconds")
    print(f"db.value = {db.value}")