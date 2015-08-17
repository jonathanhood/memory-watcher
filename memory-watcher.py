import argparse
import os
import time
import shlex
import subprocess

class MemoryReadException(Exception):
    pass

def process_status_path(pid):
    return os.path.join("/proc", str(pid), "status")

def read_status_file(pid):
    with open(process_status_path(pid), "r") as status_file:
        return status_file.readlines()
    raise MemoryReadException()

def read_mem(pid):
    status_lines = [ line.split(":") for line in read_status_file(pid) ]
    status = { key.strip() : value.strip() for (key,value) in status_lines }
    return (status["VmSize"], status["VmRSS"])

def monitor_process(proc, output_file, interval_secs):
    results = []
    while True:
        proc.poll()
        if proc.returncode is None:
            try:
                usage = read_mem(proc.pid)
                results.append( (time.time(), usage[0], usage[1]) )
                time.sleep(interval_secs)
            except:
                pass
        else:
            break 

    report = "time,vmsize,rss\n"
    for result in results:
        report += "{},{},{}\n".format(result[0],result[1],result[2])

    with open(output_file, "w") as report_file:
        report_file.write(report)
    
    return 

def start_and_monitor_process(command, output_file, interval_secs):
    proc = subprocess.Popen(shlex.split(command))
    print proc.pid
    monitor_process(proc, output_file, interval_secs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-file", default="report.csv")
    parser.add_argument("--interval-secs", type=float, default=1.0)
    parser.add_argument("command")
    args = parser.parse_args()
    start_and_monitor_process(args.command, args.output_file, args.interval_secs)

