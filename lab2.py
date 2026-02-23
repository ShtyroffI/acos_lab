import threading
import queue
import time
import os
import random
from PIL import Image, ImageOps

def input_photos(input_dir="photos", num_images=10):
    pass

def producer(q, input_dir, num_consumers):
    pass

def consumer(q, results_q, output_dir, consumer_id):
    while True:
        path = q.get()
        if path is None:
            q.task_done()
            break
            
        print(f"Consumer {consumer_id}: Processing {path}...")
        try:
            with Image.open(path) as img:
                transposed = ImageOps.exif_transpose(img)
                if transposed:
                    img = transposed

                inverted = ImageOps.invert(img.convert('RGB'))
                
                basename = os.path.basename(path)
                output_path = os.path.join(output_dir, f"inverted_{basename}")
                
                inverted.save(output_path)
                results_q.put(output_path)
                print(f"Consumer {consumer_id}: Saved {output_path}")
        except Exception as e:
            print(f"Consumer {consumer_id}: Error: {e}")
            
        q.task_done()

if __name__ == "__main__":
    input_dir = "photos"
    output_dir = "inverted_photos"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    if not os.path.exists(input_dir) or not os.listdir(input_dir):
        print("No photos found. Inputting photos")
        input_photos(input_dir, num_images=10)
    
    task_queue = queue.Queue()
    results_queue = queue.Queue()
    
    num_consumers = 3 
    
    producer_thread = threading.Thread(target=producer, args=(task_queue, input_dir, num_consumers))
    consumer_threads = [
        threading.Thread(target=consumer, args=(task_queue, results_queue, output_dir, i+1))
        for i in range(num_consumers)
    ]
    
    print(f"Producer: Starting processing with {num_consumers} consumers")
    producer_thread.start()
    for t in consumer_threads:
        t.start()
        
    producer_thread.join()
    for t in consumer_threads:
        t.join()
        
    print("\n--------Result--------")
    processed_count = 0
    while not results_queue.empty():
        results_queue.get()
        processed_count += 1
    print(f"Producer: Total processed images: {processed_count}")
