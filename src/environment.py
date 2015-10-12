import os
from src.process_runner import ProcessRunner
from src.config import Config
from src.filewriter import FileWriter
from src.result import RunResult
from src.result_analyzer import ResultAnalyzer

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
        self.results = {}
        self.analyzer = None

    def exec(self, config_file_name):
        self.init_env(config_file_name)
        self.collect_test_files()
        self.print_info()
        self.run_processes()
        self.finalize()

    def init_env(self, config_file):
        self.config.read_config_file(config_file)
        self.file_writer = FileWriter()
        self.file_writer.init_output_file(self.config.timing_csv_file_name, print_header=True)

        # initialize result collection.
        for name in self.config.run_config_names:
            self.results[name] = RunResult(name)

    def finalize(self):
        self.file_writer.finalize()

    def analyze(self):
        self.analyzer = ResultAnalyzer(self.results, self.config)
        self.analyzer.print_summary()

    def print_info(self):
        self.config.print()
        self.print_file_list()

    def collect_test_files(self):
        """
        Searches recursively in the test folder for .sil files.
        These files are filtered against the ignore list and constitute
        all programs to be benchmarked.
        :return: None
        """
        for root, dirs, files in os.walk(self.config.testFolder):
            bench_files = [os.path.normpath(os.path.join(root, f)) for f in files if f.endswith('.sil') and
                           not os.path.join(root, f).endswith(tuple(self.config.ignoreList))]
            self.files.extend(bench_files)

    def print_file_list(self):
        print(str(len(self.files)) + " file(s) included in the benchmark.")
        if self.config.list_files:
            for file in self.files:
                print("    " + file)
        print()

    def run_processes(self):
        """
        Runs all the benchmarks.
        :return:
        """
        for file in self.files:
            for run_config, config_name in zip(self.config.run_configurations, self.config.run_config_names):
                runner = ProcessRunner(run_config, file, config_name, self.config)
                timings = runner.run()
                self.results[config_name].add_results(timings)
                self.file_writer.add_timing_entry(config_name, timings)
