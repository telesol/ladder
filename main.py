#!/usr/bin/env python3
"""
Ladder Agents - Main Entry Point
24/7 Autonomous Bitcoin Puzzle Discovery System
"""
import os
import sys
import asyncio
import argparse
from datetime import datetime

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rag'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sync'))

def print_banner():
    """Print startup banner"""
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║     ██╗      █████╗ ██████╗ ██████╗ ███████╗██████╗                       ║
║     ██║     ██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗                      ║
║     ██║     ███████║██║  ██║██║  ██║█████╗  ██████╔╝                      ║
║     ██║     ██╔══██║██║  ██║██║  ██║██╔══╝  ██╔══██╗                      ║
║     ███████╗██║  ██║██████╔╝██████╔╝███████╗██║  ██║                      ║
║     ╚══════╝╚═╝  ╚═╝╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝                      ║
║                                                                           ║
║              █████╗  ██████╗ ███████╗███╗   ██╗████████╗███████╗          ║
║             ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██╔════╝          ║
║             ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   ███████╗          ║
║             ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ╚════██║          ║
║             ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ███████║          ║
║             ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝          ║
║                                                                           ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  Claude Orchestrator | Ollama Cloud Agents | Local RAG | NAS Sync        ║
║  Pure Math - No Stubs - No Hardcoding - Full BTC Verification            ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """)

async def run_daemon():
    """Run the 24/7 daemon"""
    from daemon import LadderDaemon
    daemon = LadderDaemon()
    await daemon.run()

async def run_single_goal(goal: str):
    """Run a single goal"""
    from orchestrator import ClaudeOrchestrator
    orchestrator = ClaudeOrchestrator()
    result = await orchestrator.execute_goal(goal)
    print(f"\nResult:\n{result.get('synthesis', 'No synthesis')}")
    return result

def run_rag_index():
    """Index all data for RAG"""
    from vector_store import VectorStore
    base_dir = os.path.dirname(os.path.abspath(__file__))

    store = VectorStore(os.path.join(base_dir, "rag/vectors"))

    # Index training data
    training_path = os.path.join(base_dir, "data/training_data.json")
    if os.path.exists(training_path):
        store.index_training_data(training_path)
        print(f"Indexed training data: {training_path}")

    # Index memory
    memory_path = os.path.join(base_dir, "db/memory.db")
    if os.path.exists(memory_path):
        store.index_memory_db(memory_path)
        print(f"Indexed memory: {memory_path}")

    print(f"\nTotal documents indexed: {len(store.documents)}")

def run_rag_search(query: str):
    """Search RAG"""
    from vector_store import VectorStore
    base_dir = os.path.dirname(os.path.abspath(__file__))

    store = VectorStore(os.path.join(base_dir, "rag/vectors"))
    results = store.search(query, top_k=5)

    print(f"\nSearch results for: {query}\n")
    for doc, score in results:
        print(f"[Score: {score:.4f}]")
        print(doc['content'][:300])
        print("---\n")

def check_nas_status():
    """Check NAS status"""
    from nas_sync import NASSync
    sync = NASSync()
    status = sync.get_status()

    print(f"\nNAS Status:")
    print(f"  Host: {status['nas_host']} ({status['nas_name']})")
    print(f"  Available: {'Yes' if status['nas_available'] else 'No'}")
    print(f"  Mounted: {'Yes' if status['mounted'] else 'No'}")
    print(f"  Last Sync: {status['last_sync'] or 'Never'}")

def run_nas_sync():
    """Run NAS sync"""
    from nas_sync import NASSync
    sync = NASSync()

    print("Checking NAS availability...")
    if not sync.check_nas_available():
        print("NAS not available!")
        return

    print("Mounting NAS...")
    if not sync.mount_nas():
        print("Failed to mount. Set NAS_USER and NAS_PASS environment variables.")
        return

    print("Syncing...")
    result = sync.sync_to_nas()
    print(f"Sync result: {result}")

def main():
    parser = argparse.ArgumentParser(description="Ladder Agents - Autonomous Bitcoin Puzzle Discovery")
    parser.add_argument('command', choices=['daemon', 'goal', 'rag-index', 'rag-search', 'nas-status', 'nas-sync', 'status'],
                        help="Command to run")
    parser.add_argument('--goal', '-g', type=str, help="Goal to execute (for 'goal' command)")
    parser.add_argument('--query', '-q', type=str, help="Query for RAG search")

    args = parser.parse_args()

    print_banner()

    if args.command == 'daemon':
        print("Starting 24/7 daemon mode...")
        asyncio.run(run_daemon())

    elif args.command == 'goal':
        goal = args.goal or "Explore the ladder patterns and find new insights"
        print(f"Executing goal: {goal}")
        asyncio.run(run_single_goal(goal))

    elif args.command == 'rag-index':
        print("Indexing data for RAG...")
        run_rag_index()

    elif args.command == 'rag-search':
        query = args.query or "drift constant"
        run_rag_search(query)

    elif args.command == 'nas-status':
        check_nas_status()

    elif args.command == 'nas-sync':
        run_nas_sync()

    elif args.command == 'status':
        print("\nSystem Status:")
        print(f"  Base Dir: {os.path.dirname(os.path.abspath(__file__))}")
        print(f"  Timestamp: {datetime.now().isoformat()}")

        # Check databases
        base_dir = os.path.dirname(os.path.abspath(__file__))
        for db in ['db/kh.db', 'db/memory.db']:
            path = os.path.join(base_dir, db)
            if os.path.exists(path):
                size = os.path.getsize(path) / 1024
                print(f"  {db}: {size:.1f} KB")
            else:
                print(f"  {db}: Not found")

        # Check NAS
        check_nas_status()

if __name__ == "__main__":
    main()
