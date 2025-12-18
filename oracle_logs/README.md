# Oracle Logs Directory

This directory stores outputs from long-running Oracle mode sessions.

## File Naming Convention
- `{agent}_{task}_{timestamp}.log` - Raw output
- `{agent}_{task}_{timestamp}.json` - Structured result

## Archival
Old logs are compressed and moved to `../oracle_archives/` using:
```bash
gzip -c logfile.log > ../oracle_archives/logfile.log.gz
```

## Current Sessions
Check running sessions with:
```bash
ps aux | grep ollama
```
