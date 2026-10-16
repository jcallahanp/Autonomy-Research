---
# The container file starts with a flowchart header and stays at or under about 30 lines.
type: regex
target: { source: file, path: docs/diagrams/ledgerly-containers.mmd }
pattern: '^(?=flowchart (?:LR|TB|TD|RL|BT)\b)(?![\s\S]*C4(?:Context|Container))(?:[^\n]*\n){0,30}[^\n]*$'
---
