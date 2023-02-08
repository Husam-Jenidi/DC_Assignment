#!/usr/bin/env python
import argparse
import csv
import collections
from random import expovariate

from discrete_event_sim import Simulation, Event


class MMN(Simulation):

    def __init__(self, lambd, mu, n):
        super().__init__()
        self.running = [None] * n  # list to store the ids of running jobs for each server
        self.queue = collections.deque()  # FIFO queue of the system
        self.arrivals = {}  # dictionary mapping job id to arrival time
        self.completions = {}  # dictionary mapping job id to completion time
        self.lambd = lambd  # the arrival rate
        self.n = n  # number of servers in the system
        self.mu = mu  # service rate of the servers
        self.arrival_rate = lambd / n
        self.completion_rate = mu / n
        self.schedule(expovariate(lambd), Arrival(0))

    def schedule_arrival(self, job_id):
        self.schedule(expovariate(self.arrival_rate), Arrival(job_id))

    def schedule_completion(self, job_id, server):
        self.schedule(expovariate(self.completion_rate), Completion(job_id, server))

    @property
    def queue_len(self):
        return len([running for running in self.running if running is not None]) + len(self.queue)

#class of the arrival 
class Arrival(Event):

    def __init__(self, job_id):
        self.id = job_id

    def process(self, sim: MMN):
        sim.arrivals[self.id] = sim.t
        if not any(sim.running):  # if all servers are free, assign the incoming job to a random server and schedule its completion
            server = sim.running.index(None)
            sim.running[server] = self.id
            sim.schedule_completion(self.id, server)
        else:
            sim.queue.append(self.id)
        sim.schedule_arrival(self.id + 1)


class Completion(Event):

    def __init__(self, job_id, server):
        self.id = job_id
        self.server = server

    def process(self, sim: MMN):
        assert sim.running[self.server] is not None
        sim.completions[sim.running[self.server]] = sim.t
        sim.running[self.server] = None  # release the server
        if sim.queue:  # if the queue is not empty, assign the next job to the same server
            next_job = sim.queue.popleft()
            sim.running[self.server] = next_job
            sim.schedule_completion(next_job, self.server)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lambd', type=float, default=0.7)
    parser.add_argument('--mu', type=float, default=1)
    parser.add_argument('--max-t', type=float, default=1_000_000)
    parser.add_argument('--n', type=int, default=2)
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
