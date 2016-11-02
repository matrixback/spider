#coding: utf-8
'''
线程池的特点：
适用于大量短暂的任务。
需要考虑线程数量，如果数量较少，则并发性能不好，如果数量较多，系统开销较大
对于一般的线程池，
    计算密集型任务：线程个数 = CPU个数
    IO密集型任务：线程个数 > CPU个数
Python 由于由GIL，所以
    对于计算密集型任务，一个进程内的线程共享一个CPU，所以如果要利用多核，则开
    多个进程，进程个数 = CPU个数
'''

# 一个简单的非阻塞线程池，因为任务已经确定，所以非阻塞较好，没有任务时线程自动退出
# 为后面实现动态线程池做铺垫
import Queue
import threading
import time

class WorkManager(object):
    def __init__(self, func, work_num=1000, thread_num=2):
        self.func = func
        self.job_queue = Queue.Queue()
        self.threads = []

        self.__init_work_queue(work_num)
        self.__init_thread_pool(thread_num)


    def __init_thread_pool(self, thread_num):
        for i in range(thread_num):
            self.threads.append(Work(self.func, self.job_queue))

    def __init_work_queue(self, jobs_num):
        for i in range(jobs_num):
            self.add_job(i)

    def add_job(self, *args):
        ''' 添加一项工作入队'''
        self.job_queue.put(list(args))

    def check_queue(self):
        ''' 检查剩余队列'''
        return self.job_queue.qsize()

    def wait_allcomplete(self):
        '''  如果还有线程存活，等待其死亡 '''
        for item in self.threads:
            if item.isAlive():
                item.join()


class Work(threading.Thread):
    def __init__(self, target, work_queue):
        threading.Thread.__init__(self)
        self.target = target
        self.work_queue = work_queue    # 每一个线程都包含这个队列对象
        self.start()

    def run(self):
        while True:
            try:
                args = self.work_queue.get(block=False)
                self.target(args)
                self.work_queue.task_done()
            except Exception as e:
                print(e)
                break

def do_jobs(args):
    print(args)
    time.sleep(2)

if __name__ == '__main__':
    start = time.time()
    work_manager = WorkManager(do_jobs, 10,  10)
    work_manager.wait_allcomplete()
    end = time.time()
    print("cost all time: %s" % (end - start))





