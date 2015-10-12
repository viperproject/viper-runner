__author__ = 'froth'


class RunResult:
    """
    Small value object to store the result of a single run.
    """

    def __init__(self, file_name, config_name):
        self.time_elapsed = -1
        self.input_file = file_name
        self.config_name = config_name
        self.timeout_occurred = False
        self.return_code = 0
