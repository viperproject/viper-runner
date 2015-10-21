import os

__author__ = 'froth'


class FileWriter:
    """
    Writes the various result files of the benchmark.
    """

    def __init__(self, filename, header=None):
        self.filename = filename
        directory = os.path.dirname(self.filename)
        if directory and not os.path.exists(directory):
            os.makedirs(os.path.dirname(self.filename))
        self.file = open(self.filename, "w+")
        if header:
            self.write_line(header)

    def finalize(self):
        self.file.close()

    def write_line(self, line):
        print(line, file=self.file, flush=True)

    def write_raw(self, line):
        self.file.write(line)

    def __enter__(self):
        pass  # nothing to do here

    def __exit__(self, exc_type, exc_val, exc_tb):
        err = None
        try:
            self.finalize()
        except IOError as e:
            # clean up failed, nothing we can do about it
            err = e
        if exc_type or exc_val or exc_tb or err:
            print("Error writing to file '" + self.filename + "'. ")
            print(str(exc_type) + ", " + str(exc_val) + ", " + str(exc_tb) + ", " + str(err))
        return True
