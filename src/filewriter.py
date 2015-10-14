import os

__author__ = 'froth'


class FileWriter:
    """
    Writes the various result files of the benchmark.
    """

    def __init__(self, filename, header=None):
        self.file = None
        try:
            if not os.path.exists(os.path.dirname(filename)):
                os.makedirs(os.path.dirname(filename))
            self.file = open(filename, "w+")
            if header:
                self.write_line(header)
        except IOError:
            print("Unable to open file '" + filename + "'. Aborting.")
            exit(-1)

    def finalize(self):
        self.file.close()

    def write_line(self, line):
        try:
            print(line, file=self.file, flush=True)
        except IOError:
            print("Unable to write to file '" + self.file.name + "'. Aborting.")
            exit(-1)

    def write_raw(self, line):
        try:
            self.file.write(line)
        except IOError:
            print("Unable to write to file '" + self.file.name + "'. Aborting.")
            exit(-1)
