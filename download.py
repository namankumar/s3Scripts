import multiprocessing
import boto
import os
import sys
import datetime
import logging
import queue

class Downloader(object):

    def __init__(self, download_path, bucket_name, num_processes=2,
                 log_file=None, log_level=logging.INFO):
        self.download_path = download_path
        self.bucket_name = bucket_name
        self.num_processes = num_processes
        if log_file:
            boto.set_file_logger('boto-downloader', log_file, log_level)
        else:
            boto.set_stream_logger('boto-downloader', log_level)
        self.task_queue = multiprocessing.JoinableQueue()
        self.s3 = boto.connect_s3()
        self.bucket = self.s3.lookup(self.bucket_name)
        self.n_tasks = 0
        self.count = 0

    def queue_tasks(self):
        for key in self.bucket:
            self.task_queue.put(key.name)
            self.n_tasks += 1

    def worker(self, input):
        while 1:
            try:
                p_name =  multiprocessing.current_process().name
                key_name = input.get(True, 1)
                dir = key_name.split('/')[0]
                dir = os.path.join(self.download_path, dir)
                path = os.path.join(self.download_path, key_name)
                self.count += 1

                if os.path.exists(path):
                    print('%s file exists, so skipping - %s' %  (p_name, key_name))
                    input.task_done()
                    continue
            
            except queue.Empty:
                boto.log.info('%s has no more tasks' % p_name)
                break
            key = self.bucket.lookup(key_name)

            try:
                if not os.path.exists(dir):
                    os.mkdir(dir)
                    
                def f(x, y):
                    if x < y:
                        #this logic is iffy. The right way to do this is to have sepeate output streams for each thread. Right now, the carriage
                        #return for the most recent thread will overwrite the update from the previous thread. But no biggie, this is just the status 
                        #of what's currently going on
                        
                        #similarly, self.count, is a shared variable across all threads but each thread makes a copy of it only updates it's own copy
                        #so what appears on the screen is actually wrong. But doesn't matter right now since we are downloading a sorted list and 
                        #the progress is obvious by looking at how far down the list we got. The fix is n_tasks - queLength but this doesn't work on macs
                        print('%s  %d of %d KB  -- %d done of %d - %s' % (p_name, x/1000, y/1000, self.count, self.n_tasks, key_name), end='\r')
                    else:
                        print('%s  %d of %d KB  -- %d done of %d - %s' % (p_name, x/1000, y/1000, self.count, self.n_tasks, key_name))

                key.get_contents_to_filename(path, cb=f)
                input.task_done()

            except Exception as e:
                print(p_name + ' Unexpected ERROR: %s, %s, %s, %s' % (sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2], key_name))
                print(p_name + ' ERROR processing %s' % path)
                
    def main(self):
        self.queue_tasks()
        self.start_time = datetime.datetime.now()
        for i in range(self.num_processes):
            multiprocessing.Process(target=self.worker,
                                    args=(self.task_queue,)).start()
        self.task_queue.join()
        self.task_queue.close()
        self.end_time = datetime.datetime.now()
        print('total time = ', (self.end_time - self.start_time))

dload = Downloader('download_path', 's3_bucket', number_of_threads, )
dload.main()
