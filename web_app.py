#!/usr/bin/env python3
"""
Bitcoin Puzzle Ladder - Web Interface
A visual interface for training AI and exploring the ladder mathematics
"""
from flask import Flask, render_template, jsonify, request
import sqlite3
import json
import os
import subprocess
import sys
from gpu_monitor import get_gpu_stats, get_system_stats, search_models
# V3: Tool-based agent - AI explains, Python scripts do the real math
from agent_v3 import get_conversation_history, get_agent
from ollama_integration import list_ollama_models_sync, generate_with_ollama_sync

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ladder-quest-2025'

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KH_ASSIST = os.path.join(BASE_DIR, 'kh-assist')
DB_PATH = os.path.join(KH_ASSIST, 'db', 'kh.db')
CALIB_PATH = os.path.join(KH_ASSIST, 'out', 'ladder_calib_29_70_full.json')
CSV_PATH = os.path.join(KH_ASSIST, 'data', 'btc_puzzle_1_160_full.csv')

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get current system status with verification and drift statistics"""
    try:
        # Check database
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # Get all puzzles with their solve status (solved = has actual hex, not '0x?')
        cur.execute("SELECT bits, actual_hex FROM lcg_residuals ORDER BY bits")
        rows = cur.fetchall()

        puzzles = []  # All puzzle numbers in DB
        solved_puzzles = []  # Only puzzles with actual keys (not '0x?')
        unsolved_puzzles = []  # Puzzles with '0x?' placeholder

        for bits, actual_hex in rows:
            puzzles.append(bits)
            if actual_hex and actual_hex != '0x?' and not actual_hex.endswith('?'):
                solved_puzzles.append(bits)
            else:
                unsolved_puzzles.append(bits)

        puzzle_count = len(solved_puzzles)  # Count only solved puzzles
        conn.close()

        # Check calibration
        with open(CALIB_PATH) as f:
            calib = json.load(f)

        # Analyze calibration
        a_matrix = calib['A']
        cstar = calib['Cstar']

        # Count non-zero drifts
        nonzero_drifts = 0
        for block in cstar.values():
            for lane_data in block.values():
                if isinstance(lane_data, list):
                    if any(v != 0 for v in lane_data):
                        nonzero_drifts += 1

        # Find consecutive range dynamically (only for solved puzzles)
        consecutive = []
        bridges = []
        prev = 0
        for p in solved_puzzles:
            if prev == 0 or p == prev + 1:
                consecutive.append(p)
            else:
                bridges.append(p)
            prev = p

        # Run quick verification to get current accuracy (dynamic range)
        agent = get_agent()
        verify_result = agent.tools.verify_ladder()  # Uses dynamic defaults
        verification = {
            'accuracy': verify_result.get('accuracy', 'N/A'),
            'total_matches': verify_result.get('total_matches', 0),
            'total_checks': verify_result.get('total_checks', 0),
            'perfect': verify_result.get('perfect', False),
            'mismatch_count': verify_result.get('mismatch_count', 0)
        }

        # Get drift discovery stats (dynamic range)
        drift_result = agent.tools.compute_drift_stats()  # Uses dynamic defaults
        drift_stats = {}
        if drift_result.get('success'):
            suggested = drift_result.get('suggested_drift', {})
            lanes_100pct = sum(1 for d in suggested.values() if d.get('percentage', '').startswith('100'))
            drift_stats = {
                'lanes_at_100pct': lanes_100pct,
                'suggested_drift': {str(k): v for k, v in suggested.items()}
            }

        return jsonify({
            'success': True,
            'database': {
                'total_puzzles': puzzle_count,  # Only solved count
                'puzzles': solved_puzzles,  # Only solved puzzles for grid coloring
                'consecutive': consecutive,
                'bridges': bridges,
                'unsolved': unsolved_puzzles,  # Puzzles with '0x?' placeholder
                'missing': [i for i in range(1, 161) if i not in puzzles],  # Not in DB at all
                'total_range': 160  # Bitcoin Puzzle has 160 puzzles
            },
            'calibration': {
                'a_matrix': a_matrix,
                'cstar': cstar,
                'nonzero_drifts': nonzero_drifts
            },
            'verification': verification,
            'drift_stats': drift_stats
        })
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'traceback': traceback.format_exc()})

@app.route('/api/puzzles/<int:puzzle_num>')
def get_puzzle(puzzle_num):
    """Get specific puzzle details"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT bits, actual_hex FROM lcg_residuals WHERE bits=?", (puzzle_num,))
        row = cur.fetchone()
        conn.close()

        if row:
            return jsonify({
                'success': True,
                'bits': row[0],
                'hex': row[1],
                'in_database': True
            })
        else:
            return jsonify({
                'success': True,
                'bits': puzzle_num,
                'in_database': False
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/verify', methods=['POST'])
def run_verification():
    """Run verification script"""
    try:
        os.chdir(KH_ASSIST)
        result = subprocess.run(
            [sys.executable, 'verify_affine.py'],
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout + result.stderr

        # Parse output for percentages
        forward_pct = None
        reverse_pct = None

        for line in output.split('\n'):
            if 'Forward test' in line and '%' in line:
                try:
                    forward_pct = float(line.split('=')[-1].strip().rstrip('%'))
                except:
                    pass
            if 'Reverse test' in line and '%' in line:
                try:
                    reverse_pct = float(line.split('=')[-1].strip().rstrip('%'))
                except:
                    pass

        success = forward_pct == 100.0 and reverse_pct == 100.0

        return jsonify({
            'success': True,
            'verification_passed': success,
            'forward_percentage': forward_pct,
            'reverse_percentage': reverse_pct,
            'output': output
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/compute-drift', methods=['POST'])
def compute_drift():
    """Compute missing drift C[0][ℓ][0]"""
    try:
        os.chdir(KH_ASSIST)

        # Extract bridge values from database
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT substr(actual_hex, 3, 32) FROM lcg_residuals WHERE bits=75")
        hex75 = cur.fetchone()[0]
        cur.execute("SELECT substr(actual_hex, 3, 32) FROM lcg_residuals WHERE bits=80")
        hex80 = cur.fetchone()[0]
        conn.close()

        # Set environment variables
        env = os.environ.copy()
        env['HEX75'] = hex75
        env['HEX80'] = hex80

        # Run computation
        result = subprocess.run(
            [sys.executable, 'compute_missing_drift.py'],
            capture_output=True,
            text=True,
            env=env,
            timeout=60
        )

        output = result.stdout + result.stderr

        # Check if drift file was created
        drift_file = os.path.join(KH_ASSIST, 'missing_c0.json')
        drift_data = None
        if os.path.exists(drift_file):
            with open(drift_file) as f:
                drift_data = json.load(f)

        return jsonify({
            'success': result.returncode == 0,
            'output': output,
            'drift': drift_data,
            'hex75': hex75,
            'hex80': hex80
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/patch-calibration', methods=['POST'])
def patch_calibration():
    """Patch calibration with computed drift"""
    try:
        os.chdir(KH_ASSIST)
        result = subprocess.run(
            [sys.executable, 'patch_calibration.py'],
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout + result.stderr

        return jsonify({
            'success': result.returncode == 0,
            'output': output
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/generate', methods=['POST'])
def generate_puzzle():
    """Generate next puzzle"""
    try:
        os.chdir(KH_ASSIST)
        result = subprocess.run(
            [sys.executable, 'predict_next_halfblock.py'],
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout + result.stderr

        # Parse output for generated hex
        generated_hex = None
        for line in output.split('\n'):
            if 'Predicted bits' in line and '0x' in line:
                try:
                    generated_hex = line.split('0x')[1].strip()
                except:
                    pass

        return jsonify({
            'success': result.returncode == 0,
            'output': output,
            'generated_hex': generated_hex
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/validate-address', methods=['POST'])
def validate_address():
    """Validate generated address"""
    try:
        data = request.json
        privkey_hex = data.get('privkey_hex', '')
        puzzle_num = data.get('puzzle_num', 71)

        os.chdir(KH_ASSIST)
        result = subprocess.run(
            [sys.executable, 'validate_address.py', privkey_hex, str(puzzle_num)],
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout + result.stderr

        # Check if validation passed
        validation_passed = 'MATCH!' in output and result.returncode == 0

        return jsonify({
            'success': True,
            'validation_passed': validation_passed,
            'output': output
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/documentation/<doc_name>')
def get_documentation(doc_name):
    """Get documentation content"""
    try:
        doc_path = os.path.join(BASE_DIR, f'{doc_name}.md')
        if os.path.exists(doc_path):
            with open(doc_path) as f:
                content = f.read()
            return jsonify({'success': True, 'content': content})
        else:
            return jsonify({'success': False, 'error': 'Document not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/gpu-stats')
def gpu_stats():
    """Get GPU statistics"""
    return jsonify(get_gpu_stats())

@app.route('/api/system-stats')
def system_stats():
    """Get system statistics"""
    return jsonify(get_system_stats())

@app.route('/api/models/search')
def models_search():
    """Search for AI models"""
    query = request.args.get('q', 'qwen')
    return jsonify(search_models(query))


@app.route('/api/chat/history')
def chat_history():
    """Get chat conversation history"""
    history = get_conversation_history()
    return jsonify({'history': history})

@app.route('/api/models/load', methods=['POST'])
def load_model_endpoint():
    """Load AI model for advanced reasoning"""
    try:
        # Test Ollama connection
        models = list_ollama_models_sync()
        
        if models:
            return jsonify({
                'success': True,
                'message': f'Ollama connected successfully with {len(models)} models available',
                'models': [m.get('name', 'Unknown') for m in models]
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No Ollama models available',
                'models': []
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/models/status')
def model_status():
    """Check if AI model is loaded"""
    try:
        models = list_ollama_models_sync()
        
        return jsonify({
            'success': True,
            'is_loaded': len(models) > 0,
            'model_type': 'Ollama Integration',
            'available_models': [m.get('name', 'Unknown') for m in models],
            'model_count': len(models)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/memory/stats')
def memory_stats():
    """Get memory system statistics"""
    try:
        from memory_system import get_memory_system
        memory = get_memory_system()

        conversations = memory.get_recent_conversations(limit=10000)
        progress = memory.get_progress_summary(limit=10000)
        discoveries = memory.get_discoveries()
        learnings = memory.get_learnings()

        return jsonify({
            'success': True,
            'stats': {
                'total_conversations': len(conversations),
                'progress_events': len(progress),
                'discoveries': len(discoveries),
                'verified_discoveries': len([d for d in discoveries if d['verified']]),
                'learnings': len(learnings),
                'high_confidence_learnings': len([l for l in learnings if l['confidence'] >= 0.8])
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/memory/discoveries')
def memory_discoveries():
    """Get all discoveries"""
    try:
        from memory_system import get_memory_system
        memory = get_memory_system()

        discoveries = memory.get_discoveries()

        return jsonify({
            'success': True,
            'discoveries': discoveries
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/memory/context')
def memory_context():
    """Get full context summary"""
    try:
        from memory_system import get_memory_system
        memory = get_memory_system()

        context = memory.build_context_summary()

        return jsonify({
            'success': True,
            'context': context
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/models/available')
def get_available_models():
    """Get list of available Ollama models"""
    try:
        models = list_ollama_models_sync()
        model_names = [m.get('name', 'Unknown') for m in models] if models else []

        # Get current model from agent (use agent_v3, not v2)
        agent = get_agent()
        current_model = agent.model_name

        return jsonify({
            'success': True,
            'models': model_names,
            'current_model': current_model
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'models': []})

@app.route('/api/models/select', methods=['POST'])
def select_model():
    """Select a model for the chat agent"""
    try:
        data = request.json
        model_name = data.get('model', '')

        if not model_name:
            return jsonify({'success': False, 'error': 'No model specified'})

        # Use agent_v3, not v2
        agent = get_agent()
        agent.model_name = model_name

        return jsonify({
            'success': True,
            'message': f'Model changed to {model_name}',
            'current_model': model_name
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/chat', methods=['POST'])
def chat_with_rag():
    """Chat with AI agent - AI explains, Python does the math"""
    data = request.json
    message = data.get('message', '')
    use_rag = data.get('use_rag', True)

    if not message:
        return jsonify({'error': 'No message provided'})

    agent = get_agent()
    response = agent.process_message(message, use_rag=use_rag)
    return jsonify(response)

@app.route('/api/health')
def system_health():
    """Get comprehensive system health status"""
    health = {
        'daemon': {'status': 'unknown', 'active': False},
        'ollama': {'status': 'unknown', 'models': 0},
        'database': {'status': 'unknown', 'puzzles': 0},
        'memory': {'status': 'unknown', 'discoveries': 0, 'learnings': 0}
    }

    # Check daemon status
    try:
        result = subprocess.run(
            ['systemctl', '--user', 'is-active', 'ladder-daemon.service'],
            capture_output=True, text=True, timeout=5
        )
        daemon_active = result.stdout.strip() == 'active'
        health['daemon'] = {
            'status': 'running' if daemon_active else 'stopped',
            'active': daemon_active
        }
    except:
        health['daemon'] = {'status': 'error', 'active': False}

    # Check Ollama
    try:
        models = list_ollama_models_sync()
        health['ollama'] = {
            'status': 'connected' if models else 'no models',
            'models': len(models) if models else 0
        }
    except:
        health['ollama'] = {'status': 'offline', 'models': 0}

    # Check database
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM lcg_residuals")
        puzzle_count = cur.fetchone()[0]
        conn.close()
        health['database'] = {
            'status': 'healthy',
            'puzzles': puzzle_count
        }
    except Exception as e:
        health['database'] = {'status': 'error', 'puzzles': 0, 'error': str(e)}

    # Check memory system
    try:
        from memory_system import get_memory_system
        memory = get_memory_system()
        discoveries = memory.get_discoveries()
        learnings = memory.get_learnings()
        health['memory'] = {
            'status': 'healthy',
            'discoveries': len(discoveries),
            'verified_discoveries': len([d for d in discoveries if d['verified']]),
            'learnings': len(learnings)
        }
    except Exception as e:
        health['memory'] = {'status': 'error', 'discoveries': 0, 'learnings': 0}

    return jsonify({'success': True, 'health': health})

@app.route('/api/progress')
def system_progress():
    """Get system progress assessment and learning metrics"""
    try:
        from memory_system import get_memory_system
        memory = get_memory_system()

        # Get learnings
        learnings = memory.get_learnings()
        high_conf_learnings = [l for l in learnings if l.get('confidence', 0) >= 0.8]

        # Get progress events
        progress_events = memory.get_progress_summary(limit=100)

        # Calculate success rate from progress events
        total_executions = len([p for p in progress_events if p.get('event_type') == 'strategy_execution'])
        successful_executions = len([p for p in progress_events
                                    if p.get('event_type') == 'strategy_execution'
                                    and p.get('data', {}).get('success', False)])

        success_rate = successful_executions / total_executions if total_executions > 0 else 0

        # Get discoveries
        discoveries = memory.get_discoveries()

        # Group learnings by topic
        topics = {}
        for l in learnings:
            topic = l.get('topic', 'unknown')
            if topic not in topics:
                topics[topic] = []
            topics[topic].append(l)

        # Recent progress (last 10)
        recent_progress = progress_events[:10]

        return jsonify({
            'success': True,
            'progress': {
                'total_learnings': len(learnings),
                'high_confidence_learnings': len(high_conf_learnings),
                'total_discoveries': len(discoveries),
                'verified_discoveries': len([d for d in discoveries if d.get('verified', False)]),
                'strategy_executions': total_executions,
                'successful_executions': successful_executions,
                'success_rate': success_rate,
                'learning_topics': {k: len(v) for k, v in topics.items()},
                'recent_progress': recent_progress,
                'recent_learnings': learnings[:10]
            }
        })
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'traceback': traceback.format_exc()})

# ============ ORACLE ENDPOINTS ============

@app.route('/oracle')
def oracle_page():
    """Oracle - Multi-Agent System Monitor"""
    return render_template('oracle.html')

@app.route('/api/oracle/status')
def oracle_status():
    """Get Oracle system status"""
    try:
        # Check Ollama
        models = list_ollama_models_sync()
        model_names = [m.get('name', '') for m in models] if models else []

        # Check GPU
        gpu_stats = get_gpu_stats()
        gpu_memory = 'N/A'
        if gpu_stats.get('gpus'):
            gpu = gpu_stats['gpus'][0]
            gpu_memory = f"{gpu.get('memory_used', 0):.1f}GB / {gpu.get('memory_total', 0):.1f}GB"

        # Get target puzzle from config
        target_puzzle = None  # All unsolved
        try:
            config_path = os.path.join(BASE_DIR, 'config', 'puzzle_config.json')
            if os.path.exists(config_path):
                with open(config_path) as f:
                    config = json.load(f)
                    target_puzzle = config.get('target_puzzle')  # No default
        except:
            pass

        return jsonify({
            'success': True,
            'ollama_connected': len(models) > 0,
            'model_count': len(models),
            'models': model_names,
            'gpu_memory': gpu_memory,
            'target_puzzle': target_puzzle,
            'active_tasks': 0,
            'agents': {
                'a-solver': {'model': 'qwen3-vl:8b', 'available': 'qwen3-vl:8b' in str(model_names)},
                'b-solver': {'model': 'phi4-reasoning:14b', 'available': 'phi4-reasoning:14b' in str(model_names)},
                'c-solver': {'model': 'qwq:32b', 'available': 'qwq:32b' in str(model_names)},
                'maestro': {'model': 'Claude', 'available': True}
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/oracle/query', methods=['POST'])
def oracle_query():
    """Query an agent in Oracle mode (non-streaming)"""
    try:
        data = request.json
        message = data.get('message', '')
        agent = data.get('agent', 'a-solver')

        # Map agent to model
        agent_models = {
            'a-solver': 'qwen3-vl:8b',
            'b-solver': 'phi4-reasoning:14b',
            'c-solver': 'qwq:32b',
            'auto': 'qwen3-vl:8b'  # Default to A-Solver for auto
        }
        model = agent_models.get(agent, 'qwen3-vl:8b')

        # Query Ollama
        response = generate_with_ollama_sync(message, model)

        return jsonify({
            'success': True,
            'agent': agent,
            'model': model,
            'response': response
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/oracle/stream')
def oracle_stream():
    """Stream oracle response using Server-Sent Events"""
    import requests as req

    agent = request.args.get('agent', 'a-solver')
    message = request.args.get('message', '')

    # Map agent to model
    agent_models = {
        'a-solver': 'qwen3-vl:8b',
        'b-solver': 'phi4-reasoning:14b',
        'c-solver': 'qwq:32b',
        'auto': 'qwen3-vl:8b'
    }
    model = agent_models.get(agent, 'qwen3-vl:8b')

    def generate():
        try:
            response = req.post(
                'http://localhost:11434/api/generate',
                json={'model': model, 'prompt': message, 'stream': True},
                stream=True,
                timeout=600  # 10 minute timeout for deep reasoning
            )

            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        token = data.get('response', '')
                        done = data.get('done', False)
                        yield f"data: {json.dumps({'token': token, 'done': done})}\n\n"
                        if done:
                            break
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

    return app.response_class(
        generate(),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'Connection': 'keep-alive'}
    )

@app.route('/api/oracle/agents')
def oracle_agents():
    """Get detailed agent information"""
    try:
        agents = {
            'a-solver': {
                'name': 'A-Solver',
                'model': 'qwen3-vl:8b',
                'size': '6.1GB',
                'specialty': 'Fast analysis, wallet forensics',
                'certified': True,
                'score': '10/10'
            },
            'b-solver': {
                'name': 'B-Solver',
                'model': 'phi4-reasoning:14b',
                'size': '11GB',
                'specialty': 'Deep reasoning, anomaly detection',
                'certified': False,
                'score': '7/12'
            },
            'c-solver': {
                'name': 'C-Solver',
                'model': 'qwq:32b',
                'size': '19GB',
                'specialty': 'Prediction, synthesis, mathematical reasoning',
                'certified': False,
                'score': 'Oracle mode'
            },
            'maestro': {
                'name': 'Maestro',
                'model': 'Claude (Opus)',
                'size': 'Cloud',
                'specialty': 'Orchestration, coordination',
                'certified': True,
                'score': 'N/A'
            }
        }

        # Check which models are available
        models = list_ollama_models_sync()
        model_names = [m.get('name', '') for m in models] if models else []

        for agent_id, agent in agents.items():
            if agent_id == 'maestro':
                agent['available'] = True
            else:
                agent['available'] = agent['model'] in str(model_names)

        return jsonify({'success': True, 'agents': agents})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============ AGENT MEMORY ENDPOINTS ============

@app.route('/api/oracle/memory/stats')
def oracle_memory_stats():
    """Get agent memory statistics"""
    try:
        from agent_memory import get_agent_memory
        memory = get_agent_memory()
        stats = memory.get_statistics()
        agent_status = memory.get_agent_status()

        return jsonify({
            'success': True,
            'stats': stats,
            'agents': agent_status
        })
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'traceback': traceback.format_exc()})

@app.route('/api/oracle/memory/history/<agent_id>')
def oracle_memory_history(agent_id):
    """Get agent conversation history"""
    try:
        from agent_memory import get_agent_memory
        memory = get_agent_memory()

        limit = request.args.get('limit', 20, type=int)
        history = memory.get_agent_history(agent_id, limit=limit)

        return jsonify({
            'success': True,
            'agent_id': agent_id,
            'history': history
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/oracle/memory/oracle-queries')
def oracle_memory_queries():
    """Get oracle query history"""
    try:
        from agent_memory import get_agent_memory
        memory = get_agent_memory()

        agent_id = request.args.get('agent', None)
        limit = request.args.get('limit', 20, type=int)
        queries = memory.get_oracle_history(agent_id=agent_id, limit=limit)

        return jsonify({
            'success': True,
            'queries': queries
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/oracle/memory/insights')
def oracle_memory_insights():
    """Get agent insights"""
    try:
        from agent_memory import get_agent_memory
        memory = get_agent_memory()

        agent_id = request.args.get('agent', None)
        category = request.args.get('category', None)
        min_confidence = request.args.get('min_confidence', 0.0, type=float)

        insights = memory.get_agent_insights(
            agent_id=agent_id,
            category=category,
            min_confidence=min_confidence
        )

        return jsonify({
            'success': True,
            'insights': insights
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/oracle/memory/shared')
def oracle_memory_shared():
    """Get shared knowledge base"""
    try:
        from agent_memory import get_agent_memory
        memory = get_agent_memory()

        fact_type = request.args.get('type', None)
        shared = memory.get_shared_knowledge(fact_type=fact_type)

        return jsonify({
            'success': True,
            'shared_knowledge': shared
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/oracle/memory/context/<agent_id>')
def oracle_memory_context(agent_id):
    """Get full context for an agent"""
    try:
        from agent_memory import get_agent_memory
        memory = get_agent_memory()

        include_shared = request.args.get('include_shared', 'true').lower() == 'true'
        context = memory.build_agent_context(agent_id, include_shared=include_shared)

        return jsonify({
            'success': True,
            'agent_id': agent_id,
            'context': context
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/oracle/memory/save', methods=['POST'])
def oracle_memory_save():
    """Save a message to agent memory"""
    try:
        from agent_memory import get_agent_memory
        memory = get_agent_memory()

        data = request.json
        agent_id = data.get('agent_id')
        role = data.get('role', 'user')
        content = data.get('content', '')
        tokens = data.get('tokens')
        response_time = data.get('response_time')

        if not agent_id or not content:
            return jsonify({'success': False, 'error': 'agent_id and content required'})

        memory.save_agent_message(agent_id, role, content, tokens, response_time)

        return jsonify({
            'success': True,
            'message': f'Saved message for {agent_id}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/oracle/memory/insight', methods=['POST'])
def oracle_memory_add_insight():
    """Add an insight from an agent"""
    try:
        from agent_memory import get_agent_memory
        memory = get_agent_memory()

        data = request.json
        agent_id = data.get('agent_id')
        category = data.get('category')
        insight = data.get('insight')
        confidence = data.get('confidence', 0.5)
        source_query = data.get('source_query')
        tags = data.get('tags', [])

        if not agent_id or not category or not insight:
            return jsonify({'success': False, 'error': 'agent_id, category, and insight required'})

        memory.add_agent_insight(
            agent_id, category, insight,
            confidence=confidence,
            source_query=source_query,
            tags=tags
        )

        return jsonify({
            'success': True,
            'message': f'Added insight for {agent_id}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/oracle/memory/knowledge', methods=['POST'])
def oracle_memory_add_knowledge():
    """Add shared knowledge"""
    try:
        from agent_memory import get_agent_memory
        memory = get_agent_memory()

        data = request.json
        fact_type = data.get('fact_type')
        fact = data.get('fact')
        discovered_by = data.get('discovered_by')
        confidence = data.get('confidence', 0.5)
        metadata = data.get('metadata')

        if not fact_type or not fact or not discovered_by:
            return jsonify({'success': False, 'error': 'fact_type, fact, and discovered_by required'})

        memory.add_shared_knowledge(
            fact_type, fact, discovered_by,
            confidence=confidence,
            metadata=metadata
        )

        return jsonify({
            'success': True,
            'message': 'Added shared knowledge'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/oracle/memory/init', methods=['POST'])
def oracle_memory_init():
    """Initialize agent memory with default configurations"""
    try:
        from agent_memory import initialize_agents
        initialize_agents()

        return jsonify({
            'success': True,
            'message': 'Agent memory initialized with default configurations'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============ END ORACLE ENDPOINTS ============

if __name__ == '__main__':
    print("🚀 Bitcoin Puzzle Ladder - Web Interface")
    print("=" * 60)
    print(f"📂 Base directory: {BASE_DIR}")
    print(f"🗄️  Database: {DB_PATH}")
    print(f"⚙️  Calibration: {CALIB_PATH}")
    print("=" * 60)
    print("🌐 Starting web server...")
    print("📍 Open your browser to: http://localhost:5050")
    print("📍 Oracle interface at: http://localhost:5050/oracle")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5050)
