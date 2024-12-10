# Scenario Simulator

This Python script simulates different scenarios for running commands with various delay patterns. It reads scenario configurations from a YAML file and executes them accordingly.

## Usage

To run the simulator, use the following command:

```
python simulate.py scenarios.yaml
```

Where `scenarios.yaml` is the path to your YAML configuration file containing the scenarios you want to run.

## Requirements

- Python 3.x
- PyYAML library

## Installation

`pip install -r requirements.txt`

## Scenario Types

The simulator supports four different scenario types:

1. **No Delay**
   - Type: `no_delay`
   - Description: Runs the specified command multiple times without any delay between executions.
   - Parameters:
     - `command`: The command to run
     - `times`: Number of times to run the command

2. **Random Delay**
   - Type: `random_delay`
   - Description: Runs the command multiple times with a random delay between each execution.
   - Parameters:
     - `command`: The command to run
     - `times`: Number of times to run the command
     - `max_delay`: Maximum delay in seconds (delay will be random between 0 and this value)

3. **Fixed Delay Block**
   - Type: `fixed_delay_block`
   - Description: Runs the command in blocks, with a fixed delay after each block.
   - Parameters:
     - `command`: The command to run
     - `times`: Total number of times to run the command
     - `k`: Number of executions in each block
     - `fixed_delay`: Fixed delay in seconds after each block

4. **Random Delay Block**
   - Type: `random_delay_block`
   - Description: Runs the command in blocks, with a random delay after each block.
   - Parameters:
     - `command`: The command to run
     - `times`: Total number of times to run the command
     - `k`: Number of executions in each block
     - `max_delay`: Maximum delay in seconds after each block (delay will be random between 0 and this value)

## Example YAML Configuration

```yaml
scenarios:
  - name: "no_delay_scenario"
    type: "no_delay"
    command: "./print_timestamp.sh"
    times: 3

  - name: "random_delay_scenario"
    type: "random_delay"
    command: "./print_timestamp.sh"
    times: 5
    max_delay: 5

  - name: "fixed_delay_block_scenario"
    type: "fixed_delay_block"
    command: "./print_timestamp.sh"
    times: 4
    k: 3
    fixed_delay: 3

  - name: "random_delay_block_scenario"
    type: "random_delay_block"
    command: "./print_timestamp.sh"
    times: 4
    k: 3
    max_delay: 3