import yaml
import time
import random
import subprocess
import sys


def run_command(cmd):
    # Simple wrapper to run the command. Adjust as needed.
    # If the command is a single string, you might want to split it by spaces:
    # subprocess.run(cmd.split(), check=True)
    subprocess.run(cmd, shell=True, check=True)


def main(yaml_file):
    with open(yaml_file, "r") as f:
        config = yaml.safe_load(f)

    for scenario in config.get("scenarios", []):
        scenario_type = scenario["type"]
        command = scenario["command"]
        times = scenario["times"]

        print(f"Running scenario: {scenario.get('name', 'unnamed')} [{scenario_type}]")

        if scenario_type == "no_delay":
            for _ in range(times):
                run_command(command)

        elif scenario_type == "random_delay":
            max_delay = scenario["max_delay"]
            for _ in range(times):
                run_command(command)
                # random delay between 0 and max_delay
                sleep_time = random.uniform(0, max_delay)
                time.sleep(sleep_time)

        elif scenario_type == "fixed_delay_block":
            k = scenario["k"]
            fixed_delay = scenario["fixed_delay"]
            for i in range(times):
                run_command(command)
                # after each block of k executions, sleep (if not the last iteration)
                if (i + 1) % k == 0 and (i + 1) < times:
                    time.sleep(fixed_delay)

        elif scenario_type == "random_delay_block":
            k = scenario["k"]
            max_delay = scenario["max_delay"]
            for i in range(times):
                run_command(command)
                # after each block of k executions, sleep (if not the last iteration)
                if (i + 1) % k == 0 and (i + 1) < times:
                    sleep_time = random.uniform(0, max_delay)
                    time.sleep(sleep_time)
        else:
            print(f"Unknown scenario type: {scenario_type}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python simulate.py scenarios.yaml")
        sys.exit(1)
    main(sys.argv[1])
