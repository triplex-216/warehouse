import multiprocessing
import time

def function1(queue):
    time.sleep(5)  # Simulating a long-running task
    result = "Result from Function 1"
    queue.put(result)

def function2(queue):
    time.sleep(1)  # Simulating a long-running task
    result = "Result from Function 2"
    queue.put(result)

def main():
    queue = multiprocessing.Queue()
    
    process1 = multiprocessing.Process(target=function1, args=(queue,))
    process2 = multiprocessing.Process(target=function2, args=(queue,))

    process1.start()
    process2.start()

    # Wait for the first function to finish or timeout
    process1.join(timeout=6)

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

if __name__ == "__main__":
    main()
