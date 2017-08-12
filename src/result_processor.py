import os
from src.filewriter import FileWriter

class ResultProcessor:
    """
    Object encapsulation the logic to make sense of the collected results.
    """

    def __init__(self, run_result, config):
        self.run_result = run_result
        self.config = config
        self.results_processed = False

    def write_result_files(self):
        """
        Writes the various result files.
        """
        if not self.results_processed:
            self.run_result.process_timings()

        if self.config.get('results.individual_timings', None):
            self.write_result_csv()

        if self.config.get('results.per_config_timings', None):
            self.writer_per_config_file()

        if self.config.get('results.avg_per_config_timings', None):
            self.write_avg_result_file()

    def write_result_csv(self):
        header = ["runtime [s]", "input file", "run configuration", "exit code", "timeout"]
        data = [header]

        # collect data
        for results_per_file in self.run_result.file_to_result.values():
            for result in results_per_file:
                data.append([str(result.time_elapsed),
                             result.input_file,
                             result.config_name,
                             str(result.return_code),
                             str(result.timeout_occurred)])

        # write data
        filename = os.path.join(self.config.get('results.path'), 
                                self.config.get('results.individual_timings'))
        with FileWriter(filename) as writer:
            writer.write_csv_data(data)

    def writer_per_config_file(self):
        # Assemble file header
        header = [c.get('name') for c in self.config.get('run_configurations')]
        header.sort()
        header = [[name + ", runtime [s]", name + ", exit condition", name + ", timeout"] for name in header]
        # flatten
        header = [string for cfg_header in header for string in cfg_header]
        header.insert(0, "input file")
        data = [header]

        config_names = [c.get('name') for c in self.config.get('run_configurations')]
        config_names.sort()

        for file, cfg_dict in self.run_result.file_to_sorted_result.items():
            for i in range(0, self.config.get('repetitions')):
                values = [file]
                for name in config_names:
                    curr_result = cfg_dict[name][i]
                    values.append(str(curr_result.time_elapsed))
                    values.append(str(curr_result.return_code))
                    values.append(str(curr_result.timeout_occurred))
                data.append(values)

        filename = os.path.join(self.config.get('results.path'), 
                                self.config.get('results.per_config_timings'))
        with FileWriter(filename) as writer:
            writer.write_csv_data(data)

    def write_avg_result_file(self):
        header = [c.get('name') for c in self.config.get('run_configurations')]
        header.sort()
        header = [name + ", average runtime [s]" for name in header]
        header.insert(0, "input file")
        data = [header]

        # write per config average timings csv
        config_names = [c.get('name') for c in self.config.get('run_configurations')]
        config_names.sort()

        for file, cfg_dict in self.run_result.file_to_result_avg.items():
            values = [file]
            for name in config_names:
                curr_result = cfg_dict[name]
                values.append(str(curr_result))
            data.append(values)

        filename = os.path.join(self.config.get('results.path'), 
                                self.config.get('results.avg_per_config_timings'))
        with FileWriter(filename) as writer:
            writer.write_csv_data(data)
