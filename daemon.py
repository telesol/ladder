#!/usr/bin/env python3
"""
Ladder Agents Daemon - 24/7 autonomous discovery service
Runs continuously, exploring the ladder and making discoveries
"""
import os
import sys
import asyncio
import signal
import json
import logging
from datetime import datetime
from typing import Dict, Optional
import yaml

# Add agents to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents'))

from orchestrator import ClaudeOrchestrator

class LadderDaemon:
    """24/7 daemon for autonomous ladder discovery"""

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.running = False
        self.cycle_count = 0
        self.discoveries_count = 0

        # Setup logging
        self._setup_logging()

        # Initialize orchestrator
        self.orchestrator = ClaudeOrchestrator(config_path)

        # Discovery goals to cycle through
        self.discovery_goals = [
            "Analyze all 16 lanes and find patterns in delta distributions",
            "Search for anomalies in the puzzle data",
            "Generate a hypothesis about cross-lane relationships",
            "Explore mathematical approaches to derive the key generation formula",
            "Verify the affine model and report accuracy",
            "Compute drift from bridge puzzles 75-80 and validate",
            "Analyze which lanes show the most predictable patterns",
            "Look for periodicity or cycles in the lane values",
        ]
        self.current_goal_idx = 0

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration"""
        if not os.path.isabs(config_path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, config_path)
        with open(config_path) as f:
            return yaml.safe_load(f)

    def _setup_logging(self):
        """Setup logging"""
        log_dir = os.path.join(self.base_dir, self.config['paths']['logs'])
        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(log_dir, f"daemon_{datetime.now().strftime('%Y%m%d')}.log")

        logging.basicConfig(
            level=getattr(logging, self.config['daemon']['log_level']),
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("LadderDaemon")

    def log(self, message: str, level: str = "INFO"):
        """Log a message"""
        getattr(self.logger, level.lower())(message)

    async def run_cycle(self) -> Dict:
        """Run one discovery cycle"""
        self.cycle_count += 1

        # Get next goal
        goal = self.discovery_goals[self.current_goal_idx]
        self.current_goal_idx = (self.current_goal_idx + 1) % len(self.discovery_goals)

        self.log(f"Cycle {self.cycle_count}: Starting goal - {goal}")

        try:
            result = await self.orchestrator.execute_goal(goal)

            # Check for discoveries
            if result.get('results'):
                for task_result in result['results']:
                    if 'discovery' in str(task_result.get('result', {})):
                        self.discoveries_count += 1
                        self.log(f"New discovery! Total: {self.discoveries_count}")

            self.log(f"Cycle {self.cycle_count} complete. Tasks: {result.get('tasks', 0)}")
            return result

        except Exception as e:
            self.log(f"Cycle {self.cycle_count} error: {str(e)}", "ERROR")
            return {"error": str(e)}

    async def run(self):
        """Main daemon loop"""
        self.running = True
        interval = self.config['daemon']['run_interval']

        self.log(f"Ladder Daemon starting. Interval: {interval}s")
        self.log(f"Discovery goals: {len(self.discovery_goals)}")

        while self.running:
            try:
                result = await self.run_cycle()

                # Log summary
                synthesis = result.get('synthesis', '')[:200]
                self.log(f"Synthesis: {synthesis}...")

            except Exception as e:
                self.log(f"Unexpected error: {str(e)}", "ERROR")

            # Wait for next cycle
            if self.running:
                self.log(f"Waiting {interval}s until next cycle...")
                await asyncio.sleep(interval)

        self.log("Daemon stopped")

    def stop(self):
        """Stop the daemon"""
        self.log("Stop requested")
        self.running = False

    def get_status(self) -> Dict:
        """Get daemon status"""
        return {
            "running": self.running,
            "cycle_count": self.cycle_count,
            "discoveries_count": self.discoveries_count,
            "current_goal": self.discovery_goals[self.current_goal_idx],
            "next_goal_idx": self.current_goal_idx
        }


def signal_handler(signum, frame, daemon: LadderDaemon):
    """Handle shutdown signals"""
    print(f"\nReceived signal {signum}, shutting down...")
    daemon.stop()


async def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                    LADDER AGENTS DAEMON                            ║
║                 24/7 Autonomous Discovery                          ║
╠═══════════════════════════════════════════════════════════════════╣
║  Claude Orchestrator + Ollama Cloud Agents + Local RAG            ║
║  All data stays local - synced to NAS                              ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    daemon = LadderDaemon()

    # Setup signal handlers
    signal.signal(signal.SIGINT, lambda s, f: signal_handler(s, f, daemon))
    signal.signal(signal.SIGTERM, lambda s, f: signal_handler(s, f, daemon))

    # Run daemon
    await daemon.run()


if __name__ == "__main__":
    asyncio.run(main())
