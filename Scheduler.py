import sys
import string

# Class to handle queues
class Queue:
    def __init__(self):
        self.items = []

    def is_empty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0, item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)

    def get_items(self):
        return self.items

# Class to represent the system
class System:
    def __init__(self, time, memory, devices, quantum):
        self.time = time
        self.memory = memory
        self.devices = devices
        self.quantum = quantum
        self.holdqueue1 = Queue()
        self.holdqueue2 = Queue()
        self.readyqueue = Queue()
        self.waitqueue = Queue()
        self.completequeue = Queue()

# Class to represent a job
class Job:
    def __init__(self, number, priority, arrivalTime, memory, devices, runTime):
        self.number = number
        self.priority = priority
        self.arrivalTime = arrivalTime
        self.memory = memory
        self.devices = devices
        self.runTime = runTime

total_system = System(0, 0, 0, 0)

time = 0

# entrypoint
def main():
    global time
    # my code here
    print("Starting scheduler")

    file = sys.argv[1]
    print("Running scheduler with file = " + sys.argv[1])
    print(time);
    with open(file) as lines:
        for line in lines:
            process(line)

    print("Scheduler is done")

# Dispatch function to handle all lines
def process(line):
    parameters = ['C', 'A', 'Q', 'L', 'D']
    if line[0] in parameters:

        check(line)
        print("Processing line " + line)
        if line[0] == 'C' :
            print("processing config")
            setup_system(line)

        if line[0] == 'A':

            print("processing job arrival")

        elif line[0] == 'Q':

            print("processing device request")

        elif line[0] == 'L':
            print("processing device release")

        elif line[0] == 'D':
            print("processing display")

        return
    else:
        print("line was invalid .... \"" + line + "\"")

# checks and compares arrival times
def check(line):
    global time
    args = line_to_args(line)

    if args[0] != time:
        if line[0] == 'C':
            tick_start_time(int(args[0])-time)
        else:
            tick_time(int(args[0])-time)

##ticks time equal to time difference if first received
def tick_start_time(timediff):
    global time
    for _ in range(timediff):
        time += 1
        print(time)

#ticks time equal to time difference
def tick_time(timediff):
    global time
    for _ in range(timediff):
        time+=1
        updateprocesses()
        checkqueue()
        print(time)


#processes an arrived job IN PROGRESS
def processjobarrival(line):
    print("job processed")

#processes an arrived request IN PROGRESS
def processrequest(line):
    print("request processed")

#processes updated IN PROGRESS
def updateprocesses():
    print("processes updated")

#checks queue IN PROGRESS
def checkqueue():
    print("queue checked")

# Setup system with specified args
def setup_system(line):
    global total_system
    args = line_to_args(line)
    total_system = System(args[0], args[1], args[2], args[3])
    print("System has been set up")


def display_system(line):
    print("CURRENT STATUS OF SYSTEM")

# Turn a line with letters/numbers/etc in to an array
# that can be used to fill classes. Produced arrays
# are just the arguments in numbers, each argument
# belonging in its own index and in order
def line_to_args(line):
    return (''.join(filter(lambda c: c.isdigit() or c == ' ', line))[1:]).split(" ")

if __name__ == "__main__":
    main()