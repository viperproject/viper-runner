import subprocess
import time, os
from src.config import replace_placeholders

__author__ = 'froth'


class ProcessRunner:
    """
    Runs a benchmark including repetitions.
    """

    def __init__(self, cmd, file, config):
        self.command = list(cmd)
        self.command.append(file)
        self.timeout = config.timeout
        self.repetitions = config.repetitions
        self.print_output = config.print_output
        self.file_name = os.path.basename(file)

    def run(self):
        timings = []
        for i in range(0, self.repetitions):
            # replace placeholders in command
            concrete_command = [replace_placeholders(cmd, self.file_name, i) for cmd in self.command]
            print("Running '" + " ".join(concrete_command) + "' repetition " +
                  str(i + 1) + " of " + str(self.repetitions) + "...")

            try:
                start = time.perf_counter()
                if self.print_output:
                    self.run_with_output(concrete_command)
                else:
                    self.run_without_output(concrete_command)
                end = time.perf_counter()
                exit_condition = "0"
            except subprocess.TimeoutExpired:
                end = time.perf_counter()
                exit_condition = "timeout"
                print("Process was killed due to timeout!")
            except subprocess.CalledProcessError as err:
                end = time.perf_counter()
                exit_condition = str(err.returncode)
                print("Process failed with nonzero exit code!")

            elapsed = end - start
            timings.append((elapsed, exit_condition))
            print("Time elapsed: " + "{:.3f}".format(elapsed) + " seconds")
            print()
        return timings

    def run_with_output(self, cmd):
        subprocess.run(cmd, check=True, timeout=self.timeout)

    def run_without_output(self, cmd):
        subprocess.run(cmd,
                       check=True,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       timeout=self.timeout)
