import sys
import pprint


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

    def pop_shortest_job(self):
        shortest = None

        minruntime = 999999;

        if self.size() == 0:
            return

        for job in self.items.reverse():
            if job.runTime < minruntime :
                minruntime = job.runTime
                shortest = job

        self.items.remove(shortest)

        return shortest



# Class to represent the system
class System:
    def __init__(self, time, memory, devices, quantum):
        self.time = time
        self.memory = memory
        self.availableMemory = memory;
        self.devices = devices
        self.availableDevices = devices
        self.quantum = quantum
        self.holdqueue1 = Queue()
        self.holdqueue2 = Queue()
        self.readyqueue = Queue()
        self.waitqueue = Queue()
        self.completequeue = Queue()
        self.run = None


    # make a job hold the Systems memory
    def hold_memory(self, job):
        self.availableMemory = self.availableMemory - job.memory


    # make a job release the Systems memory
    def release_memory(self, job):
        self.availableMemory = self.availableMemory + job.memory


    # hold devices from job device request
    def hold_devices(self, dvrq):
        self.availableDevices = self.availableDevices - dvrq


    # hold devices from job device release
    def release_devices(self, dvrl):
        self.availableDevices = self.availableDevices + dvrl

    def set_running_job(self, job):
        self.runningJob = job;


# Class to represent a job
class Job:
    def __init__(self, number, priority, arrivalTime, memory, devices, runTime):
        self.number = number
        self.priority = priority
        self.arrivalTime = arrivalTime
        self.memory = memory
        self.devices = devices
        self.runTime = runTime

class Process:
    def __init__(self, job):
        self.job = job


class DeviceRequest:
    def __init__(self, devices):
        self.devices = devices


total_system = System(0, 0, 0, 0)
time = 0
quantumProgress = 0;
interrupted = False


# entry-point
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
        tick(line)
        print("Processing line " + line)
        if line[0] == 'C' :
            print("processing config")
            setup_system(line)
        if line[0] == 'A':
            print("processing job arrival")
            process_job_arrival(line)
        elif line[0] == 'Q':
            print("processing device request")
            process_request(line)
        elif line[0] == 'L':
            print("processing device release")
            process_release(line)
        elif line[0] == 'D':
            print("processing display")
            display_system(line)
        return
    else:
        print("line was invalid .... \"" + line + "\"")


# checks and compares arrival times
def tick(line):
    global time
    args = line_to_args(line)

    if args[0] != time:
        if line[0] == 'C':
            tick_start_time(int(args[0])-time)
        else:
            tick_time(int(args[0])-time)


# ticks time equal to time difference if first received
def tick_start_time(timediff):
    global time
    print("ticking till system start time...")
    for _ in range(timediff):
        time += 1
        print( time)


# ticks time equal to time difference
def tick_time(timediff):
    global time
    for _ in range(timediff):
        time += 1
        update_processes()
        update_queues()
        print(time)


# processes an arrived job IN PROGRESS
def process_job_arrival(line):
    global total_system
    args = line_to_args(line)
    currentjob = Job(args[0], args[1], args[2], args[3], args[4], args[5])

    # Do not process jobs if they require more memory or devices than the system has
    if (currentjob.devices > total_system.devices) or (currentjob.memory > total_system.memory):
        return

    # if there is enough memory available to satisfy job req,
    # then we simply add the job to the ready queue
    elif (currentjob.memory < total_system.availableMemory):
        total_system.readyqueue.enqueue(currentjob)

    # put priority 1 jobs in queue 1, priority 2 in queue 2
    elif currentjob.priority == "1":
        total_system.holdqueue1.enqueue(currentjob)
    else:
        total_system.holdqueue2.enqueue(currentjob)

    print("job processed")


# processes an arrived request IN PROGRESS
def process_request(line):
    print("request processed")


def process_release(line):
    print("release processed")


# processes updated IN PROGRESS
def update_processes():
    global total_system
    if (time % (total_system.quantum + total_system.time)) == 0:
        # Should update job here
        print("quantum over, should update job to next job in queue")

    # update running process
    if total_system.run is not None:
        currJob = total_system.run
        currJob.time = currJob.time - 1

        if currJob.time == 0:
            print("done job")
            total_system.run = None
            total_system.completequeue.enqueue(currJob)
            return

        total_system.run = currJob

    print("processes updated")


# checks queue IN PROGRESS
# might be handled in update_processes
def update_queues():
    global total_system
    print("queues checked")


# Setup system with specified args
def setup_system(line):
    global total_system
    args = line_to_args(line)
    total_system = System(args[0], args[1], args[2], args[3])
    print("System has been set up")


def display_system(line):
    global total_system
    print("CURRENT STATUS OF SYSTEM")
    pprint.pprint(total_system)


# Turn a line with letters/numbers/etc in to an array
# that can be used to fill classes. Produced arrays
# are just the arguments in numbers, each argument
# belonging in its own index and in order
def line_to_args(line):
    stringargs = (''.join(filter(lambda c: c.isdigit() or c == ' ', line))[1:]).split(" ")
    intargs = list(map(int, stringargs))
    return intargs

if __name__ == "__main__":
    main()
