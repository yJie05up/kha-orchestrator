#!/usr/bin/env python3
"""Install one portable Agent Skill for multiple hosts (offline copy only)."""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
from datetime import datetime

NAME='kha-orchestrator'
ROOT=Path(__file__).resolve().parent.parent
HOSTS={'codex','claude','dsh','dsh-native'}
EXCLUDED={'__pycache__','.DS_Store'}

def install_root(host,scope,project):
    home=Path.home()
    base=home if scope=='user' else project
    if host in {'codex','dsh'}: return base/'.agents'/'skills'
    if host=='claude':return base/'.claude'/'skills'
    if host=='dsh-native':return base/'.dsh'/'skills'
    raise ValueError(host)

def main():
    p=argparse.ArgumentParser(description='Install kha-orchestrator into selected host skill roots, without network calls.')
    p.add_argument('--hosts', default='all', help='all, codex, dsh, dsh-native, claude, or comma-separated')
    p.add_argument('--scope', choices=['user','project'], default='user')
    p.add_argument('--project-root', default='.', help='Project directory when --scope project')
    p.add_argument('--dry-run',action='store_true')
    p.add_argument('--force',action='store_true',help='Backup any existing installation before replacement')
    args=p.parse_args()
    selected={'codex','dsh','claude'} if args.hosts.strip()=='all' else set(x.strip() for x in args.hosts.split(',') if x.strip())
    if not selected or selected-HOSTS:p.error('Unknown hosts: '+', '.join(sorted(selected-HOSTS)))
    project=Path(args.project_root).expanduser().resolve()
    if args.scope=='project' and not project.is_dir():p.error('Project root does not exist')
    roots=sorted(set(install_root(h,args.scope,project) for h in selected),key=str)
    if not args.force:
        collisions=[str(r/NAME) for r in roots if (r/NAME).exists()]
        if collisions and not args.dry_run:p.error('Already installed (use --force with backup): '+', '.join(collisions))
    for r in roots:
        dest=r/NAME
        print(('WOULD INSTALL' if args.dry_run else 'INSTALL')+': '+str(dest))
        if args.dry_run:continue
        r.mkdir(parents=True,exist_ok=True)
        if dest.exists():
            timestamp=datetime.now().strftime('%Y%m%d-%H%M%S')
            backup=r/f'{NAME}.bak-{timestamp}'
            i=1
            while backup.exists():
                backup=r/f'{NAME}.bak-{timestamp}-{i}';i+=1
            shutil.move(str(dest),str(backup));print('BACKUP: '+str(backup))
        shutil.copytree(ROOT,dest,ignore=shutil.ignore_patterns(*EXCLUDED))
    print('Hosts:',', '.join(sorted(selected)))
    print('No CLI installation, login, network, or host settings modification performed.')

if __name__=='__main__':main()

