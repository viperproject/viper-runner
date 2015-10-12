from statistics import mean

__author__ = 'froth'


class RunResult:
    """
    Collection of all results for a single run configuration.
    """

    def __init__(self, config_name):
        self.config_name = config_name
        self.file_to_result = {}
        self.n_timeouts = 0
        self.n_errors = 0

    def add_results(self, single_results):
        for result in single_results:
            if result.timeout_occurred:
                self.n_timeouts += 1
            if result.return_code:
                self.n_errors += 1
            self.file_to_result[result.input_file] = result

    def get_average_runtime_per_file(self):
        result = {}
        for file_name, data in self.file_to_result:
            timings = [x.time_elapsed for x in data if not x.timeout_occurred and not x.return_code]
            result[file_name] = mean(timings)
        return result


class SingleRunResult:
    """
    Small value object to store the result of a single run.
    """

    def __init__(self, file_name):
        self.time_elapsed = -1
        self.input_file = file_name
        self.timeout_occurred = False
        self.return_code = 0
