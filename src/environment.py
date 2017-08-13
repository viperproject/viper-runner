import sys
import time
import os
from src.process_runner import ProcessRunner
from src.config import Config
from src.result import RunResult, SingleRunResult
from src.result_processor import ResultProcessor
from src.getch import getch
from src.util import abort

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
        self.process_stdout_fh = None
        self.process_stderr_fh = None

    def exec(self, config_file_name):
        self._init_env(config_file_name)
        self._collect_test_files()
        self.total_jobs = len(self.files) * len(self.config.get('run_configurations')) * self.config.get('repetitions')
        self.start_time = time.perf_counter()
        self._print_start_info()
        self._check_files_accessible()
        self._open_process_output_files()
        self._run_processes()
        self._close_process_output_files()
        self.end_time = time.perf_counter()

    def _init_env(self, config_file):
        self.config.read_config_file(config_file)

    def analyze(self):
        self.analyzer = ResultProcessor(self.results, self.config)
        self.analyzer.write_result_files()

    def _print_start_info(self):
        self.config.print()
        print("Total number of:")
        print("  configurations = {}".format(len(self.config.get('run_configurations'))))
        print("  repetitions = {}".format(self.config.get('repetitions')))
        print("  files = {}".format(len(self.files)))
        print("  jobs = {}".format(self.total_jobs))
        self._confirm_or_quit()
        self._print_file_list()
        
    def print_end_info(self):
        formattedElapsed = time.strftime("%Hh:%Mm:%Ss", time.gmtime(self.end_time - self.start_time))
        print("Collected " + str(self.results.n_measurements) + " data points")
        print("Elapsed time " + formattedElapsed)

    def _collect_test_files(self):
        """
        Collects all test files: either by recursively searching the specified test folder
        (config option 'test_folder') or by reading the tests line by line from the specified
        file (config option 'test_files_in_file').
        :return: None
        """
        if self.config.get('test_folder', None):
          # Searches recursively in the test folder for .sil and .vpr files.
          # These files are filtered against the ignore list and constitute
          # all programs to be benchmarked.        
          for root, dirs, files in os.walk(self.config.get('test_folder')):
              bench_files = [os.path.normpath(os.path.join(root, f))
                             for f in files 
                             if (f.endswith('.sil') or f.endswith('.vpr'))
                                and not os.path.join(root, f).endswith(tuple(self.config.get('ignore_files', [])))]
              self.files.extend(bench_files)
        elif self.config.get('test_files_in_file', None):
          with open(self.config.get('test_files_in_file')) as fh:
            self.files = fh.readlines()
          self.files = [filename.strip() for filename in self.files]
        else:
          raise Exception("Neither 'test_folder' nor 'test_files_in_file' are set.")

    def _print_file_list(self):
        if self.config.get('list_files'):
            print()
            print("The following files are included in the benchmark:")
            for file in self.files:
                print("    " + file)
            print()
            self._confirm_or_quit()

    def _check_files_accessible(self):
        if self.config.get('check_files_accessible'):
            ok = True
            for file in self.files:
                if not (os.path.isfile(file) and os.access(file, os.R_OK)):
                    print("Cannot access " + file)
                    ok = False
            if not ok:
                abort(1)

    def _open_process_output_files(self):
        if self.config.get('print_output'):
            if self.config.get('stdout_file', None):
                out = self._create_directories_and_open_file(self.config.get('stdout_file'))
            else:
                out = sys.stdout
            if self.config.get('stderr_file', None):
                err = self._create_directories_and_open_file(self.config.get('stderr_file'))
            else:
                err = sys.stderr
        else:
            out = open(os.devnull, 'w')
            err = open(os.devnull, 'w')

        self.process_stdout_fh = out
        self.process_stderr_fh = err

    def _close_process_output_files(self):
        if self.process_stdout_fh != sys.stdout:
            self.process_stdout_fh.close()
        if self.process_stderr_fh != sys.stderr:
            self.process_stderr_fh.close()

    def _create_directories_and_open_file(self, filepath):
        try:
            # Create directories (if necessary)
            if not os.path.exists(os.path.dirname(filepath)):
                os.makedirs(os.path.dirname(filepath))
        
            fh = open(filepath, "w")
        except IOError as err:
            print("Unable to open output file. Aborting.")
            print(err)
            abort(2)

        return fh

    def _run_processes(self):
        """
        Runs all the benchmarks.
        :return: None
        """
        timeout = self.config.get('timeout')
        repetitions = self.config.get('repetitions')
        i = 1
        processed_files = 0
        for file in self.files:
            for run_config in self.config.get('run_configurations'):
                for pre_round_cmd in run_config.get('pre_round_commands', []):
                    print("Executing pre_round_cmd '{}'".format(pre_round_cmd))
                    result = ProcessRunner.run(pre_round_cmd, timeout, self.process_stdout_fh, self.process_stderr_fh)
                    assert not result.timeout_occurred, "Pre-round commands must not time out"

                result = \
                    ProcessRunner.run_as_benchmark(
                        command=run_config.get('command'), 
                        file=file, 
                        config_name=run_config.get('name'),
                        next_job=i,
                        total_jobs=self.total_jobs,
                        repetitions=repetitions,
                        timeout=timeout,
                        stdout_fh=self.process_stdout_fh,
                        stderr_fh=self.process_stderr_fh)

                self.results.add_results(result)
                i += repetitions

                for post_round_cmd in run_config.get('post_round_commands', []):
                    print("Executing post_round_cmd '{}'".format(post_round_cmd))
                    result = ProcessRunner.run(post_round_cmd, timeout, self.process_stdout_fh, self.process_stderr_fh)
                    assert not result.timeout_occurred, "Post-round commands must not time out"

            processed_files += 1

    def _confirm_or_quit(self):
        if self.config.get('confirm_start'):
            print("\nPress Q to quit, any other key to continue ...")
            choice = getch().upper()
            print()
            if choice == "Q":
                abort(0)
