#!/usr/bin/env python
import argparse
import csv
import collections
from random import expovariate

from discrete_event_sim_V01 import Simulation, Event


class MMN(Simulation):

    def __init__(self, lambd, mu, n):
        super().__init__()
        self.running = [None] * n           # list of length n  to store the ids of running jobs for each server and initialized as "None"
        self.queue = collections.deque()     # FIFO this is a deque object stores the ids of jobs that are waiting in the queue to be served.
        self.arrivals = {}  # dictionary maps job ids to their arrivals time
        self.completions = {}  # dictionary maps job ids to their completion time
        self.lambd = lambd  # the arrival rate
        self.mu = mu  # service rate of the servers
        self.n = n  # number of servers in the system
        self.arrival_rate = lambd / n  # arrival rate per server
        self.completion_rate = mu / n  # completion rate per server
        self.schedule(expovariate(lambd), Arrival(0))
        # this schedules the first job arrival event with an arrival time of expovariate(lambd) and job id of (0) by calling
        # the schedule method of the Simulation class.

    def schedule_arrival(self, job_id):
        self.schedule(expovariate(self.arrival_rate), Arrival(job_id))
        # This schedules a new job arrival event with an arrival time of expovariate(self.arrival_rate) and the specified job id.

    def schedule_completion(self, job_id, server):
        self.schedule(expovariate(self.completion_rate), Completion(job_id, server))
        # This schedules a job completion event for the specified job id and server with a completion time of expovariate(self.completion_rate).

    @property
    def queue_len(self):
        _Total_running = [element for element in self.running if element is not None]
        return len(_Total_running) + len(self.queue)

        # This is used to create a read-only attribute queue_len which returns the total number of jobs in the system, including running jobs and jobs in the queue.


# class of the arrival

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
