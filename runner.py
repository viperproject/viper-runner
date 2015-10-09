import argparse
from src.environment import Environment

"""
Helper script for the Viper tool chain.
Runs tests, measures time and kills processes that take too long.
"""


def print_header():
    print()
    print("Viper tool chain runner")
    print("-----------------------")
    print()


parser = argparse.ArgumentParser(description='Viper tool chain runner.')
parser.add_argument('config_file', help='the configuration file for this script.')
args = parser.parse_args()
print_header()
env = Environment()
env.exec(args.config_file)
