from src.filewriter import FileWriter

__author__ = 'froth'


class ResultProcessor:
    """
    Object encapsulation the logic to make sense of the collected results.
    """

    def __init__(self, run_result, config):
        self.run_result = run_result
        self.config = config
        self.csv_timings_raw_writer = None
        if config.timing_csv_file_name:
            self.csv_timings_raw_writer = FileWriter(self.config.timing_csv_file_name,
                                                     header="runtime [s];"
                                                            " input file;"
                                                            " run configuration;"
                                                            " exit code;"
                                                            " timeout")
        self.csv_timings_per_config_writer = None
        if config.per_config_timing_csv_file_name:
            header = list(config.run_config_names)
            header.sort()
            header = [[name + ", runtime [s]", name + ", exit condition", name + ", timeout"] for name in header]
            # flatten
            header = [string for cfg_header in header for string in cfg_header]
            header.insert(0, "input file")
            header = ";".join(header)
            self.csv_timings_per_config_writer = FileWriter(self.config.per_config_timing_csv_file_name, header=header)
        self.csv_timings_cfg_avg_writer = None
        if config.avg_per_config_timing_csv_file_name:
            header = list(config.run_config_names)
            header.sort()
            header = [name + ", average runtime [s]" for name in header]
            header.insert(0, "input file")
            header = ";".join(header)
            self.csv_timings_cfg_avg_writer = FileWriter(self.config.avg_per_config_timing_csv_file_name, header=header)
        self.run_result.process_timings()

    def print_summary(self):
        print("Collected " + str(self.run_result.n_measurements) + " data points.")

    def write_result_files(self):
        """
        Writes the various result files.
        """
        if self.csv_timings_raw_writer:
            self.write_result_csv()

        if self.csv_timings_per_config_writer:
            self.writer_per_config_file()

    def write_result_csv(self):
        try:
            with FileWriter(self.config.timing_csv_file_name, header="runtime [s];"
                                                                     " input file;"
                                                                     " run configuration;"
                                                                     " exit code;"
                                                                     " timeout") as writer:
                for results_per_file in self.run_result.file_to_result.values():
                    for result in results_per_file:
                        writer.write_line(";".join([str(result.time_elapsed),
                                                    result.input_file,
                                                    result.config_name,
                                                    str(result.return_code),
                                                    str(result.timeout_occurred)]))
        except IOError:
            print("Error writing to file '" + self.config.timing_csv_file_name + "'. ")

    def writer_per_config_file(self):
        # Assemble file header
        header = list(self.config.run_config_names)
        header.sort()
        header = [[name + ", runtime [s]", name + ", exit condition", name + ", timeout"] for name in header]
        # flatten
        header = [string for cfg_header in header for string in cfg_header]
        header.insert(0, "input file")
        header = ";".join(header)

        config_names = self.config.run_config_names
        config_names.sort()
        with FileWriter(self.config.timing_csv_file_name, header=header) as writer:
            for file, cfg_dict in self.run_result.file_to_sorted_result.items():
                for i in range(0, self.config.repetitions):
                    values = [file]
                    for name in config_names:
                        curr_result = cfg_dict[name][i]
                        values.append(str(curr_result.time_elapsed))
                        values.append(str(curr_result.return_code))
                        values.append(str(curr_result.timeout_occurred))

                    writer.write_line(";".join(values))

        # write per config average timings csv
        if self.csv_timings_cfg_avg_writer:
            for file, cfg_dict in self.run_result.file_to_result_avg.items():
                values = [file]
                for name in config_names:
                    curr_result = cfg_dict[name]
                    values.append(str(curr_result))

                self.csv_timings_cfg_avg_writer.write_line(";".join(values))
            self.csv_timings_cfg_avg_writer.finalize()
