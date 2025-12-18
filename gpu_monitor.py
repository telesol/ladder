#!/usr/bin/env python3
"""
GPU Monitoring Module
Queries NVIDIA GPUs and system stats
"""
import subprocess
import json
import os

def get_gpu_stats():
    """Get GPU statistics using nvidia-smi with PyTorch fallback for unified memory systems"""
    try:
        cmd = [
            'nvidia-smi',
            '--query-gpu=index,name,memory.total,memory.used,memory.free,utilization.gpu,utilization.memory,temperature.gpu,power.draw,power.limit',
            '--format=csv,noheader,nounits'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

        if result.returncode != 0:
            return {'error': 'nvidia-smi failed', 'gpus': []}

        gpus = []
        is_unified_memory = False

        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 8:
                # Helper function to parse values that might be [N/A]
                def parse_value(val, default=0, as_type=int):
                    try:
                        if val == '[N/A]' or not val:
                            return default
                        return as_type(float(val))
                    except:
                        return default

                gpu_index = parse_value(parts[0], 0)
                memory_total = parse_value(parts[2], 0)
                memory_used = parse_value(parts[3], 0)
                memory_free = parse_value(parts[4], 0)

                # If memory values are 0 (N/A from nvidia-smi), this is likely unified memory
                if memory_total == 0:
                    is_unified_memory = True

                    # Try to get GPU memory via system python with torch
                    try:
                        torch_cmd = ['python3', '-c',
                            'import torch; '
                            'print(int(torch.cuda.get_device_properties(0).total_memory/(1024*1024))) '
                            'if torch.cuda.is_available() else print(0)']
                        torch_result = subprocess.run(torch_cmd, capture_output=True, text=True, timeout=5)
                        if torch_result.returncode == 0 and torch_result.stdout.strip():
                            memory_total = int(torch_result.stdout.strip())
                    except:
                        pass  # Fallback to meminfo

                    # If still no GPU memory, fall back to system memory (for unified mem)
                    if memory_total == 0:
                        memory_total = 122880  # Default ~120GB for GB10

                    # Get system memory usage for unified memory estimate
                    try:
                        with open('/proc/meminfo') as f:
                            meminfo = f.read()
                            mem_total_sys = 0
                            mem_avail_sys = 0
                            for memline in meminfo.split('\n'):
                                if memline.startswith('MemTotal:'):
                                    mem_total_sys = int(memline.split()[1]) // 1024  # MB
                                elif memline.startswith('MemAvailable:'):
                                    mem_avail_sys = int(memline.split()[1]) // 1024  # MB

                            # Estimate GPU memory usage from system memory
                            memory_used = mem_total_sys - mem_avail_sys
                            memory_free = mem_avail_sys
                    except:
                        memory_used = 0
                        memory_free = memory_total

                gpus.append({
                    'index': gpu_index,
                    'name': parts[1],
                    'memory_total': memory_total,
                    'memory_used': memory_used,
                    'memory_free': memory_free,
                    'gpu_util': parse_value(parts[5], 0),
                    'mem_util': parse_value(parts[6], 0),
                    'temperature': parse_value(parts[7], 0),
                    'power_draw': parse_value(parts[8], 0, float) if len(parts) > 8 else 0,
                    'power_limit': parse_value(parts[9], 0, float) if len(parts) > 9 else 0,
                    'unified_memory': is_unified_memory
                })

        return {
            'success': True,
            'gpu_count': len(gpus),
            'gpus': gpus,
            'unified_memory': is_unified_memory
        }
    except Exception as e:
        return {'error': str(e), 'gpus': []}

def get_system_stats():
    """Get system statistics"""
    try:
        # CPU info
        cpu_percent = 0
        mem_percent = 0

        # Try to get from /proc/stat for CPU
        try:
            with open('/proc/meminfo') as f:
                meminfo = f.read()
                for line in meminfo.split('\n'):
                    if line.startswith('MemTotal:'):
                        mem_total = int(line.split()[1]) // 1024  # MB
                    elif line.startswith('MemAvailable:'):
                        mem_avail = int(line.split()[1]) // 1024  # MB
                mem_used = mem_total - mem_avail
                mem_percent = (mem_used / mem_total) * 100
        except:
            mem_total = 0
            mem_used = 0
            mem_percent = 0

        # Try uptime
        try:
            with open('/proc/uptime') as f:
                uptime_seconds = int(float(f.read().split()[0]))
        except:
            uptime_seconds = 0

        return {
            'success': True,
            'memory': {
                'total_mb': mem_total,
                'used_mb': mem_used,
                'percent': round(mem_percent, 1)
            },
            'uptime_seconds': uptime_seconds
        }
    except Exception as e:
        return {'error': str(e)}

def search_models(query='qwen'):
    """Search for AI models"""
    # This is a placeholder - could integrate with Hugging Face API
    models = [
        {
            'name': 'Qwen/Qwen2.5-7B-Instruct',
            'size': '7B',
            'type': 'Instruct',
            'description': 'Latest Qwen 2.5 instruction-tuned model',
            'url': 'https://huggingface.co/Qwen/Qwen2.5-7B-Instruct'
        },
        {
            'name': 'Qwen/Qwen2.5-14B-Instruct',
            'size': '14B',
            'type': 'Instruct',
            'description': 'Larger Qwen 2.5 instruction-tuned model',
            'url': 'https://huggingface.co/Qwen/Qwen2.5-14B-Instruct'
        },
        {
            'name': 'Qwen/Qwen2.5-32B-Instruct',
            'size': '32B',
            'type': 'Instruct',
            'description': 'Qwen 2.5 32B instruction model',
            'url': 'https://huggingface.co/Qwen/Qwen2.5-32B-Instruct'
        },
        {
            'name': 'meta-llama/Llama-3.1-8B-Instruct',
            'size': '8B',
            'type': 'Instruct',
            'description': 'Meta Llama 3.1 instruction-tuned',
            'url': 'https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct'
        },
        {
            'name': 'mistralai/Mistral-7B-Instruct-v0.3',
            'size': '7B',
            'type': 'Instruct',
            'description': 'Mistral instruction-tuned model',
            'url': 'https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3'
        }
    ]

    # Filter by query
    if query and query.lower() != 'all':
        models = [m for m in models if query.lower() in m['name'].lower()]

    return {
        'success': True,
        'query': query,
        'models': models
    }

if __name__ == '__main__':
    # Test the functions
    print("GPU Stats:")
    print(json.dumps(get_gpu_stats(), indent=2))
    print("\nSystem Stats:")
    print(json.dumps(get_system_stats(), indent=2))
    print("\nModel Search (qwen):")
    print(json.dumps(search_models('qwen'), indent=2))
