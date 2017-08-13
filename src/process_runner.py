import subprocess
import time
import datetime
import os
import psutil

from src.util import replace_placeholders
from src.result import SingleRunResult

class ProcessRunnerResult:
    def __init__(self):
        self.timeout_occurred = None
        self.return_code = None
        self.time_elapsed = None

class ProcessRunner:
    @staticmethod
    def run_as_benchmark(command, file, config_name, next_job, total_jobs, repetitions, timeout, stdout_fh, stderr_fh):
        run_results = []

        for i in range(0, repetitions):
            # Replace placeholders in command
            concrete_command = \
                [replace_placeholders(part, file=file, repetition=i, config_name=config_name)
                 for part in command]

            # Print information about next repetition
            print(datetime.datetime.now().strftime("%d.%m.%Y, %H:%M:%S") +
                  ": running job " + str(next_job + i) +
                  " of " + str(total_jobs) + ", repetition " +
                  str(i + 1) + " of " + str(repetitions) + "...")
            print("Command: '" + " ".join(concrete_command))

            # Run command to benchmark
            process_result = ProcessRunner.run(concrete_command, timeout, stdout_fh, stderr_fh)

            # Create and initialize a run result, and append it to the list of recorded run results
            run_result = SingleRunResult(config_name, file)

            run_result.timeout_occurred = process_result.timeout_occurred
            run_result.return_code = process_result.return_code
            run_result.time_elapsed = process_result.time_elapsed

            run_results.append(run_result)

            print()
            print("Time elapsed: " + "{:.3f}".format(run_result.time_elapsed) + " seconds")
            print()

        return run_results

    @staticmethod
    def run(command, timeout, stdout_fh, stderr_fh):
        return_code = -1
        timeout_occurred = False
        start_time = time.perf_counter()
        
        # Run the actual process
        process = subprocess.Popen(command, stdout=stdout_fh, stderr=stderr_fh)
        try:
            return_code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timeout_occurred = True
            
            # Kill process and all its children
            try:
                parent = psutil.Process(process.pid)
                for child in parent.children(recursive=True):
                    child.kill()
                parent.kill()
                print("Process was killed due to timeout!")
            except psutil.NoSuchProcess:
                # Ignore this exception: it just means that the process barely made it
                pass
            except psutil.AccessDenied:
                # Ignore this exception
                pass
        finally:
            end_time = time.perf_counter()

        process_result = ProcessRunnerResult()
        process_result.return_code = return_code
        process_result.timeout_occurred = timeout_occurred
        process_result.time_elapsed = end_time - start_time

        return process_result
