"""
A script to simulate running commands with different delay scenarios.
Includes detailed reporting and statistics for each scenario and overall execution.
"""

import yaml
import time
import random
import subprocess
import sys
import asyncio
import argparse
from datetime import datetime
from typing import List, Optional, Union, NamedTuple
from dataclasses import dataclass
import signal
from concurrent.futures import ThreadPoolExecutor
import logging
from pathlib import Path
from statistics import mean, median, stdev

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ANSI color codes tuned for terminal
class Colors:
    BLUE = "\033[38;5;75m"
    GREEN = "\033[38;5;77m"
    YELLOW = "\033[38;5;180m"
    RED = "\033[38;5;196m"
    RESET = "\033[0m"
    CYAN = "\033[38;5;87m"
    GRAY = "\033[38;5;240m"
    TIME = "\033[38;5;246m"
    BOLD = "\033[1m"


class ExecutionStats(NamedTuple):
    """Statistics for command execution"""

    total_time: float
    avg_execution_time: float
    median_execution_time: float
    std_dev_execution_time: float
    min_execution_time: float
    max_execution_time: float
    total_delay_time: float
    success_count: int
    failure_count: int


@dataclass
class ScenarioConfig:
    """Data class for scenario configuration"""

    name: str
    type: str
    command: str
    times: int
    max_delay: Optional[float] = None
    k: Optional[int] = None
    fixed_delay: Optional[float] = None
    max_block_size: Optional[int] = None


@dataclass
class ScenarioReport:
    """Report data for a scenario"""

    name: str
    scenario_type: str
    start_time: datetime
    end_time: datetime
    execution_times: List[float]
    delay_times: List[float]
    success_count: int
    failure_count: int

    @property
    def total_time(self) -> float:
        return (self.end_time - self.start_time).total_seconds()

    def generate_stats(self) -> ExecutionStats:
        """Generate execution statistics"""
        if not self.execution_times:
            return ExecutionStats(0, 0, 0, 0, 0, 0, 0, 0, 0)

        return ExecutionStats(
            total_time=self.total_time,
            avg_execution_time=mean(self.execution_times),
            median_execution_time=median(self.execution_times),
            std_dev_execution_time=(
                stdev(self.execution_times) if len(self.execution_times) > 1 else 0
            ),
            min_execution_time=min(self.execution_times),
            max_execution_time=max(self.execution_times),
            total_delay_time=sum(self.delay_times),
            success_count=self.success_count,
            failure_count=self.failure_count,
        )


