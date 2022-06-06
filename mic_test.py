import subprocess 
import os, signal
from time import time_ns
file_name1 = "mic_test_problem.wav"
file_name2 = "mic_test2.wav"
try: 
    init_time = time_ns()
    p = subprocess.Popen(['arecord', '--format=S16_LE', '--rate=16000', '--file-type=wav', file_name1])
    # while(True):
    #     if time_ns() - init_time >= 5e9:

except KeyboardInterrupt: 
    print("First audio finished")
finally:
    print("Program ending ")

while(True):
    if time_ns() - init_time >= 5e9:
        os.kill(p.pid, signal.SIGINT)  # Send the signal to all the process groups
        print("audio completed")
        break 
print("Actually ending now")
