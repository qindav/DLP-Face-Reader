# Benchmark utility
# Matthew Kroesche
# ECEN 404

import time



class Bench(object):

    on = True

    def __init__(self, msg):
        if self.on:
            self.msg = msg

    def __enter__(self):
        if self.on:
            self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args):
        if self.on:
            self.end_time = time.perf_counter()
            print('%s: %f seconds' % (self.msg, self.end_time-self.start_time))
        return False
