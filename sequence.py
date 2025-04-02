import subprocess
import time

import time
start_time = time.time()
subprocess.call("python 1stPart.py 1", shell=True)
subprocess.call("python 2ndPart.py 1", shell=True)
end_time = time.time()

print("Execution time:", end_time-start_time)

