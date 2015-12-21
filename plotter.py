import csv
import datetime
import argparse
import numpy
import matplotlib.pyplot as plt
import os.path

parser = argparse.ArgumentParser(description='Viper runner result plotter.')
parser.add_argument('-max', dest='max', type=int, help='cutoff value for plotting.')
parser.add_argument('csv', help='the csv file containing the data.')
args = parser.parse_args()

data = {}
mean_std_dev_dict = {}
max_value = int(args.max or -1)

# Read data
with open(args.csv, newline='') as csv_file:
    dataReader = csv.reader(csv_file, delimiter=";")
    readerIter = dataReader.__iter__()
    next(readerIter)  # skip first line
    for line in readerIter:
        file_name = line[1]
        if file_name not in data:
            data[file_name] = {}
            mean_std_dev_dict[file_name] = {}

        file_dict = data[file_name]

        config_name = line[2]
        if config_name not in file_dict:
            file_dict[config_name] = []

        time = float(line[0])
        file_dict[config_name].append(time)

# Process data
for file, file_data in data.items():
    for config, timings in file_data.items():
        if not timings:
            mean_std_dev_dict[file][config] = (-1, 0)
        else:
            arr = numpy.array(timings)
            mean_std_dev_dict[file][config] = (numpy.mean(arr), numpy.std(arr))

# Plot data
configs = list(list(data.values())[0].keys())
configs.sort()

for i in range(0, len(configs)):
    config1 = configs[i]

    for j in range(i+1, len(configs)):
        config2 = configs[j]
        plt.figure()

        curr_min = None
        curr_max = 0

        config1_faster = 0
        config2_faster = 0

        diffs = []

        for file, config_dict in data.items():
            (x, x_dev) = mean_std_dev_dict[file][config1]
            (y, y_dev) = mean_std_dev_dict[file][config2]

            fmt = 'bo'
            if x == -1 or 0 < max_value < x:
                x = max_value
                x_dev = None
                fmt = 'rs'
            if y == -1 or 0 < max_value < y:
                y = max_value
                y_dev = None
                fmt = 'rs'

            if x < y:
                config1_faster += 1
            if y < x:
                config2_faster += 1
            if x != max_value and y != max_value:
                diffs.append(x-y)
            plt.errorbar(x, y, xerr=x_dev, yerr=y_dev, fmt=fmt)

            tmp_max = max(x, y)
            if tmp_max > curr_max:
                curr_max = tmp_max
            tmp_min = min(x, y)
            if not curr_min or tmp_min < curr_min:
                curr_min = tmp_min

        plt.rc('text', usetex=True)
        plt.rc('font', family='serif', size=16)
        plt.plot([curr_min, curr_max + 0.1], [curr_min, curr_max + 0.1], 'r-')
        plt.title("Runtime comparison: " + config1 + " vs " + config2)
        plt.xlabel(config1 + ", runtime in [s]")
        plt.ylabel(config2 + ", runtime in [s]")
        plt.grid(True)
        print(str(len(data)) + " points")
        print("config " + config1 + " was faster " + str(config1_faster) + " times.")
        print("config " + config2 + " was faster " + str(config2_faster) + " times.")
        print(str(len(data) - config1_faster - config2_faster) + " times both were exactly equally fast (or timeout).")

        # differences statistics
        diffs_arr = arr = numpy.array(diffs)
        mean_diff = numpy.mean(diffs)
        variance_diffs = numpy.var(diffs)
        std_diffs = numpy.std(diffs)

        print("Mean difference (" + config1 + " - " + config2 + ") was " +
              str(mean_diff) + ", standard deviation was " + str(std_diffs) +
              ", variance was " + str(variance_diffs) + " .")

        time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        fig_name = os.path.join(os.path.dirname(os.path.realpath(args.csv)),
                                time + "_" + config1 + "_vs_" + config2 + "_scatter.pdf") + ""
        plt.savefig(fig_name, dpi=600, format="pdf")

        plt.show()


