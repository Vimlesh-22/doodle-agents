"""Create a reviewed source-only inventory/archive; never include runtime data."""
from pathlib import Path
import hashlib,json,tarfile,re,base64
root=Path(__file__).resolve().parent.parent
lock=json.loads((root/'package-lock.json').read_text())
for name in ['jose','ipaddr.js']:
    dep=lock['packages']['node_modules/'+name]
    data=(root/'vendor'/f'{name}-{dep["version"]}.tgz').read_bytes()
    assert 'sha512-'+base64.b64encode(hashlib.sha512(data).digest()).decode()==dep['integrity'], 'Vendor integrity mismatch'
paths=[p for p in root.rglob('*') if p.is_file() and not any(x in p.relative_to(root).parts for x in ['node_modules','.git','artifacts'])]
for p in paths:
    assert not p.is_symlink(), f'Symlink forbidden: {p.name}'
    assert p.name not in ['.env','relay.secrets.json'] and not p.name.endswith(('.sqlite','.curl.conf')), f'Private file forbidden: {p.name}'
    raw=p.read_text() if p.suffix != ".tgz" else ""
    assert not re.search(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|sk-proj-[A-Za-z0-9_-]{20,})',raw), f'Potential credential in {p.name}'
manifest=[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(paths)]
out=root/'artifacts';out.mkdir(exist_ok=True)
(out/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
archive=out/'doodle-agents-source.tar.gz'
with tarfile.open(archive,'w:gz') as t:
    for p in sorted(paths):t.add(p,arcname='doodle-agents/'+str(p.relative_to(root)),recursive=False)
    t.add(out/'SOURCE_MANIFEST.json',arcname='doodle-agents/SOURCE_MANIFEST.json')
with tarfile.open(archive) as t:
    for m in t.getmembers():
        if m.isfile():
            with t.extractfile(m) as f:
                while f.read(1048576):pass
sha=hashlib.sha256(archive.read_bytes()).hexdigest()
(out/'SHA256SUMS').write_text(f'{sha}  {archive.name}\n')
print(json.dumps({'files':len(manifest),'archive_bytes':archive.stat().st_size,'sha256':sha,'integrity':'passed','secret_pattern_scan':'passed (not a guarantee; reviewed generated files only)'}))
