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
# L = λ * W
# L: Length of the queue
# λ: Arrival rate
# W: Time spent in the system
# load_balancing for the multi queues


class MMN(Simulation):

    def __init__(self, lambd, mu, n):  # lambd is the overall arrival rate for the system,service rate,number of servers in the system
        # if n != 1:
        #     raise NotImplementedError  # extend this to make it work for multiple queues

        super().__init__()
        #self.running = [None] * n  # server can now be running a job, so we need to keep track of the jobs running
                                   # on each server using a list.

       # self.queue = [collections.deque()] * n   # we have n FIFO queue for each server of the system
        self.servers = [{'running': None, 'queue': collections.deque()} for _ in range(n)]
        self.arrivals = {}  # dictionary mapping job id to arrival time
        self.completions = {}  # dictionary mapping job id to completion time
        self.lambd = lambd  # the arrival rate
        self.n = n  # number of servers in the system
        self.mu = mu  # service rate of the servers
        self.arrival_rate = lambd / n  # do I need to delete /n and keep the arrival rate as it is?
        self.completion_rate = mu / n  # do I need to delete /n and keep the completion rate as it is?
        self.schedule(expovariate(lambd), Arrival(0))


    def schedule_arrival(self, job_id):
        # schedule the arrival following an exponential distribution, to compensate the number of queues the arrival
        # time should depend also on "n"
        arrival_time = expovariate(self.lambd)
        server_index = job_id % self.n
        self.schedule(arrival_time, Arrival(job_id, server_index))

    def schedule_completion(self, job_id, server_index):
        # schedule the time of the completion event
        self.schedule(expovariate(self.completion_rate), Completion(job_id, server_index))

    @property
    def queue_len(self):
        return sum([(server['running'] is not None) + len(server['queue']) for server in self.servers])


class Arrival(Event):

    def __init__(self, job_id, server_index):
        self.id = job_id

    def process(self, sim: MMN):
        # set the arrival time of the job
        sim.arrivals[self.id] = sim.t
        # if there is no running job, assign the incoming one and schedule its completion
        if sim.running is None:
            sim.running = self.id
            sim.schedule_completion(self.id)
        # otherwise put the job into the queue
        else:
            sim.queue.append(self.id)
        # schedule the arrival of the next job
        sim.schedule_arrival(self.id + 1)


# manage the completion of the running job and schedule the next job from the queue, if any.
class Completion(Event):
    def __init__(self, job_id, server_index):
        self.id = job_id  # currently unused, might be useful when extending

    def process(self, sim: MMN):
        assert sim.running is not None
        sim.completions[sim.running] = sim.t  # set the completion time of the running job
        # if the queue is not empty
        if sim.queue:
            next_job = sim.queue.popleft()  # get a job from the queue
            sim.running = next_job
            sim.schedule_completion(next_job)  # schedule its completion
        else:
            sim.running = None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lambd', type=float, default=0.7)
    parser.add_argument('--mu', type=float, default=1)
    parser.add_argument('--max-t', type=float, default=1_000_000)
    parser.add_argument('--n', type=int, default=1)
    parser.add_argument('--csv', help="CSV file in which to store results")
    args = parser.parse_args()

    sim = MMN(args.lambd, args.mu, args.n)
    sim.run(args.max_t)

    completions = sim.completions
    W = (sum(completions.values()) - sum(sim.arrivals[job_id] for job_id in completions)) / len(completions)
    print(f"Average time spent in the system: {W}")
    print(f"Theoretical expectation for random server choice: {1 / (1 - args.lambd)}")

    if args.csv is not None:
        with open(args.csv, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([args.lambd, args.mu, args.max_t, W])


if __name__ == '__main__':
    main()
