"""Local-only smoke test using public fixtures. Creates/removes its own Docker volume."""
import tempfile,subprocess,json,hashlib,uuid,time,os
from pathlib import Path
name='doodle-rebuild-test-'+uuid.uuid4().hex[:12]
volume=name+'-data'
def run(*args):return subprocess.check_output(['docker',*args],text=True).strip()
def fetch(path,post=False):
 script="const r=await fetch('http://127.0.0.1:8080"+path+"',"+json.dumps({'method':'POST','headers':{'Authorization':'Bearer test-intake','Content-Type':'application/json','Idempotency-Key':'smoke'},'body':json.dumps({'title':'Smoke','instructions':'No external actions'})} if post else {})+");console.log(r.status)"
 return run('exec',name,'node','--input-type=module','-e',script)
with tempfile.TemporaryDirectory(prefix='doodle-smoke-') as directory:
 config=Path(directory)/'fixture.json'
 config.write_text(json.dumps({'owner':'owner','enabled':True,'encryptionKeyHex':'ab'*32,'intakeTokenSha256':hashlib.sha256(b'test-intake').hexdigest(),'mcpTokenSha256':hashlib.sha256(b'test-mcp').hexdigest(),'callbackHosts':[]}));config.chmod(0o600)
 # Match sudo setup: the mounted 0600 configuration is root-owned.
 run('run','--rm','--network','none','--user','0:0','--cap-drop','ALL','--cap-add','CHOWN','--mount',f'type=bind,src={config},dst=/fixture','--entrypoint','chown','doodle-agents:rebuild-test','0:0','/fixture')
 run('volume','create',volume)
 try:
  for expected in ['202','200']:
   run('run','-d','--name',name,'--network','none','--read-only','--user','0:0','--cap-drop','ALL','--cap-add','CHOWN','--cap-add','FOWNER','--cap-add','SETUID','--cap-add','SETGID','--security-opt','no-new-privileges','--mount',f'type=volume,src={volume},dst=/data','--mount',f'type=bind,src={config},dst=/run/config.json,readonly','-e','RELAY_CONFIG=/run/config.json','doodle-agents:rebuild-test')
   for attempt in range(30):
    if run('inspect','--format','{{.State.Running}}',name)=='false':
     print(run('logs',name));raise RuntimeError('Container exited')
    try:
     if fetch('/healthz')=='200':break
    except subprocess.CalledProcessError:pass
    time.sleep(.1)
   assert fetch('/healthz')=='200'
   assert fetch('/v1/tasks/unknown')=='401'
   assert fetch('/v1/tasks',True)==expected
   status=run('exec',name,'cat','/proc/1/status')
   assert 'Uid:\t1000\t1000\t1000\t1000' in status
   print('PASS health=200 unauthorized=401 intake='+expected+' runtime_uid=1000')
   run('rm','-f',name)
 finally:
  subprocess.run(['docker','rm','-f',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  run('volume','rm',volume)
print('PASS persistence across container replacement; test resources removed')
