import concurrent.futures
import functools
import logging
import queue
import random
import subprocess
import threading
import time


class FakeDatabase:
    def __init__(self):
        self.value = []
        self._lock = threading.Lock()

    def locked_update(self, new_value):
        with self._lock:
            local_copy = self.value
            local_copy.append(new_value)
            self.value = local_copy


def producer(queue, event):
    """Pretend we're getting a number from the network."""
    while not event.is_set():
        message = random.randint(1, 101)
        logging.info("Producer got message: %s", message)
        queue.put(message)

    logging.info("Producer received event. Exiting")


def consumer(queue, event):
    """Pretend we're saving a number in the database."""
    while not event.is_set() or not queue.empty():
        message = queue.get()
        logging.info("Consumer storing message: %s (size=%d)", message, queue.qsize())

    logging.info("Consumer received event. Exiting")


def run_check(db, chk):
    cmd = ["nc", "-z", "-w", f"{chk['timeout']}", f"{chk['address']}", f"{chk['port']}"]
    rv = subprocess.run(cmd, check=False)
    if rv.returncode == 0:
        db.locked_update("success")
    else:
        db.locked_update("failure")
    print(f"rv.returncode {rv.returncode} for {' '.join(cmd)}")


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    pipeline = queue.Queue(maxsize=10)
    event = threading.Event()
    db = FakeDatabase()
    targets = [{"address": "localhost", "port": "8080", "timeout": "3"},
               {"address": "localhost", "port": "8000", "timeout": "3"},
               {"address": "localhost", "port": "80", "timeout": "3"},
               {"address": "localhost", "port": "90", "timeout": "3"}, ]
    fn = functools.partial(run_check, db)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # executor.submit(producer, pipeline, event)
        # executor.submit(consumer, pipeline, event)
        executor.map(fn, targets)

    print(f"db.value = {db.value}")