#!/usr/bin/env python3
"""Static check for portable Agent Skills bundle; does not connect to KHA."""
from pathlib import Path
import re,json,sys
try: import yaml
except ImportError: yaml=None
ROOT=Path(__file__).resolve().parent.parent
errors=[]
name=ROOT.name
text=(ROOT/'SKILL.md').read_text(encoding='utf-8')
match=re.match(r'\A---\n(.*?)\n---\n',text,re.S)
if not match:errors.append('Missing YAML frontmatter')
else:
    if yaml is not None:
        meta=yaml.safe_load(match.group(1))
    else:
        meta={k.strip():v.strip().strip('"') for k,v in re.findall(r'(?m)^([A-Za-z-]+):\s*(.+)$',match.group(1))}
    if meta.get('name')!=name:errors.append(f'name mismatch: expected {name}')
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',str(meta.get('name',''))):errors.append('Invalid portable skill name')
    if len(str(meta.get('name','')))>64:errors.append('Skill name too long')
    if not (1<=len(str(meta.get('description','')))<=1024):errors.append('Skill description must be 1-1024 chars')
    if len(str(meta.get('compatibility',''))) > 500:errors.append('Compatibility is too long')
    if 'allowed-tools' in meta:errors.append('Avoid host-specific allowed-tools in portable Skill')
for f in ROOT.rglob('*.md'):
    raw=f.read_text(encoding='utf-8')
    for target in re.findall(r'\]\(([^)]+\.md)\)',raw):
        if '://' in target or target.startswith('#'):continue
        if not (f.parent/target).is_file():errors.append(f'Broken link {f.relative_to(ROOT)} -> {target}')
for f in (ROOT/'examples').glob('*.json'):
    try:json.loads(f.read_text(encoding='utf-8'))
    except Exception as e:errors.append(f'Invalid example JSON {f.name}: {e}')
required=['README.md','references/host-compatibility.md','references/native-orchestration.md','references/host-orchestration.md','references/cli-cookbook.md','references/verification-and-recovery.md','scripts/install.py','adapters/AGENTS.snippet.md','adapters/CLAUDE.snippet.md','adapters/DSH.snippet.md']
for path in required:
    if not (ROOT/path).is_file():errors.append('Missing '+path)
if text.count('spawn_subagent')<1:errors.append('Missing native KHA orchestration guard')
if 'KHA-HOST' not in text:errors.append('Missing host-managed mode')
if 'KHA-NATIVE' not in text:errors.append('Missing native mode')
if 'Codex 永远' in text:errors.append('Host-specific hardcoded assumption')
print('Skill:',ROOT)
print('Files:',len([f for f in ROOT.rglob('*') if f.is_file()]))
if errors:
    for e in errors:print('ERROR:',e)
    sys.exit(1)
print('PASS: portable frontmatter, file links, examples, structure, and key invariants')
print('NOTE: not a runtime test of external KHA service or client discovery')

