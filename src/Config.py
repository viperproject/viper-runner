import os
import datetime

__author__ = 'froth'


PLACEHOLDER_DATE = "@date@"
PLACEHOLDER_FILE = "@file@"
PLACEHOLDER_REP = "@rep@"
CURR_DATE = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


def replace_placeholders(string, file_name=PLACEHOLDER_FILE, repetition=PLACEHOLDER_REP, date=CURR_DATE):
    return string.replace(PLACEHOLDER_DATE, date)\
                 .replace(PLACEHOLDER_FILE, file_name)\
                 .replace(PLACEHOLDER_REP, str(repetition))


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
        self.run_configurations = [["../carbon/carbon.bat"]]
        self.ignoreList = []
        self.timeout = 60  # seconds
        self.repetitions = 5
        self.list_files = False
        self.timing_csv_file_name = "timings.txt"
        self.print_output = False

    def print(self):
        print()
        print("Configuration:")
        print("    Run configurations: " + str(self.run_configurations))
        print("    Test folder: " + self.testFolder)
        print("    Ignored tests: " + str(self.ignoreList))
        print("    Timeout: " + str(self.timeout) + " seconds")
        print("    Test repetitions: " + str(self.repetitions))
        print("    CSV file with timings: " + str(os.path.join(os.getcwd(), self.timing_csv_file_name)))
        print("    Print process output: " + str(self.print_output))
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
                        curr_conf = [os.path.normpath(line_splits.pop())]
                        self.run_configurations.append(curr_conf)
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
                        self.list_files = parse_bool(line_splits.pop())
                    elif opt == "arg":
                        # parse argument and add it to the last mentioned run_configuration.
                        arg = line_splits.pop().split(" ", maxsplit=1)
                        idx = len(self.run_configurations)
                        self.run_configurations[idx - 1].extend(arg)
                    elif opt == "timing_csv":
                        self.timing_csv_file_name = line_splits.pop().replace(PLACEHOLDER_DATE, CURR_DATE)
                    elif opt == "print_process_output":
                        self.print_output = parse_bool(line_splits.pop())
                    else:
                        print("Skipping unknown configuration option '" + opt + "'.")

        except IOError:
            print("Unable to read '" + config_file + "'. Resorting to default configuration.")
        print("Done.")


def parse_bool(val):
    if val == "False":
        return False
    else:
        return bool(val)
