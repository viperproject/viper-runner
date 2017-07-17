import os
from src.process_runner import ProcessRunner
from src.config import Config
from src.result import RunResult
from src.result_processor import ResultProcessor

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

    def exec(self, config_file_name):
        self.init_env(config_file_name)
        self.collect_test_files()
        self.print_info()
        self.run_processes()

    def init_env(self, config_file):
        self.config.read_config_file(config_file)

    def analyze(self):
        self.analyzer = ResultProcessor(self.results, self.config)
        self.analyzer.write_result_files()
        self.analyzer.print_summary()

    def print_info(self):
        self.config.print()
        self.print_file_list()

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
        print(str(len(self.files)) + " file(s) included in the benchmark.")
        if self.config.list_files:
            for file in self.files:
                print("    " + file)
        print()

    def run_processes(self):
        """
        Runs all the benchmarks.
        :return: None
        """
        i = 1
        total = len(self.files) * len(self.config.run_configurations) * self.config.repetitions
        for file in self.files:
            for run_config, config_name in zip(self.config.run_configurations, self.config.run_config_names):
                runner = ProcessRunner(run_config, file, config_name, self.config)
                timings = runner.run(i, total)
                self.results.add_results(timings)
                i += self.config.repetitions
