import sys
import time
import os
from src.process_runner import ProcessRunner
from src.config import Config
from src.result import RunResult, SingleRunResult
from src.result_processor import ResultProcessor
from src.getch import getch

__author__ = 'froth'


class Environment:
    """
    Benchmark environment.

    Responsible for bookkeeping and collecting results.
    """

    def __init__(self):
        self.config = Config()
        self.files = []
        self.file_writer = None
        self.results = RunResult()
        self.analyzer = None
        self.start_time = 0.0
        self.end_time = 0.0
        self.total_jobs = 0

    def exec(self, config_file_name):
        self.init_env(config_file_name)
        self.collect_test_files()
        self.total_jobs = len(self.files) * len(self.config.run_configurations) * self.config.repetitions
        self.start_time = time.perf_counter()
        self.print_start_info()
        self.check_files_accessible()
        self.run_processes()
        self.end_time = time.perf_counter()

    def init_env(self, config_file):
        self.config.read_config_file(config_file)

    def analyze(self):
        self.analyzer = ResultProcessor(self.results, self.config)
        self.analyzer.write_result_files()

    def print_start_info(self):
        self.config.print()
        print("Total number of:")
        print("  configurations = {}".format(len(self.config.run_configurations)))
        print("  repetitions = {}".format(self.config.repetitions))
        print("  files = {}".format(len(self.files)))
        print("  jobs = {}".format(self.total_jobs))
        self.confirm_or_quit()
        self.print_file_list()
        
    def print_end_info(self):
        formattedElapsed = time.strftime("%Hh:%Mm:%Ss", time.gmtime(self.end_time - self.start_time))
        print("Collected " + str(self.results.n_measurements) + " data points")
        print("Elapsed time " + formattedElapsed)

    def collect_test_files(self):
        """
        Collects all test files: either by recursively searching the specified test folder
        (config option 'test_folder') or by reading the tests line by line from the specified
        file (config option 'test_files_in_file').
        :return: None
        """
        if self.config.testFolder != "":
          # Searches recursively in the test folder for .sil and .vpr files.
          # These files are filtered against the ignore list and constitute
          # all programs to be benchmarked.        
          for root, dirs, files in os.walk(self.config.testFolder):
              bench_files = [os.path.normpath(os.path.join(root, f))
                             for f in files 
                             if (f.endswith('.sil') or f.endswith('.vpr'))
                                and not os.path.join(root, f).endswith(tuple(self.config.ignoreList))]
              self.files.extend(bench_files)
        elif self.config.testFilesInFile != "":
          with open(self.config.testFilesInFile) as fh:
            self.files = fh.readlines()
          self.files = [filename.strip() for filename in self.files]
        else:
          raise Exception("Neither 'test_folder' nor 'test_files_in_file' are set.")

    def print_file_list(self):
        if self.config.list_files:
            print()
            print("The following files are included in the benchmark:")
            for file in self.files:
                print("    " + file)
            print()
            self.confirm_or_quit()

    def check_files_accessible(self):
        if self.config.check_files_accessible:
            ok = True
            for file in self.files:
                if not (os.path.isfile(file) and os.access(file, os.R_OK)):
                    print("Cannot access " + file)
                    ok = False
            if not ok:
                exit(1)

    def run_processes(self):
        """
        Runs all the benchmarks.
        :return: None
        """
        i = 1
        processed_files = 0
        for file in self.files:
            for run_config in self.config.run_configurations:
                for pre_round_cmd in run_config.pre_round_cmds:
                    print("Executing pre_round_cmd '{}'".format(pre_round_cmd))
                    # Hacky!
                    runner = ProcessRunner(pre_round_cmd, file, run_config.name, self.config)
                    irrelevant_result = SingleRunResult(run_config.name, file)
                    runner.run_process(pre_round_cmd, file, -1, irrelevant_result)

                runner = ProcessRunner(run_config.main_cmd, file, run_config.name, self.config)
                timings = runner.run(i, self.total_jobs)

                self.results.add_results(timings)
                i += self.config.repetitions

                for post_round_cmd in run_config.post_round_cmds:
                    print("Executing post_round_cmd '{}'".format(post_round_cmd))
                    # Hacky!
                    runner = ProcessRunner(post_round_cmd, file, run_config.name, self.config)
                    irrelevant_result = SingleRunResult(run_config.name, file)
                    runner.run_process(post_round_cmd, file, -1, irrelevant_result)
                
            processed_files += 1

    def confirm_or_quit(self):
        if self.config.confirm_start:
            print("\nPress Q to quit, any other key to continue ...")
            choice = str(getch()).upper()
            print()
            if choice == "Q":
                exit(0)
