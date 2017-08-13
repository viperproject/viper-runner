import os
import shutil
from pyhocon import ConfigFactory, HOCONConverter, UndefinedKey
from src.util import replace_placeholders, abort, require

class Config():
    """
    Benchmark configuration object.
    """
    data = None

    def __init__(self):
        """
        Initializes default config.
        :return: None
        """

    def print(self):
        print()
        print("Configuration:")
        print(HOCONConverter.convert(self.data, 'hocon'))
        print()

    def read_config_file(self, config_file):
        """
        Parses the configuration file.
        :return: None
        """

        print("Parsing configuration file...")
        self.data = ConfigFactory.parse_file(config_file)

        self._set_default_values()
        self._replace_placeholders()
        self._check_consistency()

        print("Copying config to output folder...")

        # generate output folder if it does not yet exist
        output_dir = self.get_string('results.path') #os.path.dirname(self.timing_csv_file_name)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # create file in case it does not yet exist.
        config_copy_filename = os.path.join(output_dir, os.path.basename(config_file))
        open(config_copy_filename, 'a').close()

        # copy content
        shutil.copyfile(config_file, config_copy_filename)
        print("Done.")

    def _set_default_values(self):
        self._set_default_value('check_files_accessible', True)
        self._set_default_value('confirm_start', True)
        self._set_default_value('print_output', False)
        self._set_default_value('list_files', False)

    def _set_default_value(self, key, default):
        val = self.data.get(key, default)
        self.data.put(key, val)

    def _check_consistency(self):
        # TODO: Complete checks, e.g. check existence of all mandatory properties
        require(self.data, "Parsing configuration file failed")

        require(self.get_int('repetitions', None), "Mandatory property 'repetitions' not found")
        require(self.get_int('timeout', None), "Mandatory property 'timeout' not found")
        require(self.get_config('results', None), "Mandatory property 'results' not found")
        require(self.get_string('results.path', None), "Mandatory property 'results.path' not found")

        output_file_set = self.get_string('stdout_file', "") or self.get_string('stderr_file', "")
        require(self.get_bool('print_output') or not output_file_set, "Properties 'stdout_file' and 'stderr_file' may only be set if 'print_output' is true")

        test_options = 0
        test_options += int(bool(self.get_string('test_folder', "")))
        test_options += int(bool(self.get_string('test_files_in_file', "")))
        require(test_options == 1, "Exactly one of 'test_folder' and 'test_files_in_file' must be set")
        require(not self.get('ignore_files', []) or self.get_string('test_folder', ""), "'ignore_files' can only be set if 'test_folder' is true")

    def _replace_placeholders(self):
        self._transform_string('results.path', replace_placeholders)
        self._transform_string('results.individual_timings', replace_placeholders)
        self._transform_string('results.per_config_timings', replace_placeholders)
        self._transform_string('results.avg_per_config_timings', replace_placeholders)
        self._transform_string('stdout_file', replace_placeholders)
        self._transform_string('stderr_file', replace_placeholders)

    def _transform_string(self, key, func):
        pre_value = self.data.get(key, None)
        if not pre_value == None:
            post_value = func(pre_value)
            self.data.put(key, post_value)

    #
    # The next getters are mere proxies accessing the actual configuration data
    #

    def get(self, key, default=UndefinedKey):
        return self.data.get(key, default)

    def get_string(self, key, default=UndefinedKey):
        return self.data.get_string(key, default)

    def get_int(self, key, default=UndefinedKey):
        return self.data.get_int(key, default)

    def get_float(self, key, default=UndefinedKey):
        return self.data.get_float(key, default)

    def get_bool(self, key, default=UndefinedKey):
        return self.data.get_bool(key, default)

    def get_list(self, key, default=UndefinedKey):
        return self.data.get_list(key, default)

    def get_config(self, key, default=UndefinedKey):
        return self.data.get_config(key, default)