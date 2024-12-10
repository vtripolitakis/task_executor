"""
A script to simulate running commands with different delay scenarios.
Includes progress tracking for each scenario.

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
and progress of each scenario.
"""


import yaml
import time
import random
import subprocess
import sys
from datetime import datetime

# ANSI color codes tuned for terminal
class Colors:
    BLUE = '\033[38;5;75m'      # Bright blue
    GREEN = '\033[38;5;77m'     # Bright green
    YELLOW = '\033[38;5;180m'   # Muted yellow/brown
    RESET = '\033[0m'
    CYAN = '\033[38;5;87m'      # Bright cyan
    GRAY = '\033[38;5;240m'     # Dark gray for dividers
    PURPLE = '\033[38;5;98m'    # Purple for some text
    TIME = '\033[38;5;246m'     # Gray for timestamp

def format_timestamp():
    """Format current timestamp in a clean way"""
    now = datetime.now()
    return now.strftime("%H:%M:%S")

def print_divider():
    """Print a divider line"""
    print(f"{Colors.GRAY}{'─' * 75}{Colors.RESET}")

def get_progress_color(progress):
    """Get the appropriate color for the progress bar based on percentage"""
    if progress < 33:
        return Colors.YELLOW
    elif progress < 66:
        return Colors.BLUE
    return Colors.GREEN

