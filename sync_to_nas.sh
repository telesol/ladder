#!/bin/bash
# Automatic sync script for ZBook Ladder to NAS backup
# Monitors key files and syncs changes to the NAS backup location

# Configuration
SOURCE_DIR="/home/solo/LadderV3/kh-assist"
BACKUP_DIR="/mnt/c/temp/ZBook-Ladder-Backup-20251127_121742"
NAS_PATH="\\\\Boyz-NAS\\Public\\home\\projects\\ZBook-Ladder"

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== ZBook Ladder Auto-Sync ===${NC}"
echo "Source: $SOURCE_DIR"
echo "Backup: $BACKUP_DIR"
echo "NAS Target: $NAS_PATH"
echo ""

# Function to sync a file
sync_file() {
    local file="$1"
    local dest="$2"

    if [ -f "$file" ]; then
        cp -v "$file" "$dest/" 2>&1 | sed "s/^/  /"
        return 0
    fi
    return 1
}

# Function to perform full sync
full_sync() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')]${NC} Syncing files..."

    # Database
    sync_file "db/kh.db" "$BACKUP_DIR"

    # Calibration files
    for calib in out/ladder_calib_*.json; do
        [ -f "$calib" ] && sync_file "$calib" "$BACKUP_DIR"
    done

    # Missing C0 if it exists
    [ -f "missing_c0.json" ] && sync_file "missing_c0.json" "$BACKUP_DIR"

    # Guide files
    for guide in last_status.md DOTHIS.md TODO_Sep_22.md 1-Progress.md 2-Progress.md; do
        sync_file "$guide" "$BACKUP_DIR"
    done

    # CLAUDE.md from parent
    [ -f "../CLAUDE.md" ] && cp -v ../CLAUDE.md "$BACKUP_DIR/" 2>&1 | sed "s/^/  /"

    # Scripts
    sync_file "verify_affine.py" "$BACKUP_DIR"
    sync_file "predict_next_halfblock.py" "$BACKUP_DIR"
    sync_file "compute_c0_leftpad.py" "$BACKUP_DIR"
    sync_file "tools/patch_cstar_from_bridge_pair.py" "$BACKUP_DIR"

    # Data file
    sync_file "data/btc_puzzle_1_160_full.csv" "$BACKUP_DIR"

    # Update inventory
    cat > "$BACKUP_DIR/BACKUP_INVENTORY.md" <<EOF
# ZBook Ladder Backup Inventory
**Last Updated:** $(date '+%Y-%m-%d %H:%M:%S')
**Source:** $SOURCE_DIR

## Auto-Sync Enabled
This backup is automatically synchronized when files change.

## Contents

### Database Files
$(ls -lh db/kh.db 2>/dev/null | awk '{print "- kh.db ("$5")"}' || echo "- kh.db (missing)")

### Calibration Files
$(ls -1 out/ladder_calib_*.json 2>/dev/null | xargs -I {} basename {} | sed 's/^/- /')
$([ -f "missing_c0.json" ] && echo "- missing_c0.json" || echo "- missing_c0.json (not yet created)")

### Guide Files
- last_status.md - **START HERE** Current session status and next steps
- DOTHIS.md - One-shot checklist for clean rebuild
- TODO_Sep_22.md - Known issues and action items
- 1-Progress.md - Historical progress documentation
- 2-Progress.md - Additional progress notes
- CLAUDE.md - Repository instructions

### Scripts
- verify_affine.py - Forward/reverse verification
- predict_next_halfblock.py - Prediction tool
- compute_c0_leftpad.py - Drift computation
- patch_cstar_from_bridge_pair.py - Calibration patcher

### Data Files
- btc_puzzle_1_160_full.csv - Source data

## Current State
**Last Sync:** $(date '+%Y-%m-%d %H:%M:%S')

## NAS Destination
This folder should be copied to: \`$NAS_PATH\`

## Manual Copy to NAS
From Windows File Explorer:
1. Navigate to: C:\\temp\\ZBook-Ladder-Backup-20251127_121742
2. Copy entire folder to: $NAS_PATH

From WSL/Linux (if NAS mounted):
\`\`\`bash
rsync -av "$BACKUP_DIR/" /path/to/nas/ZBook-Ladder/
\`\`\`
EOF

    echo -e "${GREEN}✅ Sync completed at $(date '+%H:%M:%S')${NC}"
    echo ""
}

# Main sync logic
if [ "$1" = "--once" ]; then
    # Single sync
    cd "$SOURCE_DIR" || exit 1
    full_sync
    exit 0
elif [ "$1" = "--watch" ]; then
    # Continuous monitoring mode
    cd "$SOURCE_DIR" || exit 1
    echo -e "${BLUE}Watching for changes... (Ctrl+C to stop)${NC}"
    echo ""

    # Initial sync
    full_sync

    # Watch for changes (using inotifywait if available, otherwise polling)
    if command -v inotifywait &> /dev/null; then
        while true; do
            inotifywait -r -e modify,create,move,delete \
                db/ out/ *.md *.py tools/ data/ 2>/dev/null
            sleep 2  # Debounce
            full_sync
        done
    else
        # Fallback to polling every 30 seconds
        echo -e "${YELLOW}Note: inotify-tools not installed, using polling mode${NC}"
        while true; do
            sleep 30
            full_sync
        done
    fi
else
    echo "Usage:"
    echo "  $0 --once    # Sync once and exit"
    echo "  $0 --watch   # Continuous monitoring (recommended)"
    echo ""
    echo "Recommended: Run in background with:"
    echo "  $0 --watch &"
    exit 1
fi
