import threading
import time
from queue import Queue

# A thread-safe Queue for message passing
message_queue = Queue()

def worker_function(id):
    print(f"Worker {id}: Starting and doing some work.")
    time.sleep(5)  # Simulate some work
    message = f"Message from Worker {id}"
    print(f"Worker {id}: Sending a message.")
    message_queue.put(message)  # Send a message to the central function

def central_function():
    for _ in range(3):  # Expecting 3 messages
        message = message_queue.get()  # Wait and get a message from the queue
        print(f"Central Function: Received {message}")
        message_queue.task_done()

# Create threads for workers and the central function
workers = [threading.Thread(target=worker_function, args=(i,)) for i in range(1, 4)]
central = threading.Thread(target=central_function)

# Start all threads
for w in workers:
    w.start()
central.start()

# Wait for all threads to complete
for w in workers:
    w.join()
central.join()

print("Program terminated.")
