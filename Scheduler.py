import sys
import pprint

from prettytable import PrettyTable



# Class to handle queues
class Queue:
    def __init__(self):
        self.items = []

    def is_empty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0, item)

    def get_first_item(self):
        if len(self.items) == 0:
            return None
        return self.items[-1]

    def dequeue(self):
        # Remove NoneTypes from list
        self.items = list(filter(None.__ne__, self.items))

        # If list is length 0, return NoneType
        if len(self.items) == 0:
            return None

        # Get item and return it
        item = self.items.pop()

        # print("Dequeued job temp: " + str(item.number))

        return item

    def size(self):
        return len(self.items)

    def get_items(self):
        return self.items

    def print_queue(self):
        for item in self.items:
            if item is not None:
                print("items include job" + str(item.number))

    def get_shortest_job(self):
        shortest = None

        self.items = list(filter(None.__ne__, self.items))

        # If list is length 0, return NoneType
        if len(self.items) == 0:
            return None

        temp = self.items;

        minruntime = 999999;
        temp.reverse()
        for job in temp:
            if job is not None:
                if job.remainingTime < minruntime :
                    minruntime = job.remainingTime
                    shortest = job

        return shortest

    # get job from a job number if it exists,
    # otherwise return none
    def get_job_from_number(self, number):
        jobFound = None
        for job in self.items:
            if job.number == number:
                jobFound = job
        return jobFound



# Class to represent the system
class System:
    def __init__(self, time, memory, devices, quantum):
        self.startTime = time
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
        self.turnaroundTime = None
        self.weightedTime = None

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
        self.remainingTime = runTime
        self.turnaroundTime = None
        self.weightedTime = None
        self.devicesInUse = 0
        self.location = "just arrived"

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
        #print("Processing line " + line)
        if line[0] == 'C' :
            setup_system(line)
        if line[0] == 'A':
            process_job_arrival(line)
        elif line[0] == 'Q':
            process_request(line)
        elif line[0] == 'L':
            process_release(line)
        elif line[0] == 'D':
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
        # print(time)


# ticks time equal to time difference
def tick_time(timediff):
    global time
    for _ in range(timediff):
        time += 1
        # print("ticking time " + str(time))
        update_processes()
        update_queues()
        # print(time)


# processes an arrived job IN PROGRESS
def process_job_arrival(line):
    global total_system
    args = line_to_args(line)
    currentjob = Job(args[1], args[5], args[0], args[2], args[3], args[4])

    # Do not process jobs if they require more memory or devices than the system has
    if (currentjob.devices > total_system.devices) or (currentjob.memory > total_system.memory):
        return

    # if there is enough memory available to satisfy job req,
    # then we simply add the job to the ready queue

    elif currentjob.memory <= total_system.availableMemory:
        currentjob.location = "Ready Queue"
        total_system.readyqueue.enqueue(currentjob)
        total_system.availableMemory = total_system.availableMemory - currentjob.memory

    # put priority 1 jobs in queue 1, priority 2 in queue 2
    elif currentjob.priority == 1:
        currentjob.location = "Hold Queue 1"
        total_system.holdqueue1.enqueue(currentjob)
    else:

        currentjob.location = "Hold Queue 2"
        total_system.holdqueue2.enqueue(currentjob)


# processes an arrived request
def process_request(line):
    args = line_to_args(line)

    tempjob = None

    # If its the running job, we need to interrupt
    if(total_system.run is not None and total_system.run.number == args[1]):
        tempjob = total_system.run
        total_system.run = None
        print("interrupting job " + str(tempjob.number) + " " + str(tempjob.remainingTime))

    # Otherwise, the job must be in the ready queue
    else:
        tempjob = total_system.readyqueue.get_job_from_number(args[1])

        # If we get None here, then we can't find the job. This is an error
        if tempjob is None:
            print("Could not find job in ready queue or run state to request devices....")
            return

        # Since we found the job, we need to remove if from its position in the readyqueue
        total_system.readyqueue.items.remove(tempjob)

    if(tempjob.devicesInUse + args[2]) > tempjob.devices:
        print("Job is attempting to request more devices than it should")
        return

    tempjob.devicesInUse = args[2]
    # If there is not enough availableDevices, then we add the job to the back of the wait
    if(args[2] > total_system.availableDevices):
        tempjob.location = "Wait Queue"
        total_system.waitqueue.enqueue(tempjob)
        print("Moving to wait queue")

    # Otherwise, we add the job to the ready queue
    else:
        tempjob.location = "Ready Queue"
        total_system.readyqueue.enqueue(tempjob)
        total_system.availableDevices = total_system.availableDevices - args[2]

    print("available devices after device request " + str(total_system.availableDevices))

    print("request processed")


def release_all_devices(job):
    global total_system
    print("before device release " + str(total_system.availableDevices))
    total_system.availableDevices = total_system.availableDevices + job.devicesInUse
    print("after device release " + str(total_system.availableDevices))


def release_all_memory(job):
    global total_system

    total_system.availableMemory = total_system.availableMemory + job.memory


def move_from_wait_queue():
    global total_system

    temp = total_system.waitqueue.items

    temp = list(filter(None.__ne__, temp))

    temp.reverse()

    if(len(temp) == 0):
        return



    for job in temp:
        if job is not None:
            if(job.devicesInUse <= total_system.availableDevices):
                job.location = "Ready Queue"
                total_system.readyqueue.enqueue(job)
                total_system.availableDevices = total_system.availableDevices - job.devicesInUse
                total_system.waitqueue.items.remove(job)
                print("moved job from wait queue")


