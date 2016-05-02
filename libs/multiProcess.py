#!/usr/bin/env python2

#Multiprocessing: https://gist.github.com/baojie/6047780
def chunks(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]

def dispatch_jobs(data, job_number, function, remote=False, in_data=False, split_range=(False,False)):
    import multiprocessing
    total = len(data)
    chunk_size = total / job_number or total
    
    _slice = chunks(data, chunk_size)
    jobs = []

    for s in _slice:
        j = multiprocessing.Process(target=function, args=(s, remote, in_data, split_range))
        jobs.append(j)

    for j in jobs:
        j.start()
    j.join() #Wait process end

def get_cores():
    from multiprocessing import cpu_count
    return cpu_count()
