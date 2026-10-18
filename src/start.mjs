import {readFileSync,lstatSync,mkdirSync,chownSync,chmodSync} from 'node:fs';
import {dirname,resolve} from 'node:path';
import {createRelay} from './app.mjs';
process.umask(0o077);
const file=process.env.RELAY_CONFIG;
if(!file)throw new Error('RELAY_CONFIG must point to a private configuration file');
const stat=lstatSync(file);
if(!stat.isFile()||stat.isSymbolicLink()||(stat.mode&0o077))throw new Error('Configuration must be a regular mode-0600 file');
const config=JSON.parse(readFileSync(file,'utf8'));
const dbPath=resolve(process.env.RELAY_DB??'./data/relay.sqlite');
if(process.getuid?.()===0){if(dbPath!=='/data/relay/relay.sqlite')throw new Error('Root initializer restricted to /data/relay/relay.sqlite');mkdirSync('/data/relay',{recursive:true,mode:0o700});if(lstatSync('/data/relay').isSymbolicLink())throw new Error('Symlink data directory');chownSync('/data/relay',1000,1000);chmodSync('/data/relay',0o700);process.setgroups([]);process.setgid(1000);process.setuid(1000);}
const relay=createRelay(config,{dbPath});
const timer=setInterval(()=>relay.drain().catch(()=>console.error('Delivery cycle failed')),1000);
relay.server.listen(Number(process.env.PORT??8080),process.env.HOST??'127.0.0.1',()=>console.log('Doodle relay listening'));
let stopping=false;async function stop(){if(stopping)return;stopping=true;clearInterval(timer);relay.server.close(()=>{relay.close();process.exit(0);});setTimeout(()=>process.exit(1),15000).unref();}
process.on('SIGTERM',stop);process.on('SIGINT',stop);
