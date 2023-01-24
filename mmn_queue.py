#!/usr/bin/env python

import argparse
import csv
import collections
from random import expovariate

from discrete_event_sim import Simulation, Event

# To use weibull variates, for a given set of parameter do something like
# from weibull import weibull_generator
# gen = weibull_generator(shape, mean)
#
# and then call gen() every time you need a random variable


class MMN(Simulation):

    def __init__(self, lambd, mu, n):
        if n != 1:
            raise NotImplementedError  # extend this to make it work for multiple queues

        super().__init__()
        self.running = None  # if not None, the id of the running job
        self.queue = collections.deque()  # FIFO queue of the system
        self.arrivals = {}  # dictionary mapping job id to arrival time
        self.completions = {}  # dictionary mapping job id to completion time
        self.lambd = lambd
        self.n = n
        self.mu = mu
        self.arrival_rate = lambd / n
        self.completion_rate = mu / n
        self.schedule(expovariate(lambd), Arrival(0))

    def schedule_arrival(self, job_id):
        # schedule the arrival following an exponential distribution, to compensate the number of queues the arrival
        # time should depend also on "n"
        self.schedule(expovariate(self.arrival_rate), Arrival(job_id))

    def schedule_completion(self, job_id):
        # schedule the time of the completion event
        self.schedule(expovariate(self.completion_rate), Completion(job_id))

    @property
    def queue_len(self):
        return (self.running is None) + len(self.queue)
