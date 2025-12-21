# Cluster Configuration

## Nodes

| Node | IP | RAM | Key Models |
|------|-----|-----|------------|
| Spark1 | 10.0.0.1 (local) | 119GB | qwq:32b, phi4:14b, deepseek-v3-cloud |
| Spark2 | 10.0.0.2 | 119GB | qwen3:32b, devstral:14b |
| box211 | 192.168.111.211 | 119GB | deepseek-r1:70b, devstral-small:24b |
| box212 | 192.168.111.212 | 119GB | mixtral:8x22b, deepseek-math:7b, codellama:70b |

## Total Compute
- 4 nodes × 119GB RAM = 476GB RAM
- Cloud APIs: deepseek-v3-cloud, mistral-large-cloud, gpt-oss-cloud, kimi-k2-cloud

## SSH Access
```bash
ssh spark2    # 10.0.0.2
ssh box211    # 192.168.111.211
ssh box212    # 192.168.111.212
```

## Current Tasks ($(date))
- Spark1: Cloud APIs (deepseek-v3, mistral-large)
- Spark2: qwen3:32b (bit analysis)
- box211: deepseek-r1:70b + devstral:24b
- box212: mixtral:8x22b + deepseek-math:7b + gpt-oss-cloud
