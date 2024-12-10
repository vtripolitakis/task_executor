"""
A script to simulate running commands with different delay scenarios.

It takes a YAML configuration file as an argument. The YAML file must
contain a list of scenarios, each with the following attributes:

  - name: a string to identify the scenario
  - type: one of "no_delay", "random_delay", "fixed_delay_block", or
    "random_delay_block"
  - command: the command to run
  - times: the number of times to run the command
  - max_delay: the maximum delay between commands in a scenario
    (applicable only to "random_delay" and "random_delay_block" scenarios)
  - k: the size of the block of commands in a scenario
    (applicable only to "fixed_delay_block" and "random_delay_block" scenarios)
  - fixed_delay: the fixed delay between blocks of commands in a scenario
    (applicable only to "fixed_delay_block" scenarios)

The script will run each scenario in sequence, reporting the start time
of each scenario.
"""

import yaml
import time
import random
import subprocess
import sys


def run_command(cmd):
    """
    Run a command in the shell.

    Args:
        cmd: the command to run

    Returns:
        None
    """
    subprocess.run(cmd, shell=True, check=True)


def run_no_delay_scenario(command, times):
    """
    Run a command repeatedly with no delay between runs.

    Args:
        command: the command to run
        times: the number of times to run the command

    Returns:
        None
    """
    for _ in range(times):
        run_command(command)


def run_random_delay_scenario(command, times, max_delay):
    """
    Run a command repeatedly with a random delay between runs.

    Args:
        command: the command to run
        times: the number of times to run the command
        max_delay: the maximum delay between runs

    Returns:
        None
    """
    for _ in range(times):
        run_command(command)
        sleep_time = random.uniform(0, max_delay)
        time.sleep(sleep_time)


def run_fixed_delay_block_scenario(command, times, k, fixed_delay):
    """
    Run a command repeatedly with a fixed delay between runs, but
    grouped into blocks of k runs with no delay between runs in the
    same block.

    Args:
        command: the command to run
        times: the number of times to run the command
        k: the size of the block of commands
        fixed_delay: the fixed delay between blocks of commands

    Returns:
        None
    """
    for i in range(times):
        run_command(command)
        if (i + 1) % k == 0 and (i + 1) < times:
            time.sleep(fixed_delay)


def run_random_delay_block_scenario(command, times, k, max_delay):
    """
    Run a command repeatedly with a random delay between runs, but
    grouped into blocks of k runs with no delay between runs in the
    same block.

    Args:
        command: the command to run
        times: the number of times to run the command
        k: the size of the block of commands
        max_delay: the maximum delay between blocks of commands

    Returns:
        None
    """
    for i in range(times):
        run_command(command)
        if (i + 1) % k == 0 and (i + 1) < times:
            sleep_time = random.uniform(0, max_delay)
            time.sleep(sleep_time)


def main(yaml_file):
    """
    Run a scenario from a YAML configuration file.

    Args:
        yaml_file: the YAML file to read the scenario from

    Returns:
        None
    """
    with open(yaml_file, "r") as f:
        config = yaml.safe_load(f)

    for scenario in config.get("scenarios", []):
        scenario_type = scenario["type"]
        command = scenario["command"]
        times = scenario["times"]

        print(f"Running scenario: {
            scenario.get('name', 'unnamed')} [{scenario_type}]")

        if scenario_type == "no_delay":
            run_no_delay_scenario(command, times)
        elif scenario_type == "random_delay":
            run_random_delay_scenario(command, times, scenario["max_delay"])
        elif scenario_type == "fixed_delay_block":
            run_fixed_delay_block_scenario(
                command, times, scenario["k"], scenario["fixed_delay"]
            )
        elif scenario_type == "random_delay_block":
            run_random_delay_block_scenario(
                command, times, scenario["k"], scenario["max_delay"]
            )
        else:
            print(f"Unknown scenario type: {scenario_type}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python simulate.py scenarios.yaml")
        sys.exit(1)
    main(sys.argv[1])
