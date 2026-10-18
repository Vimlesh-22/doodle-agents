// Owner-controlled setup only; not invoked by build, install, or startup.
import {randomBytes} from 'node:crypto';
import {mkdirSync,writeFileSync,existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {createInterface} from 'node:readline/promises';
import {hash} from '../src/security.mjs';
const target=resolve(process.argv[2]??'.');
if(!process.stdin.isTTY||!process.stdout.isTTY)throw new Error('Run interactively');
if(!process.argv[2]?.startsWith('/')||existsSync(target)||target.startsWith(process.cwd()+'/'))throw new Error('Choose a new absolute private directory outside checkout');
const rl=createInterface({input:process.stdin,output:process.stdout});
const answer=await rl.question('Create persistent private intake and manual MCP credentials? Type CREATE PRIVATE RELAY CREDENTIALS: ');rl.close();
if(answer!=='CREATE PRIVATE RELAY CREDENTIALS')throw new Error('Canceled');
process.umask(0o077);mkdirSync(target,{mode:0o700});
const intake=randomBytes(32).toString('base64url'),mcp=randomBytes(32).toString('base64url');
const config={owner:'owner',enabled:true,encryptionKeyHex:randomBytes(32).toString('hex'),intakeTokenSha256:hash(intake),mcpTokenSha256:hash(mcp),callbackHosts:[]};
writeFileSync(target+'/relay.secrets.json',JSON.stringify(config,null,2),{mode:0o600,flag:'wx'});
for(const [name,value] of [['intake',intake],['mcp',mcp]])writeFileSync(`${target}/${name}.curl.conf`,`header = "Authorization: Bearer ${value}"\n`,{mode:0o600,flag:'wx'});
console.log('Private files created. Values were not printed. No provider/plugin connection established.');
