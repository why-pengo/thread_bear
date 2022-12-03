import multiprocessing
import subprocess
import time

results = []


def run_check(chk):
    name = multiprocessing.current_process().name
    cmd = ["nc", "-z", "-w", f"{chk['timeout']}", f"{chk['address']}", f"{chk['port']}"]
    rv = subprocess.run(cmd, check=False)
    if rv.returncode == 0:
        results.append("success")
    else:
        results.append("failure")
    print(f"{name}:rv.returncode {rv.returncode} for {' '.join(cmd)}")


def run_all_checks(targets):
    with multiprocessing.Pool() as pool:
        pool.map(run_check, targets)


if __name__ == "__main__":
    targets = [{"address": "localhost", "port": "8080", "timeout": "3"},
               {"address": "localhost", "port": "8000", "timeout": "3"},
               {"address": "localhost", "port": "80", "timeout": "3"},
               {"address": "localhost", "port": "90", "timeout": "3"}, ]
    start_time = time.time()
    run_all_checks(targets)
    duration = time.time() - start_time
    print(f"Ran {len(targets)} check(s) in {duration} seconds")
    print(f"results = {results}")
