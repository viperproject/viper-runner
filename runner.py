import os
import subprocess
import time
import datetime
import argparse

"""
Carbon benchmark script.
Runs tests, measures time and kills processes that take too long.
"""
PLACEHOLDER_DATE = "@date@"
PLACEHOLDER_FILE = "@file@"
PLACEHOLDER_REP = "@rep@"
CURR_DATE = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


class Config:
    """
    Benchmark configuration object.
    """

    def __init__(self):
        """
        Initializes default config.
        :return: None
        """
        self.testFolder = "../silver/src/test/resources/all"
        self.run_configurations = [["carbon.bat"]]
        self.ignoreList = []
        self.timeout = 60  # seconds
        self.repetitions = 5
        self.list_files = False
        self.timing_csv_file_name = "timings.txt"

    def print(self):
        print()
        print("Configuration:")
        print("    Run configurations: " + str(self.run_configurations))
        print("    Test folder: " + self.testFolder)
        print("    Ignored tests: " + str(self.ignoreList))
        print("    Timeout: " + str(self.timeout) + " seconds")
        print("    Test repetitions: " + str(self.repetitions))
        print("    CSV file with timings: " + str(os.path.join(os.getcwd(), self.timing_csv_file_name)))
        print()

    def read_config_file(self, config_file):
        """
        Parses the configuration file.
        :return: None
        """
        print("Parsing configuration file...")
        try:
            with open(config_file) as configFile:
                run_config_override = True
                for line in [l.strip(' \r\n') for l in configFile if l.strip(' \r\n') and not l.startswith('#')]:
                    line_splits = line.split(" ", maxsplit=1)
                    opt = line_splits.pop(0).strip()

                    # skip invalid option without argument.
                    if not line_splits:
                        print("Ignoring option '" + opt + "' because it is missing the configuration argument.")
                        continue

                    # option parsing
                    if opt == "test_folder":
                        self.testFolder = line_splits.pop()
                    elif opt == "run_configuration":
                        # override default run configurations
                        if run_config_override:
                            run_config_override = False
                            self.run_configurations = []
                        self.run_configurations.append(line_splits)
                    elif opt == "ignore":
                        # normalize path separators, so that filtering works correctly
                        self.ignoreList.append(os.path.normpath(line_splits.pop()))
                    elif opt == "repetitions":
                        try:
                            self.repetitions = int(line_splits[0])
                        except ValueError:
                            print("Error: Unable to parse '" + line_splits[0] + "' as number of test repetitions.")
                    elif opt == "timeout":
                        try:
                            self.timeout = int(line_splits[0])
                        except ValueError:
                            print("Error: Unable to parse '" + line_splits[0] + "' as timeout [seconds].")
                    elif opt == "list_files":
                        if line_splits[0] == "False":
                            self.list_files = False
                        else:
                            self.list_files = bool(line_splits[0])
                    elif opt == "arg":
                        # parse argument and add it to the last mentioned run_configuration.
                        arg = line_splits.pop().split(" ", maxsplit=1)
                        idx = len(self.run_configurations)
                        self.run_configurations[idx - 1].extend(arg)
                    elif opt == "timing_csv":
                        self.timing_csv_file_name = line_splits.pop().replace(PLACEHOLDER_DATE, CURR_DATE)
                    else:
                        print("Skipping unknown configuration option '" + opt + "'.")

        except IOError:
            print("Unable to read '" + config_file + "'. Resorting to default configuration.")
        print("Done.")


class BenchRunner:
    """
    Runs a benchmark including repetitions.
    """

    def __init__(self, config, file, timeout, repetitions):
        self.command = list(config)
        self.command.append(file)
        self.timeout = timeout
        self.repetitions = repetitions
        self.file_name = os.path.basename(file)

    def run(self):
        timings = []
        for i in range(0, self.repetitions):
            # replace placeholders in command
            concrete_command = [replace_placeholders(cmd, self.file_name, i) for cmd in self.command]
            print("Running '" + " ".join(concrete_command) + "' repetition " +
                  str(i + 1) + " of " + str(self.repetitions) + "...")

            start = time.perf_counter()
            try:
                subprocess.run(concrete_command,
                               check=True,
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL,
                               timeout=self.timeout)
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


class BenchEnvironment:
    """
    Benchmark environment.

    Responsible for bookkeeping and collecting results.
    """

    def __init__(self):
        self.config = Config()
        self.files = []
        self.file_writer = None

    def init_env(self, config_file):
        self.config.read_config_file(config_file)
        self.file_writer = FileWriter(self.config.timing_csv_file_name)
        self.file_writer.init_csv_timings()

    def finalize(self):
        self.file_writer.finalize()

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

    def run_benchmark(self):
        """
        Runs all the benchmarks.
        :return:
        """
        for file in self.files:
            for run_config in self.config.run_configurations:
                runner = BenchRunner(run_config, file, self.config.timeout, self.config.repetitions)
                timings = runner.run()
                self.file_writer.add_timing_entry(timings, file, run_config)


class FileWriter:
    """
    Writes the various result files of the benchmark.
    """

    def __init__(self, csv_timings_file_name):
        self.csv_timings = csv_timings_file_name
        self.csv_header = "runtime [s], input file, run configuration, exit condition"
        self.csv_timings_file = None

    def finalize(self):
        self.csv_timings_file.close()

    def init_csv_timings(self):
        try:
            self.csv_timings_file = open(os.path.join(os.getcwd(), self.csv_timings), "w+")
            print(self.csv_header, file=self.csv_timings_file)
        except IOError:
            print("Unable to open file '" + self.csv_timings + "'. Aborting.")
            exit(-1)

    def add_timing_entry(self, timings, input_file, run_config):
        try:
            for (t, exit_condition) in timings:
                # writes all the timing triplets (timing, file, command)
                print(", ".join([str(t), input_file, " ".join(run_config), exit_condition]),
                      file=self.csv_timings_file, flush=True)
        except IOError:
            print("Unable to write to file '" + self.csv_timings + "'. Aborting.")
            exit(-1)


def print_header():
    print()
    print("Viper tool chain analysis script")
    print("--------------------------------")
    print()


def replace_placeholders(string, file_name, repetition):
    return string.replace(PLACEHOLDER_DATE, CURR_DATE)\
                 .replace(PLACEHOLDER_FILE, file_name)\
                 .replace(PLACEHOLDER_REP, str(repetition))


parser = argparse.ArgumentParser(description='Viper tool chain analysis script.')
parser.add_argument('config_file', help='the configuration file for this script.')
args = parser.parse_args()
print_header()
env = BenchEnvironment()
env.init_env(args.config_file)
env.collect_test_files()
env.print_info()
env.run_benchmark()
env.finalize()
