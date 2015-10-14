from statistics import mean

__author__ = 'froth'


class RunResult:
    """
    Collection of all results for a single run configuration.
    """

    def __init__(self):
        self.file_to_result = {}
        self.file_to_sorted_result = {}
        self.file_to_result_avg = {}
        self.n_measurements = 0
        self.n_timeouts = 0
        self.n_errors = 0

    def add_results(self, single_results):
        for result in single_results:
            self.n_measurements += 1
            if result.timeout_occurred:
                self.n_timeouts += 1
            if result.return_code:
                self.n_errors += 1

            if result.input_file not in self.file_to_result:
                self.file_to_result[result.input_file] = []

            self.file_to_result[result.input_file].append(result)

    def process_timings(self):
        # calculate per config timings and avg.
        for file_name, data in self.file_to_result.items():
            config_to_avg_time = {}
            config_to_time = {}
            # collect all timings required
            for res in data:
                if res.config_name not in config_to_avg_time:
                    config_to_avg_time[res.config_name] = []
                    config_to_time[res.config_name] = []
                config_to_time[res.config_name].append(res)
                config_to_avg_time[res.config_name].append(res.time_elapsed)

            self.file_to_sorted_result[file_name] = config_to_time
            # take the average
            for config_name in config_to_avg_time:
                config_to_avg_time[config_name] = mean(config_to_avg_time[config_name])
            self.file_to_result_avg[file_name] = config_to_avg_time


class SingleRunResult:
    """
    Small value object to store the result of a single run.
    """

    def __init__(self, config_name, file_name):
        self.config_name = config_name
        self.time_elapsed = -1
        self.input_file = file_name
        self.timeout_occurred = False
        self.return_code = 0
