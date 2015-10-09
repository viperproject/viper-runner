import datetime
import os

__author__ = 'froth'

PLACEHOLDER_DATE = "@date@"
PLACEHOLDER_FILENAME = "@file_name@"
PLACEHOLDER_PATH_DEPENDENT_FILENAME = "@path_name@"
PLACEHOLDER_REP = "@rep@"
PLACEHOLDER_CONFIG_NAME = "@config_name@"
CURR_DATE = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


def replace_placeholders(string, file="", repetition=PLACEHOLDER_REP, date=CURR_DATE,
                         config_name=PLACEHOLDER_CONFIG_NAME):
    filename = PLACEHOLDER_FILENAME
    path_filename = PLACEHOLDER_PATH_DEPENDENT_FILENAME
    if file != "":
        filename = os.path.basename(file)
        path_filename = generate_path_dependent_filename(file)
    return string.replace(PLACEHOLDER_DATE, date) \
        .replace(PLACEHOLDER_FILENAME, filename) \
        .replace(PLACEHOLDER_REP, str(repetition)) \
        .replace(PLACEHOLDER_PATH_DEPENDENT_FILENAME, path_filename) \
        .replace(PLACEHOLDER_CONFIG_NAME, config_name)


def generate_path_dependent_filename(file):
    folders = []
    while True:
        path, folder = os.path.split(file)

        if path:
            folders.append(folder)
        else:
            break
        file = path
    folders.reverse()
    return "_".join(folders)