class ProgressBar:
    """Class to handle progress bar display and updates"""

    def __init__(self, total: int, scenario_name: str, width: int = 40):
        self.total = total
        self.scenario_name = scenario_name
        self.width = width
        self.last_update = 0
        self._start_time = time.time()

    def _get_color(self, progress: float) -> str:
        if progress < 33:
            return Colors.YELLOW
        elif progress < 66:
            return Colors.BLUE
        return Colors.GREEN

    def update(self, current: int, delay: float) -> None:
        """Update progress bar display"""
        current_time = time.time()
        if current_time - self.last_update < 0.1 and current < self.total - 1:
            return

        self.last_update = current_time
        progress = (current + 1) / self.total * 100
        filled_length = int(self.width * (current + 1) // self.total)

        blocks = "█" * filled_length
        empty = "░" * (self.width - filled_length)
        color = self._get_color(progress)

        elapsed = current_time - self._start_time
        rate = (current + 1) / elapsed if elapsed > 0 else 0
        eta = (self.total - (current + 1)) / rate if rate > 0 else 0
        eta_str = f"ETA: {int(eta)}s" if eta > 0 else "Complete"

        progress_line = (
            f"{Colors.CYAN}▸ {self.scenario_name:<30} :: run: {current+1} / {self.total} :: delay {delay:.3f}\" "
            f"{color}|{blocks}{empty}|{Colors.RESET} "
            f"{progress:>5.1f}% {Colors.TIME}@ {datetime.now().strftime('%H:%M:%S')} [{eta_str}]{Colors.RESET}"
        )

        print(f"\r{progress_line}", end="", flush=True)
        if current + 1 == self.total:
            print()


class ScenarioRunner:
    """Class to handle scenario execution"""

    def __init__(self, config: ScenarioConfig):
        self.config = config
        self.progress = ProgressBar(config.times, config.name)
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._stop_event = asyncio.Event()
        self.report = ScenarioReport(
            name=config.name,
            scenario_type=config.type,
            start_time=datetime.now(),
            end_time=datetime.now(),
            execution_times=[],
            delay_times=[],
            success_count=0,
            failure_count=0,
        )

    async def calculate_delay(self, current: int) -> float:
        """Calculate delay based on scenario type"""
        if current >= self.config.times - 1:
            return 0

        if self.config.type == "random_delay":
            return random.uniform(0, self.config.max_delay)
        elif self.config.type == "fixed_delay_block":
            return self.config.fixed_delay if (current + 1) % self.config.k == 0 else 0
        elif self.config.type == "random_delay_block":
            return (
                random.uniform(0, self.config.max_delay)
                if (current + 1) % self.config.k == 0
                else 0
            )
        elif self.config.type == "random_block_size_fixed_delay":
            return (
                self.config.fixed_delay
                if random.randint(1, self.config.max_block_size) == 1
                else 0
            )
        elif self.config.type == "random_block_size_random_delay":
            return (
                random.uniform(0, self.config.max_delay)
                if random.randint(1, self.config.max_block_size) == 1
                else 0
            )
        return 0

    async def run_command(self, cmd: str) -> float:
        """Run a command and return execution time"""
        start_time = time.time()
        try:
            await asyncio.get_event_loop().run_in_executor(
                self._executor,
                lambda: subprocess.run(
                    cmd, shell=True, check=True, capture_output=True
                ),
            )
            self.report.success_count += 1
        except subprocess.CalledProcessError as e:
            self.report.failure_count += 1
            logger.error(f"Command failed: {e.stderr.decode()}")
            raise
        finally:
            execution_time = time.time() - start_time
            self.report.execution_times.append(execution_time)
        return execution_time

    async def run(self) -> ScenarioReport:
        """Run the scenario and return report"""
        self.report.start_time = datetime.now()

        for i in range(self.config.times):
            if self._stop_event.is_set():
                break

            try:
                await self.run_command(self.config.command)
                delay = await self.calculate_delay(i)
                self.progress.update(i, delay)

                if delay > 0:
                    self.report.delay_times.append(delay)
                    await asyncio.sleep(delay)

            except Exception as e:
                logger.error(f"Error in scenario {self.config.name}: {str(e)}")
                break

        self.report.end_time = datetime.now()
        self.print_scenario_report()
        return self.report

    def print_scenario_report(self) -> None:
        """Print detailed report for the scenario"""
        stats = self.report.generate_stats()

        print(
            f"\n{Colors.BOLD}Scenario Report: {Colors.CYAN}{self.report.name}{Colors.RESET}"
        )
        print(f"{Colors.GRAY}{'─' * 75}{Colors.RESET}")
        print(f"Type: {self.report.scenario_type}")
        print(f"Duration: {stats.total_time:.2f}s")
        print("Execution Times:")
        print(f"  ├─ Average: {stats.avg_execution_time:.3f}s")
        print(f"  ├─ Median:  {stats.median_execution_time:.3f}s")
        print(f"  ├─ Std Dev: {stats.std_dev_execution_time:.3f}s")
        print(f"  ├─ Min:     {stats.min_execution_time:.3f}s")
        print(f"  └─ Max:     {stats.max_execution_time:.3f}s")
        print(
            f"Delays: {len(self.report.delay_times)} ({sum(self.report.delay_times):.2f}s total)"
        )
        print(
            f"Success Rate: {self.report.success_count}/{self.report.success_count + self.report.failure_count}"
        )
        print(f"{Colors.GRAY}{'─' * 75}{Colors.RESET}")

    def stop(self) -> None:
        """Stop the scenario execution"""
        self._stop_event.set()
        self._executor.shutdown(wait=False)


class SimulationManager:
    """Class to manage overall simulation execution"""

    def __init__(self, config_file: Union[str, Path]):
        self.config_file = Path(config_file)
        self.runners: List[ScenarioRunner] = []
        self._stop_event = asyncio.Event()
        self.reports: List[ScenarioReport] = []

    def load_config(self) -> List[ScenarioConfig]:
        """Load and validate configuration"""
        with open(self.config_file) as f:
            config = yaml.safe_load(f)

        scenarios = []
        for scenario in config.get("scenarios", []):
            scenarios.append(ScenarioConfig(**scenario))
        return scenarios

    async def run_scenarios(self) -> None:
        """Run all scenarios and collect reports"""
        scenarios = self.load_config()
        total_scenarios = len(scenarios)

        print(f"\n{Colors.CYAN}Starting {total_scenarios} scenarios{Colors.RESET}")
        print(f"{Colors.GRAY}{'─' * 75}{Colors.RESET}")

        start_time = datetime.now()

        for i, scenario_config in enumerate(scenarios, 1):
            if self._stop_event.is_set():
                break

            print(
                f"Scenario {i}/{total_scenarios}: {Colors.CYAN}{scenario_config.name}{Colors.RESET}"
            )
            print(
                f"Command: {Colors.BLUE}{scenario_config.command}{Colors.RESET}"
            )

            runner = ScenarioRunner(scenario_config)
            self.runners.append(runner)

            report = await runner.run()
            self.reports.append(report)

        self.print_final_report(start_time)

    def print_final_report(self, start_time: datetime) -> None:
        """Print final summary report for all scenarios"""
        total_time = (datetime.now() - start_time).total_seconds()
        total_executions = sum(r.success_count + r.failure_count for r in self.reports)
        total_successes = sum(r.success_count for r in self.reports)
        total_failures = sum(r.failure_count for r in self.reports)

        print(f"\n{Colors.BOLD}{Colors.GREEN}Final Simulation Report{Colors.RESET}")
        print(f"{Colors.GRAY}{'═' * 75}{Colors.RESET}")
        print(f"Total Scenarios: {len(self.reports)}")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Total Executions: {total_executions}")
        print(
            f"Total Failures: {total_failures}"
        )
        print(
            f"Overall Success Rate: {total_successes}/{total_executions} ({total_successes/total_executions*100:.1f}%)"
        )

        print(f"\n{Colors.BOLD}Performance Summary:{Colors.RESET}")
        for report in self.reports:
            stats = report.generate_stats()
            print(f"\n{Colors.CYAN}{report.name}{Colors.RESET}")
            print(f"  ├─ Duration: {stats.total_time:.2f}s")
            print(f"  ├─ Avg Execution: {stats.avg_execution_time:.3f}s")
            print(
                f"  ├─ Success Rate: {report.success_count}/{report.success_count + report.failure_count}"
            )
            print(f"  └─ Total Delay Time: {stats.total_delay_time:.2f}s")

        print(f"\n{Colors.GRAY}{'═' * 75}{Colors.RESET}")

    def stop(self) -> None:
        """Stop all running scenarios"""
        self._stop_event.set()
        for runner in self.runners:
            runner.stop()


def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Run command execution scenarios")
    parser.add_argument("config", type=str, help="Path to YAML configuration file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return parser.parse_args()


async def main() -> None:
    """Main entry point"""
    args = parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    manager = SimulationManager(args.config)

    def signal_handler(sig, frame):
        print("\nGracefully shutting down...")
        manager.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await manager.run_scenarios()
    except Exception as e:
        logger.error(f"Simulation failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
