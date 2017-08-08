import os
import shutil
from src.util import replace_placeholders
from pprint import pprint
import shlex


__author__ = 'froth'

class RunConfiguration:
    def __init__(self):
        self.name = ""
        self.main_cmd = []
        self.pre_round_cmds = []
        self.post_round_cmds = []

    def __repr__(self):
        return "RunConfig(name: {}, cmd: {}, pre_round_cmds: {}, post_round_cmds: {})".format(
            repr(self.name), repr(self.main_cmd), repr(self.pre_round_cmds), repr(self.post_round_cmds))

class Config:
    """
    Benchmark configuration object.
    """

    def __init__(self):
        """
        Initializes default config.
        :return: None
        """
        self.testFolder = ""
        self.testFilesInFile = ""
        self.run_configurations = []
        self.ignoreList = []
        self.timeout = None  # seconds > 0 or None
        self.repetitions = 5
        self.list_files = False
        self.check_files_accessible = True
        self.timing_csv_file_name = ""
        self.avg_per_config_timing_csv_file_name = ""
        self.per_config_timing_csv_file_name = ""
        self.print_output = False
        self.stdout_file_name = ""
        self.stderr_file_name = ""
        self.confirm_start = True

    def print(self):
        print()
        print("Configuration:")
        pprint(vars(self), width=80)
        print()

    def read_config_file(self, config_file):
        """
        Parses the configuration file.
        :return: None
        """
        print("Parsing configuration file...")
        try:
            with open(config_file) as configFile:
                # run_config_override = True
                for line in [l for l in [l.strip() for l in configFile] if l and not l.startswith('#')]:
                    line_splits = line.split(" ", maxsplit=1)
                    opt = line_splits.pop(0).strip().lower()

                    # skip invalid option without argument.
                    if not line_splits:
                        print("Ignoring option '" + opt + "' because it is missing the configuration argument.")
                        continue

                    # option parsing
                    if opt == "test_folder":
                        self.testFolder = line_splits.pop()
                    elif opt == "test_files_in_file":
                        self.testFilesInFile = line_splits.pop()                        
                    # elif opt == "run_configuration":
                    #     # override default run configurations
                    #     if run_config_override:
                    #         run_config_override = False
                    #         self.run_configurations = []
                    #         self.run_config_names = []
                    #     curr_conf = [os.path.normpath(line_splits.pop())]
                    #     self.run_configurations.append(curr_conf)
                    #     self.run_config_names.append("run_config_" + str(len(self.run_configurations)))
                    elif opt == "run_configuration":
                        config_name = line_splits.pop()
                        if config_name in [c.name for c in self.run_configurations]:
                            print("Error: Configuration name '" + config_name + "' is not unique.")
                            exit(1)
                        else:
                            configuration = RunConfiguration()
                            configuration.name = config_name
                            self.run_configurations.append(configuration)
                    elif opt == "cmd":
                        parts = shlex.split(line_splits.pop())
                        configuration = self.run_configurations[-1]
                        configuration.main_cmd = parts
                    elif opt == "pre_round_cmd":
                        parts = shlex.split(line_splits.pop())
                        configuration = self.run_configurations[-1]
                        configuration.pre_round_cmds.append(parts)
                    elif opt == "post_round_cmd":
                        parts = shlex.split(line_splits.pop())
                        configuration = self.run_configurations[-1]
                        configuration.post_round_cmds.append(parts)
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
                            if self.timeout <= 0:
                                self.timeout = None
                        except ValueError:
                            print("Error: Unable to parse '" + line_splits[0] + "' as timeout [seconds].")
                    elif opt == "list_files":
                        self.list_files = parse_bool(line_splits.pop())
                    elif opt == "check_files_accessible":
                        self.check_files_accessible = parse_bool(line_splits.pop())
                    elif opt == "timing_csv":
                        self.timing_csv_file_name = replace_placeholders(line_splits.pop())
                    elif opt == "avg_per_config_timing_csv":
                        self.avg_per_config_timing_csv_file_name = replace_placeholders(line_splits.pop())
                    elif opt == "per_config_timing_csv":
                        self.per_config_timing_csv_file_name = replace_placeholders(line_splits.pop())
                    elif opt == "print_process_output":
                        self.print_output = parse_bool(line_splits.pop())
                    elif opt == "stdout_file":
                        self.stdout_file_name = line_splits.pop()
                    elif opt == "stderr_file":
                        self.stderr_file_name = line_splits.pop()
                    elif opt == "confirm_start":
                        self.confirm_start = parse_bool(line_splits.pop())
                    else:
                        print("Skipping unknown configuration option '" + opt + "'.")

        except IOError:
            print("Unable to read '" + config_file + "'. Resorting to default configuration.")

        print("Copying config to output folder...")

        # generate output folder if it does not yet exist
        output_dir = os.path.dirname(self.timing_csv_file_name)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # create file in case it does not yet exist.
        config_copy_filename = os.path.join(output_dir, os.path.basename(config_file))
        open(config_copy_filename, 'a').close()

        # copy content
        shutil.copyfile(config_file, config_copy_filename)
        print("Done.")


def parse_bool(val):
    if val == "False" or val == "0":
        return False
    else:
        return bool(val)
