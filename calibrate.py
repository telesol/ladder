#!/usr/bin/env python3
"""
Unified Calibration Tool

This tool provides a unified interface for the calibration workflow with subcommands
for different calibration operations.
"""

import argparse
import sys
import os
import logging
from typing import Optional, Dict, Any
import yaml
import json

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CalibrationConfig:
    """Configuration manager for calibration parameters"""

    DEFAULT_CONFIG = {
        'database': {
            'path': 'db/kh.db'
        },
        'calibration': {
            'range': [29, 70],
            'lanes': [1, 5, 9, 13],
            'output_dir': 'out',
            'calib_file': 'ladder_calib_29_70_full.json',
            'temp_file': 'missing_c0.json'
        },
        'logging': {
            'level': 'INFO',
            'format': '%(asctime)s - %(levelname)s - %(message)s'
        }
    }

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.config_path = config_path

        if config_path and os.path.exists(config_path):
            self.load_config(config_path)

    def load_config(self, config_path: str) -> None:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f) or {}
                self._deep_update(self.config, user_config)
            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            raise

    def _deep_update(self, original: Dict, update: Dict) -> Dict:
        """Recursively update dictionary"""
        for key, value in update.items():
            if isinstance(value, dict) and key in original:
                original[key] = self._deep_update(original.get(key, {}), value)
            else:
                original[key] = value
        return original

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def save_config(self, config_path: str) -> None:
        """Save current configuration to file"""
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                yaml.dump(self.config, f)
            logger.info(f"Configuration saved to {config_path}")
        except Exception as e:
            logger.error(f"Error saving config file: {e}")
            raise

