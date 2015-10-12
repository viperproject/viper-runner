__author__ = 'froth'


class ResultAnalyzer:
    """
    Object encapsulationg the logic to make sense of the collected results.
    """

    def __init__(self, results, config):
        self.results = results
        self.config = config

    def print_summary(self):
        n_results = 0
        for res in self.results.values():
            n_results += len(res.file_to_result.values())
        print("Collected " + str(n_results) + " data points.")
