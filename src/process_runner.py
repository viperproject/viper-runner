import subprocess
import time
import datetime
import os
import psutil

from src.util import replace_placeholders
from src.run_result import RunResult

__author__ = 'froth'


class ProcessRunner:
    """
    Runs a benchmark including repetitions.
    """

    def __init__(self, cmd, file, config_name, config):
        self.command = list(cmd)
        self.command.append(file)
        self.config = config
        self.file = file
        self.config_name = config_name

    def run(self):
        results = []
        for i in range(0, self.config.repetitions):
            # replace placeholders in command
            concrete_command = [replace_placeholders(cmd, file=self.file, repetition=i, config_name=self.config_name)
                                for cmd in self.command]

            print(datetime.datetime.now().strftime("%d.%m.%Y, %H:%M:%S") + ": running next job, repetition " +
                  str(i + 1) + " of " + str(self.config.repetitions) + "...")
            print("Command: '" + " ".join(concrete_command))

            curr_result = RunResult(self.file, self.config_name)
            self.run_process(concrete_command, self.file, i, curr_result)

            results.append(curr_result)
            print()
            print("Time elapsed: " + "{:.3f}".format(curr_result.time_elapsed) + " seconds")
            print()
        return results

    def run_process(self, cmd, file, repetition, result):
        stdout_output, stderr_output = self.get_process_output(file, repetition)

        # run the actual process
        start = time.perf_counter()
        process = subprocess.Popen(cmd, stdout=stdout_output, stderr=stderr_output)
        try:
            result.return_code = process.wait(timeout=self.config.timeout)
        except subprocess.TimeoutExpired:
            result.timeout_occurred = True
            # kill process and all its children
            parent = psutil.Process(process.pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()
            print("Process was killed due to timeout!")
        finally:
            end = time.perf_counter()

            # close files again, if they were opened
            if self.config.stdout_file_name:
                stdout_output.close()
            if self.config.stderr_file_name:
                stderr_output.close()
        result.time_elapsed = end-start

    def get_process_output(self, file, repetition):
        # generate file names for output files.
        curr_stdout_file_name = replace_placeholders(self.config.stdout_file_name,
                                                     file=file,
                                                     repetition=repetition,
                                                     config_name=self.config_name)
        curr_stderr_file_name = replace_placeholders(self.config.stderr_file_name,
                                                     file=file,
                                                     repetition=repetition,
                                                     config_name=self.config_name)
        if self.config.print_output:
            stdout_output = None
            stderr_output = None
        else:
            stdout_output = subprocess.DEVNULL
            stderr_output = subprocess.DEVNULL
        try:
            # generate files / folders, if not existing
            if curr_stdout_file_name:
                if not os.path.exists(os.path.dirname(curr_stdout_file_name)):
                    os.makedirs(os.path.dirname(curr_stdout_file_name))
                stdout_output = open(curr_stdout_file_name, "w+")

            if curr_stderr_file_name:
                if not os.path.exists(os.path.dirname(curr_stderr_file_name)):
                    os.makedirs(os.path.dirname(curr_stderr_file_name))
                stderr_output = open(curr_stderr_file_name, "w+")
        except IOError as err:
            print("Unable to open output file. Aborting.")
            print(err)
            exit(-1)
        return stdout_output, stderr_output
