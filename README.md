Viper Runner
========================

Benchmark tool for the Viper tool chain.
Runs tests, measures runtimes and kills processes that take too long (including
their children).

Usage: `python runner.py some.conf`

See `./example_configs/` for example configuration files.

Dependencies:
--------------------------
- Python 3.5 or newer
- pyhocon — `pip install pyhocon`
- psutil — included in recent Python installations; otherwise `pip install psutil`
