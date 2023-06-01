import multiprocessing
import time
from lib.core import *

def function1(queue, b):
    print(b)
    time.sleep(10)  # Simulating a long-running task
    
    result = "Result from Function 1"
    queue.put(result)

def function2(queue, a):
    #time.sleep(5)  # Simulating a long-running task
    result = "Result from Function 2"
    print(a)
    queue.put(result)

CONF = Config()

def check_timeout(conf: Config):
    queue = multiprocessing.Queue()
    b=1
    a=2
    process1 = multiprocessing.Process(target=function1, args=(queue,b))
    process2 = multiprocessing.Process(target=function2, args=(queue,a))

    process1.start()
    process2.start()
    
    # Wait for the first function to finish or timeout
    process1.join(timeout=conf.default_timeout_value)

    if process1.is_alive():
        # First function is still running after 60 seconds, terminate it
        process1.terminate()
        process1.join()

        # Get the result from the second function
        result = queue.get()
        print("Main function: ", result)
    else:
        # Get the result from the first function
        result = queue.get()
        print("Main function: ", result)

    # Clean up the second function if it's still running
    if process2.is_alive():
        process2.terminate()
        process2.join()

def main():
    check_timeout(conf = CONF)

if __name__ == "__main__":
    main()
