import os

__author__ = 'froth'


class FileWriter:
    """
    Writes the various result files of the benchmark.
    """

    def __init__(self, csv_timings_file_name):
        self.csv_timings_file_name = csv_timings_file_name
        self.csv_header = "runtime [s], input file, run configuration, exit condition"
        self.csv_timings_file = None

    def finalize(self):
        self.csv_timings_file.close()

    def init_csv_timings(self):
        try:
            if not os.path.exists(os.path.dirname(self.csv_timings_file_name)):
                os.makedirs(os.path.dirname(self.csv_timings_file_name))
            self.csv_timings_file = open(os.path.join(os.getcwd(), self.csv_timings_file_name), "w+")
            print(self.csv_header, file=self.csv_timings_file)
        except IOError:
            print("Unable to open file '" + self.csv_timings_file_name + "'. Aborting.")
            exit(-1)

    def add_timing_entry(self, timings, input_file, run_config):
        try:
            for (t, exit_condition) in timings:
                # writes all the timing triplets (timing, file, command)
                print(", ".join([str(t), input_file, " ".join(run_config), exit_condition]),
                      file=self.csv_timings_file, flush=True)
        except IOError:
            print("Unable to write to file '" + self.csv_timings_file_name + "'. Aborting.")
            exit(-1)
