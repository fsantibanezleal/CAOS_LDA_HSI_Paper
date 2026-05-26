"""Throwaway reconciler for the manifest vs filesystem audit (2026-05-24)."""
import json, os, sys

BASE = 'd:/_Repos/_Web_Projects/CAOS_LDA_HSI'

m = json.load(open(os.path.join(BASE, 'data/derived/manifests/index.json'), encoding='utf-8'))
manifest_paths = set(a['path'] for a in m['artifacts'])
print('Total manifest entries:', len(manifest_paths))

fs_paths = set()
for root, dirs, files in os.walk(os.path.join(BASE, 'data/derived')):
    for f in files:
        full = os.path.join(root, f).replace('\\', '/')
        rel = full.replace(BASE.replace('\\', '/') + '/', '')
        fs_paths.add(rel)
print('Total filesystem files:', len(fs_paths))

only_in_fs = fs_paths - manifest_paths
only_in_manifest = manifest_paths - fs_paths
print()
print('Files on FS not in manifest:', len(only_in_fs))
for p in sorted(only_in_fs):
    print('  +', p)
print()
print('Manifest entries with no file on disk:', len(only_in_manifest))
for p in sorted(only_in_manifest)[:50]:
    print('  -', p)