def setup_logging(config: CalibrationConfig) -> None:
    """Configure logging based on configuration"""
    log_level = config.get('logging.level', 'INFO').upper()
    log_format = config.get('logging.format', '%(asctime)s - %(levelname)s - %(message)s')

    numeric_level = getattr(logging, log_level, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')

    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def init_calibration(config: CalibrationConfig) -> None:
    """Initialize calibration by creating necessary directories and files"""
    logger.info("Initializing calibration...")

    # Create output directory if it doesn't exist
    output_dir = config.get('calibration.output_dir', 'out')
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Created output directory: {output_dir}")

    # Create default calibration file if it doesn't exist
    calib_file = os.path.join(output_dir, config.get('calibration.calib_file'))
    if not os.path.exists(calib_file):
        default_calib = {
            "range": config.get('calibration.range', [29, 70]),
            "lanes": list(range(16)),
            "A": {str(i): 1 for i in range(16)},
            "Cstar": {
                "0": {str(i): [0, 0] for i in range(16)},
                "1": {str(i): [0, 0] for i in range(16)}
            }
        }

        with open(calib_file, 'w') as f:
            json.dump(default_calib, f, indent=2)
        logger.info(f"Created default calibration file: {calib_file}")
    else:
        logger.info(f"Calibration file already exists: {calib_file}")

    logger.info("Calibration initialization complete")

def compute_drift(config: CalibrationConfig) -> None:
    """Compute missing drift constants with enhanced error detection"""
    logger.info("Computing missing drift constants...")

    try:
        # Set environment variables for bridge data
        os.environ['HEX75'] = os.environ.get('HEX75', '')
        os.environ['HEX80'] = os.environ.get('HEX80', '')

        # Import the enhanced drift computation
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from kh_assist.compute_missing_drift_enhanced import compute_drift_with_diagnostics

        # Convert CalibrationConfig to dict for compatibility
        config_dict = config.config
        compute_drift_with_diagnostics(config_dict)
    except ImportError as e:
        logger.warning(f"Enhanced drift computation not available: {e}, using basic implementation")
        basic_compute_drift(config)
    except Exception as e:
        logger.error(f"Error in enhanced drift computation: {e}")
        basic_compute_drift(config)

def basic_compute_drift(config: CalibrationConfig) -> None:
    """Basic drift computation as fallback"""
    logger.warning("Using basic drift computation (no diagnostics)")
    logger.info("To compute drift, run: python kh-assist/compute_missing_drift.py")

def patch_calibration(config: CalibrationConfig) -> None:
    """Patch calibration file with computed drift values"""
    logger.info("Patching calibration file...")

    # Get file paths from config
    output_dir = config.get('calibration.output_dir', 'out')
    calib_path = os.path.join(output_dir, config.get('calibration.calib_file'))
    drift_path = config.get('calibration.temp_file', 'missing_c0.json')

    # Check if files exist
    if not os.path.exists(calib_path):
        logger.error(f"Calibration file not found: {calib_path}")
        return

    if not os.path.exists(drift_path):
        logger.error(f"Drift file not found: {drift_path}")
        logger.info("Run 'calibrate.py compute' first")
        return

    try:
        # Load existing calibration
        with open(calib_path) as f:
            calib = json.load(f)

        logger.info(f"Loaded calibration from {calib_path}")

        # Load computed drift
        with open(drift_path) as f:
            drift_data = json.load(f)

        if 'C0_0' not in drift_data:
            logger.error("Drift file does not contain 'C0_0' key")
            return

        drift = drift_data['C0_0']

        # Convert hex strings to integers if needed
        drift_values = []
        for v in drift:
            if isinstance(v, str):
                # Remove 0x prefix and convert
                drift_values.append(int(v.replace('0x', ''), 16))
            else:
                drift_values.append(int(v))

        if len(drift_values) != 16:
            logger.error(f"Expected 16 drift values, got {len(drift_values)}")
            return

        logger.info(f"Loaded drift C[0][ℓ][0] from {drift_path}")
        logger.debug(f"Values: {drift_values}")

        # Patch the calibration
        # Ensure Cstar structure exists
        if 'Cstar' not in calib:
            calib['Cstar'] = {}

        if '0' not in calib['Cstar']:
            calib['Cstar']['0'] = {}

        if '1' not in calib['Cstar']:
            calib['Cstar']['1'] = {}

        # Patch C[0][lane][0] for each lane
        for lane in range(16):
            lane_str = str(lane)

            # Initialize lane if not present
            if lane_str not in calib['Cstar']['0']:
                calib['Cstar']['0'][lane_str] = [0, 0]

            # Ensure it's a 2-element list
            if not isinstance(calib['Cstar']['0'][lane_str], list):
                calib['Cstar']['0'][lane_str] = [0, 0]

            if len(calib['Cstar']['0'][lane_str]) < 2:
                calib['Cstar']['0'][lane_str] = [0, 0]

            # Patch occurrence 0 with computed drift
            old_value = calib['Cstar']['0'][lane_str][0]
            calib['Cstar']['0'][lane_str][0] = drift_values[lane]

            logger.info(f"  Lane {lane:2d}: C[0][{lane:2d}][0] = {drift_values[lane]:3d} (0x{drift_values[lane]:02x}) [was: {old_value}]")

        # Write back to file (create backup first)
        backup_path = calib_path + '.backup'
        if not os.path.exists(backup_path):
            with open(backup_path, 'w') as f:
                json.dump(calib, f, indent=2)
            logger.info(f"Backup created at {backup_path}")

        with open(calib_path, 'w') as f:
            json.dump(calib, f, indent=2)

        logger.info(f"Calibration file patched successfully!")

    except Exception as e:
        logger.error(f"Error patching calibration: {e}")

def verify_calibration(config: CalibrationConfig) -> None:
    """Verify calibration accuracy"""
    logger.info("Verifying calibration...")

    # This would call the existing verify_affine.py functionality
    # For now, we'll just log the action
    logger.warning("Calibration verification not yet implemented in unified tool")
    logger.info("To verify calibration, run: python kh-assist/verify_affine.py")

def full_calibration(config: CalibrationConfig) -> None:
    """Run complete calibration workflow"""
    logger.info("Starting full calibration workflow...")

    # Initialize calibration
    init_calibration(config)

    # Compute drift
    compute_drift(config)

    # Patch calibration
    patch_calibration(config)

    # Verify calibration
    verify_calibration(config)

    logger.info("Full calibration workflow complete")

def show_status(config: CalibrationConfig) -> None:
    """Show calibration status"""
    logger.info("Calibration Status:")

    # Check if calibration file exists
    output_dir = config.get('calibration.output_dir', 'out')
    calib_file = os.path.join(output_dir, config.get('calibration.calib_file'))

    if os.path.exists(calib_file):
        logger.info(f"✓ Calibration file: {calib_file}")
        try:
            with open(calib_file, 'r') as f:
                calib_data = json.load(f)
                range_start, range_end = calib_data.get('range', ['unknown', 'unknown'])
                logger.info(f"  Calibration range: {range_start}-{range_end}")
                logger.info(f"  Lanes: {len(calib_data.get('lanes', []))} lanes configured")
        except Exception as e:
            logger.error(f"  Error reading calibration file: {e}")
    else:
        logger.warning(f"✗ Calibration file not found: {calib_file}")

    # Check if drift file exists
    drift_file = config.get('calibration.temp_file', 'missing_c0.json')
    if os.path.exists(drift_file):
        logger.info(f"✓ Drift file: {drift_file}")
    else:
        logger.warning(f"✗ Drift file not found: {drift_file}")

def main():
    """Main entry point for calibration tool"""
    parser = argparse.ArgumentParser(
        description='Unified Calibration Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  calibrate.py init --config config/calibration.yaml
  calibrate.py compute --verbose
  calibrate.py patch
  calibrate.py verify
  calibrate.py full
  calibrate.py status
        """
    )

    # Global arguments
    parser.add_argument(
        '--config',
        type=str,
        default='config/calibration.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help='Increase verbosity level (use -v, -vv, -vvv)'
    )

    # Add verbose flag to each subcommand
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for subparser in action._choices_actions:
                subparser.add_argument(
                    '-v', '--verbose',
                    action='count',
                    default=0,
                    help=argparse.SUPPRESS  # Hide from help to avoid duplication
                )

    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize calibration')
    init_parser.set_defaults(func=init_calibration)

    # Compute command
    compute_parser = subparsers.add_parser('compute', help='Compute missing drifts')
    compute_parser.set_defaults(func=compute_drift)

    # Patch command
    patch_parser = subparsers.add_parser('patch', help='Patch calibration files')
    patch_parser.set_defaults(func=patch_calibration)

    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify calibration')
    verify_parser.set_defaults(func=verify_calibration)

    # Full command
    full_parser = subparsers.add_parser('full', help='Complete calibration workflow')
    full_parser.set_defaults(func=full_calibration)

    # Status command
    status_parser = subparsers.add_parser('status', help='Show calibration status')
    status_parser.set_defaults(func=show_status)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Set up configuration
    try:
        config = CalibrationConfig(args.config)
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    # Set up logging based on verbosity
    if args.verbose == 1:
        config.config['logging']['level'] = 'DEBUG'
    elif args.verbose >= 2:
        config.config['logging']['level'] = 'DEBUG'
        # Add file logging for higher verbosity
        log_file = os.path.join(config.get('calibration.output_dir', 'out'), 'calibration.log')
        logging.getLogger().addHandler(logging.FileHandler(log_file))

    setup_logging(config)

    # Execute the requested command
    try:
        args.func(config)
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