def move_from_hold_queues():
    move_from_hold1()
    move_from_hold2()


def move_from_hold1():
    global total_system

    item = total_system.holdqueue1.get_shortest_job()

    if item is None:
        return

    if (item.memory <= total_system.availableMemory):
        item.location = "Ready Queue"
        total_system.readyqueue.enqueue(item)
        total_system.holdqueue1.items.remove(item)
        total_system.availableMemory = total_system.availableMemory - item.memory
        print("MOVED job " + str(item.number) + " FROM HOLD 1")


def move_from_hold2():
    global total_system

    item = total_system.holdqueue2.get_first_item()

    if item is None:
        return

    if(item.memory <= total_system.availableMemory):
        item.location = "Ready Queue"
        total_system.readyqueue.enqueue(item)
        total_system.holdqueue2.items.remove(item)
        total_system.availableMemory = total_system.availableMemory - item.memory
        print("MOVED job " + str(item.number) + " FROM HOLD 2")


def release_job(job):
    release_all_devices(job)
    release_all_memory(job)
    move_from_wait_queue()
    move_from_hold_queues()


def process_release(line):
    args = line_to_args(line)

    tempjob = None

    # If its the running job, we need to interrupt
    if (total_system.run is not None and total_system.run.number == args[1]):
        tempjob = total_system.run
        total_system.run = None

    # Otherwise, the job must be in the ready queue
    else:
        tempjob = total_system.readyqueue.get_job_from_number(args[1])

        # If we get None here, then we can't find the job. This is an error
        if tempjob is None:
            print("device release job was either completed or in hold queue")
            return

        # Since we found the job, we need to remove if from its position in the readyqueue
        total_system.readyqueue.items.remove(tempjob)

    print("releasing " + str(args[2]) + "devices")
    total_system.availableDevices = total_system.availableDevices + args[2]
    tempjob.devicesInUse = tempjob.devicesInUse - args[2]

    move_from_wait_queue()


# processes updated IN PROGRESS
def update_processes():
    global total_system

    # If quantum is over,
    if ((time - total_system.startTime) % (total_system.quantum)) == 0:
        # Should update job here
        # print("quantum over, should update job to next job in queue")

        # if total_system.waitqueue:
        runJob = total_system.run
        total_system.run = None
        if runJob is not None:
            runJob.location = "Ready queue"
            total_system.readyqueue.enqueue(runJob)

        jobToRun = total_system.readyqueue.dequeue()
        total_system.run = jobToRun

    # update running process
    if total_system.run is not None:
        currJob = total_system.run
        currJob.location = "CPU"
        currJob.remainingTime = currJob.remainingTime - 1
        # print("running job " + str(currJob.number) + " with " + str(currJob.runTime) + " work units left at time " + str(time))

        if currJob.remainingTime == 0:
            print("done job " + str(currJob.number) + " at time " + str(time))
            total_system.turnaroundTime = time

            currJob.turnaroundTime = time
            currJob.weightedTime = round(time/currJob.runTime, 3)
            total_system.run = None
            release_job(currJob)
            currJob.location = "Complete"
            total_system.completequeue.enqueue(currJob)
            return

        total_system.run = currJob


# checks queue IN PROGRESS
# might be handled in update_processes
def update_queues():
    global total_system


# Setup system with specified args
def setup_system(line):
    global total_system
    args = line_to_args(line)
    total_system = System(args[0], args[1], args[2], args[3])


def display_system(line):
    global total_system
    jobstable = PrettyTable(['Job Number', 'State', 'Time Remaining', 'Turnaround Time', 'Weighted Turnaround Time'])
    newlist = []

    #gathers the jobs from every queue
    for item in total_system.completequeue.items:
        if item is not None:
            newlist.append(item)
    for item in total_system.waitqueue.items:
        if item is not None:
            newlist.append(item)
    for item in total_system.holdqueue2.items:
        if item is not None:
            newlist.append(item)
    for item in total_system.holdqueue1.items:
        if item is not None:
            newlist.append(item)
    for item in total_system.readyqueue.items:
        if item is not None:
            newlist.append(item)
    if total_system.run is not None:
        newlist.append(total_system.run)

    #creates job table sorted by the job number
    newlist.sort(key=lambda x: x.number)
    for item in newlist:
        if item is not None:
            jobstable.add_row([item.number, item.location, item.remainingTime, item.turnaroundTime, item.weightedTime])
    print("------------------------------------------------------------------------------------------------------------------------------------------------")
    print("JOB STATUS")
   # print("------------------------------------------------------------------------------------------------------------------------------------------------")
    print(jobstable)
    print()
    args = line_to_args(line)
    if (args[0] == 9999):
        print("SYSTEM TABLE")
        systemstable = PrettyTable(['System Turnaround Time', "System Weighted Turnaround Time"])
        total_system.weightedTime = round(total_system.turnaroundTime / (total_system.turnaroundTime - total_system.startTime), 3)
        systemstable.add_row([total_system.turnaroundTime, total_system.weightedTime])
        print(systemstable)
    print("------------------------------------------------------------------------------------------------------------------------------------------------")


    #pprint.pprint(total_system)


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
