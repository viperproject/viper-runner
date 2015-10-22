import os

__author__ = 'froth'


class FileWriter:
    """
    Writes the various result files of the benchmark.
    """

    def __init__(self, filename):
        self.filename = filename
        self.file_open = False
        self.file = None

    def open_file(self):
        try:
            directory = os.path.dirname(self.filename)
            if directory and not os.path.exists(directory):
                os.makedirs(os.path.dirname(self.filename))
            self.file = open(self.filename, "w+")
            self.file_open = True
        except IOError as err:
            print("Unable to open file '" + self.filename + "'.")
            print("Error: " + str(err))

            self.file_open = False
            if self.file:
                self.file.close()

    def finalize(self):
        try:
            self.file.close()
        except IOError as e:
            # clean up failed, nothing we can do about it
            pass

    def write_line(self, line):
        if not self.file_open:
            self.open_file()
        print(line, file=self.file, flush=True)

    def write_raw(self, line):
        if not self.file_open:
            self.open_file()
        self.file.write(line)

    def write_csv_data(self, data):
        length = 0
        if data:
            length = len(data[0])
        for values in data:
            if len(values) != length:
                raise IOError("Inconsistent data length, invalid CSV data.")
            self.write_line(";".join(values))

    def __enter__(self):
        if not self.file_open:
            self.open_file()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finalize()
        return True
