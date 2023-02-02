#!/usr/bin/env python
import argparse
import csv
import collections
from random import expovariate

from discrete_event_sim import Simulation, Event


class MMN(Simulation):

    def __init__(self, lambd, mu, n):
        super().__init__()
        self.servers = [{'running': None, 'queue': collections.deque()} for _ in range(n)]
        self.arrivals = {}
        self.completions = {}
        self.lambd = lambd
        self.mu = mu
        self.n = n
        self.arrival_time = lambd / n
        self.completion_time = mu / n
        self.schedule(expovariate(lambd), Arrival(0, 0))

    def schedule_arrival(self, job_id):
        arrival_time = expovariate(self.arrival_time)
        server_index = job_id % self.n
        self.schedule(arrival_time, Arrival(job_id, server_index))

    def schedule_completion(self, job_id, server_index):
        self.schedule(expovariate(self.completion_time), Completion(job_id, server_index))

    @property
    def queue_len(self):
        return sum([(server['running'] is not None) + len(server['queue']) for server in self.servers])


class Arrival(Event):

    def __init__(self, job_id, server_index):
        self.id = job_id
        self.server_index = server_index

    def process(self, sim: MMN):
        sim.arrivals[self.id] = sim.t
        if sim.servers[self.server_index]['running'] is None:
            sim.servers[self.server_index]['running'] = self.id
            sim.schedule_completion(self.id, self.server_index)
        else:
            sim.servers[self.server_index]['queue'].append(self.id)
        sim.schedule_arrival(self.id + 1)


class Completion(Event):

    def __init__(self, job_id, server_index):
        self.id = job_id
        self.server_index = server_index

    def process(self, sim: MMN):
        assert sim.servers[self.server_index]['running'] is not None
        sim.completions[sim.servers[self.server_index]['running']] = sim.t
        if sim.servers[self.server_index]['queue']:
            next_job = sim.servers[self.server_index]['queue'].popleft()
            sim.servers[self.server_index]['running'] = next_job
            sim.schedule_completion(next_job, self.server_index)
        else:
            sim.servers[self.server_index]['running'] = None


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
