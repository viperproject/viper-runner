__author__ = 'froth'


class ResultAnalyzer:
    """
    Object encapsulationg the logic to make sense of the collected results.
    """

    def __init__(self, results, config):
        self.results = results
        self.config = config

    def print_summary(self):
        print("Collected " + str(len(self.results.file_to_result.values)) + " data points.")
