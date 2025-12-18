#!/usr/bin/env python3
"""
NAS Sync - Synchronize LA project data with Boyz-NAS (QNAP)
"""
import os
import subprocess
import time
import logging
from datetime import datetime
from typing import Dict, List
import yaml

class NASSync:
    """Sync manager for Boyz-NAS"""

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.sync_config = self.config.get('sync', {})

        self.nas_host = self.sync_config.get('nas_host', '192.168.111.232')
        self.nas_name = self.sync_config.get('nas_name', 'Boyz-NAS')
        self.nas_share = self.sync_config.get('nas_share', 'LadderAgents')
        self.interval = self.sync_config.get('sync_interval', 300)
        self.sync_paths = self.sync_config.get('sync_paths', ['db/', 'data/', 'logs/'])

        self.mount_point = os.path.join(self.base_dir, 'sync/mnt')
        self.last_sync = None

        self._setup_logging()

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration"""
        if not os.path.isabs(config_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, config_path)
        with open(config_path) as f:
            return yaml.safe_load(f)

    def _setup_logging(self):
        """Setup logging"""
        log_dir = os.path.join(self.base_dir, 'logs')
        os.makedirs(log_dir, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'nas_sync.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("NASSync")

    def check_nas_available(self) -> bool:
        """Check if NAS is reachable"""
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '2', self.nas_host],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"NAS ping failed: {e}")
            return False

    def mount_nas(self, username: str = None, password: str = None) -> bool:
        """Mount NAS share via CIFS (supports guest access)"""
        os.makedirs(self.mount_point, exist_ok=True)

        # Check if already mounted
        result = subprocess.run(['mountpoint', '-q', self.mount_point])
        if result.returncode == 0:
            self.logger.info("NAS already mounted")
            return True

        # Get credentials from environment or config
        username = username or os.getenv('NAS_USER', '')
        password = password or os.getenv('NAS_PASS', '')

        # Build mount options - use guest if no credentials provided
        if not username or username.lower() == 'guest':
            mount_opts = f'guest,uid={os.getuid()},gid={os.getgid()}'
        elif not password:
            # Username but no password - try guest with username hint
            mount_opts = f'guest,uid={os.getuid()},gid={os.getgid()}'
        else:
            mount_opts = f'username={username},password={password},uid={os.getuid()},gid={os.getgid()}'

        mount_cmd = [
            'sudo', 'mount', '-t', 'cifs',
            f'//{self.nas_host}/{self.nas_share}',
            self.mount_point,
            '-o', mount_opts
        ]

        try:
            result = subprocess.run(mount_cmd, capture_output=True, timeout=30)
            if result.returncode == 0:
                self.logger.info(f"Mounted NAS at {self.mount_point}")
                return True
            else:
                self.logger.error(f"Mount failed: {result.stderr.decode()}")
                return False
        except Exception as e:
            self.logger.error(f"Mount error: {e}")
            return False

    def unmount_nas(self) -> bool:
        """Unmount NAS share"""
        try:
            result = subprocess.run(
                ['sudo', 'umount', self.mount_point],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Unmount error: {e}")
            return False

    def sync_to_nas(self) -> Dict:
        """Sync local files to NAS"""
        if not self.check_nas_available():
            return {"success": False, "error": "NAS not available"}

        results = {
            "success": True,
            "synced": [],
            "errors": [],
            "timestamp": datetime.now().isoformat()
        }

        for path in self.sync_paths:
            local_path = os.path.join(self.base_dir, path)
            remote_path = os.path.join(self.mount_point, path)

            if not os.path.exists(local_path):
                continue

            try:
                # Use rsync for efficient sync
                rsync_cmd = [
                    'rsync', '-avz', '--delete',
                    local_path,
                    os.path.dirname(remote_path) + '/'
                ]

                result = subprocess.run(
                    rsync_cmd,
                    capture_output=True,
                    timeout=300
                )

                if result.returncode == 0:
                    results["synced"].append(path)
                    self.logger.info(f"Synced {path}")
                else:
                    results["errors"].append({
                        "path": path,
                        "error": result.stderr.decode()
                    })
                    self.logger.error(f"Sync failed for {path}: {result.stderr.decode()}")

            except Exception as e:
                results["errors"].append({"path": path, "error": str(e)})
                self.logger.error(f"Sync error for {path}: {e}")

        if results["errors"]:
            results["success"] = False

        self.last_sync = datetime.now()
        return results

    def sync_from_nas(self) -> Dict:
        """Sync files from NAS to local"""
        if not self.check_nas_available():
            return {"success": False, "error": "NAS not available"}

        results = {
            "success": True,
            "synced": [],
            "errors": [],
            "timestamp": datetime.now().isoformat()
        }

        for path in self.sync_paths:
            local_path = os.path.join(self.base_dir, path)
            remote_path = os.path.join(self.mount_point, path)

            if not os.path.exists(remote_path):
                continue

            try:
                rsync_cmd = [
                    'rsync', '-avz',
                    remote_path,
                    os.path.dirname(local_path) + '/'
                ]

                result = subprocess.run(
                    rsync_cmd,
                    capture_output=True,
                    timeout=300
                )

                if result.returncode == 0:
                    results["synced"].append(path)
                else:
                    results["errors"].append({
                        "path": path,
                        "error": result.stderr.decode()
                    })

            except Exception as e:
                results["errors"].append({"path": path, "error": str(e)})

        if results["errors"]:
            results["success"] = False

        return results

    def run_sync_daemon(self):
        """Run continuous sync daemon"""
        self.logger.info(f"Starting NAS sync daemon. Interval: {self.interval}s")

        while True:
            if self.check_nas_available():
                # Check if mounted
                result = subprocess.run(['mountpoint', '-q', self.mount_point])
                if result.returncode != 0:
                    self.mount_nas()

                # Sync to NAS
                result = self.sync_to_nas()
                if result["success"]:
                    self.logger.info(f"Sync complete: {len(result['synced'])} paths")
                else:
                    self.logger.warning(f"Sync issues: {result['errors']}")
            else:
                self.logger.warning("NAS not available, skipping sync")

            time.sleep(self.interval)

    def get_status(self) -> Dict:
        """Get sync status"""
        nas_available = self.check_nas_available()

        # Check mount
        result = subprocess.run(['mountpoint', '-q', self.mount_point])
        mounted = result.returncode == 0

        return {
            "nas_host": self.nas_host,
            "nas_name": self.nas_name,
            "nas_available": nas_available,
            "mounted": mounted,
            "mount_point": self.mount_point,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "sync_paths": self.sync_paths
        }


# CLI interface
if __name__ == "__main__":
    import sys

    sync = NASSync()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python nas_sync.py status    - Check NAS status")
        print("  python nas_sync.py mount     - Mount NAS share")
        print("  python nas_sync.py unmount   - Unmount NAS share")
        print("  python nas_sync.py sync      - Sync to NAS (one-time)")
        print("  python nas_sync.py pull      - Pull from NAS")
        print("  python nas_sync.py daemon    - Run continuous sync")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "status":
        status = sync.get_status()
        print(f"NAS: {status['nas_name']} ({status['nas_host']})")
        print(f"Available: {status['nas_available']}")
        print(f"Mounted: {status['mounted']}")
        print(f"Last sync: {status['last_sync']}")

    elif cmd == "mount":
        if sync.mount_nas():
            print("NAS mounted successfully")
        else:
            print("Failed to mount NAS")

    elif cmd == "unmount":
        if sync.unmount_nas():
            print("NAS unmounted")
        else:
            print("Failed to unmount")

    elif cmd == "sync":
        result = sync.sync_to_nas()
        print(f"Sync result: {result}")

    elif cmd == "pull":
        result = sync.sync_from_nas()
        print(f"Pull result: {result}")

    elif cmd == "daemon":
        sync.run_sync_daemon()
