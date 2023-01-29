# importing the needed libraries for implementing the queueing system
import logging
import heapq

# This will configure the logger to print log messages at the "info" level to the console.
logging.basicConfig(level=logging.INFO)


class EventQueue:
    def __init__(self):  # constructor method, initialize the attributes of the class when an object is created from it.
        self.queue = []

    def push(self, event, priority):  # add event function
        heapq.heappush(self.queue, (priority, event))

    def pop(self):  # pull event function
        return heapq.heappop(self.queue)[1]

    def is_empty(self):
        return len(self.queue) == 0

    def print_events(self):
        for event in self.queue:
            print(event[1])  # event[1] is the event object, event[0] is the priority


class Simulation:
    """Subclass this to represent the simulation state.

    Here, self.t is the simulated time and self.events is the event queue.
    """

    def __init__(self):
        """Extend this method with the needed initialization.

        You can call super().__init__() there to call the code here.
        """
        self.t = 0  # simulated time
        self.events = EventQueue()  # set up self.events as an empty queue

    def schedule(self, delay, event):
        """Add an event to the event queue after the required delay."""
        event.priority = self.t + delay
        self.events.push(event, event.priority)  # add event to the queue at time self.t + delay

    def run(self, max_t=float('inf')):
        """Run the simulation. If max_t is specified, stop it at that time. If max_t is not specified,
         it defaults to infinity which means it will run until the event queue is empty """
        while not self.events.is_empty():  # as long as the event queue is not empty
            event = self.events.pop()   # pull the event from the queue
            if self.t > max_t:
                break
            self.t = event.priority
            event.process(self)

    def log_info(self, msg):
        logging.info(f'{self.t:.2f}: {msg}')


class Event:
    """
    Subclass this to represent your events.

    You may need to define __init__ to set up all the necessary information.
    """
    def __init__(self, name, duration, callback):
        self.name = name
        self.duration = duration
        self.callback = callback
        # self.priority = None

    def process(self, sim1):
        sim1.log_info(f'Started {self.name}')
        # sim1.schedule(self.duration, EndEvent(self.name, self.callback))
        self.callback()
        sim1.log_info(f'Ended {self.name}')

#
# class EndEvent(Event):
#     def __init__(self, name, callback):
#         super().__init__(name, 0, callback)
#
#     def process(self, sim1):
#         sim1.log_info(f'Ended {self.name}')

    # raise NotImplementedError, it didn't work
    # Example of how to use the simulation


def my_callback():
    print("Event finished")


# quu = EventQueue()
# quu.push("test1", 2)
# quu.push("test2", 3)
# quu.push("test3", 1)
# print(quu.is_empty())
# quu.print_events()
# quu.pop()
# quu.pop()
# print(quu.is_empty())
# quu.print_events()
#
# sim = Simulation()
# event1 = Event("Event 1", 5, my_callback)
# sim.schedule(5, event1)
# sim.run()