def print_progress(current, total, scenario_name):
    """
    Print an enhanced progress bar showing scenario completion status.
    """
    progress = (current + 1) / total * 100
    bar_length = 40
    filled_length = int(bar_length * (current + 1) // total)
    
    # Using simple blocks for the progress bar
    blocks = "█" * filled_length
    empty = "░" * (bar_length - filled_length)
    
    # Color the progress bar
    color = get_progress_color(progress)
    
    # Format the scenario name
    formatted_name = f"{scenario_name[:30]:<30}"
    
    # Construct the progress line
    progress_line = (
        f"{Colors.CYAN}▸ {formatted_name}"
        f"{color}|{blocks}{empty}|{Colors.RESET} "
        f"{progress:>5.1f}% {Colors.TIME}@ {format_timestamp()}{Colors.RESET}"
    )
    
    print(progress_line)

def run_command(cmd):
    """Run a command in the shell."""
    subprocess.run(cmd, shell=True, check=True)

def run_no_delay_scenario(command, times, scenario_name):
    """
    Run a command repeatedly with no delay between runs.

    Args:
        command: the command to run
        times: the number of times to run the command
        scenario_name: name of the scenario for progress tracking

    Returns:
        None
    """
    for i in range(times):
        run_command(command)
        print_progress(i, times, scenario_name)


def run_random_delay_scenario(command, times, max_delay, scenario_name):
    """
    Run a command repeatedly with a random delay between runs.

    Args:
        command: the command to run
        times: the number of times to run the command
        max_delay: the maximum delay between runs
        scenario_name: name of the scenario for progress tracking

    Returns:
        None
    """
    for i in range(times):
        run_command(command)
        print_progress(i, times, scenario_name)
        if i < times - 1:  # Don't sleep after the last command
            sleep_time = random.uniform(0, max_delay)
            time.sleep(sleep_time)


def run_fixed_delay_block_scenario(command, times, k, fixed_delay, scenario_name):
    """
    Run a command repeatedly with a fixed delay between runs, but
    grouped into blocks of k runs with no delay between runs in the
    same block.

    Args:
        command: the command to run
        times: the number of times to run the command
        k: the size of the block of commands
        fixed_delay: the fixed delay between blocks of commands
        scenario_name: name of the scenario for progress tracking

    Returns:
        None
    """
    for i in range(times):
        run_command(command)
        print_progress(i, times, scenario_name)
        if (i + 1) % k == 0 and (i + 1) < times:
            time.sleep(fixed_delay)


def run_random_delay_block_scenario(command, times, k, max_delay, scenario_name):
    """
    Run a command repeatedly with a random delay between runs, but
    grouped into blocks of k runs with no delay between runs in the
    same block.

    Args:
        command: the command to run
        times: the number of times to run the command
        k: the size of the block of commands
        max_delay: the maximum delay between blocks of commands
        scenario_name: name of the scenario for progress tracking

    Returns:
        None
    """
    for i in range(times):
        run_command(command)
        print_progress(i, times, scenario_name)
        if (i + 1) % k == 0 and (i + 1) < times:
            sleep_time = random.uniform(0, max_delay)
            time.sleep(sleep_time)


def run_random_block_size_fixed_delay_scenario(
        command, times, max_block_size, fixed_delay, scenario_name):
    """
    Run a command repeatedly with a fixed delay between runs, but
    grouped into blocks of random size.

    Args:
        command: the command to run
        times: the number of times to run the command
        max_block_size: the maximum size of the block of commands
        fixed_delay: the fixed delay between blocks of commands
        scenario_name: name of the scenario for progress tracking

    Returns:
        None
    """
    block_size = 0
    for i in range(times):
        run_command(command)
        print_progress(i, times, scenario_name)
        block_size += 1
        if block_size >= random.randint(1, max_block_size) and (i + 1) < times:
            time.sleep(fixed_delay)
            block_size = 0


def run_random_block_size_random_delay_scenario(
        command, times, max_block_size, max_delay, scenario_name):
    """
    Run a command repeatedly with a random delay between runs, but
    grouped into blocks of random size.

    Args:
        command: the command to run
        times: the number of times to run the command
        max_block_size: the maximum size of the block of commands
        max_delay: the maximum delay between blocks of commands
        scenario_name: name of the scenario for progress tracking

    Returns:
        None
    """
    block_size = 0
    for i in range(times):
        run_command(command)
        print_progress(i, times, scenario_name)
        block_size += 1
        if block_size >= random.randint(1, max_block_size) and (i + 1) < times:
            sleep_time = random.uniform(0, max_delay)
            time.sleep(sleep_time)
            block_size = 0


def main(yaml_file):
    """
    Run scenarios from a YAML configuration file.
    """
    with open(yaml_file, "r") as f:
        config = yaml.safe_load(f)

    total_scenarios = len(config.get("scenarios", []))
    
    print(f"\n{Colors.CYAN}Starting {total_scenarios} scenarios{Colors.RESET}")
    print_divider()

    for i, scenario in enumerate(config.get("scenarios", []), 1):
        scenario_type = scenario["type"]
        command = scenario["command"]
        times = scenario["times"]
        scenario_name = scenario.get('name', 'unnamed')

        print(f"Scenario {i}/{total_scenarios}: {Colors.CYAN}{scenario_name}{Colors.RESET}")
        
        # Run the appropriate scenario
        for current in range(times):
            run_command(command)
            print_progress(current, times, scenario_name)
            
            # Add appropriate delays based on scenario type
            if current < times - 1:  # Don't delay after the last iteration
                if scenario_type == "random_delay":
                    time.sleep(random.uniform(0, scenario["max_delay"]))
                elif scenario_type == "fixed_delay_block" and (current + 1) % scenario["k"] == 0:
                    time.sleep(scenario["fixed_delay"])
                elif scenario_type == "random_delay_block" and (current + 1) % scenario["k"] == 0:
                    time.sleep(random.uniform(0, scenario["max_delay"]))
                elif scenario_type == "random_block_size_fixed_delay":
                    if random.randint(1, scenario["max_block_size"]) == 1:
                        time.sleep(scenario["fixed_delay"])
                elif scenario_type == "random_block_size_random_delay":
                    if random.randint(1, scenario["max_block_size"]) == 1:
                        time.sleep(random.uniform(0, scenario["max_delay"]))

        print_divider()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"{Colors.RED}Usage: python simulate.py scenarios.yaml{Colors.RESET}")
        sys.exit(1)
    main(sys.argv[1])