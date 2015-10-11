import subprocess
import time
import datetime
import os

from src.util import replace_placeholders

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
        timings = []
        for i in range(0, self.config.repetitions):
            # replace placeholders in command
            concrete_command = [replace_placeholders(cmd, file=self.file, repetition=i, config_name=self.config_name)
                                for cmd in self.command]

            print(datetime.datetime.now().strftime("%d.%m.%Y, %H:%M:%S") + ": running next job, repetition " +
                  str(i + 1) + " of " + str(self.config.repetitions) + "...")
            print("Command: '" + " ".join(concrete_command))

            try:
                if self.config.print_output:
                    elapsed = self.run_with_output(concrete_command, self.file, i)
                else:
                    elapsed = self.run_without_output(concrete_command)
                exit_condition = "0"
            except subprocess.TimeoutExpired:
                exit_condition = "timeout"
                elapsed = self.config.timeout
                print("Process was killed due to timeout!")
            except subprocess.CalledProcessError as err:
                exit_condition = str(err.returncode)
                elapsed = -1
                print("Process failed with nonzero exit code!")

            timings.append((elapsed, exit_condition))
            print()
            print("Time elapsed: " + "{:.3f}".format(elapsed) + " seconds")
            print()
        return timings

    def run_without_output(self, cmd):
        start = time.perf_counter()
        subprocess.run(cmd,
                       check=True,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       timeout=self.config.timeout)
        end = time.perf_counter()
        return end - start

    def run_with_output(self, cmd, file, repetition):
        if self.config.output_file_name:
            # write stdout of subprocess to file
            curr_file_name = replace_placeholders(self.config.output_file_name, file=file, repetition=repetition,
                                                  config_name=self.config_name)
            try:
                if not os.path.exists(os.path.dirname(curr_file_name)):
                    os.makedirs(os.path.dirname(curr_file_name))
                start = time.perf_counter()
                with open(curr_file_name, "w+") as f:
                    subprocess.call(cmd, stdout=f, stderr=subprocess.STDOUT, timeout=self.config.timeout)
                #  output = subprocess.check_output(cmd, timeout=self.config.timeout, universal_newlines=True)
            except IOError:
                print("Unable to open file '" + curr_file_name + "'. Aborting.")
            finally:
                end = time.perf_counter()
        else:
            start = time.perf_counter()
            subprocess.run(cmd,
                           check=True,
                           timeout=self.config.timeout)
            end = time.perf_counter()
        return end - start
