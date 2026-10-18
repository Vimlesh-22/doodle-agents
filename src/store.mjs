import {Fault} from './security.mjs';
import {DatabaseSync} from 'node:sqlite';
import {mkdirSync,chmodSync,lstatSync} from 'node:fs';
import {dirname} from 'node:path';
export class Store {
 constructor(path){if(path!==':memory:'){mkdirSync(dirname(path),{recursive:true,mode:0o700});if(lstatSync(dirname(path)).isSymbolicLink())throw new Error('Symlink data directory');chmodSync(dirname(path),0o700);try{if(lstatSync(path).isSymbolicLink())throw new Error('Symlink database');}catch(e){if(e.code!=='ENOENT')throw e;}}
 this.db=new DatabaseSync(path);this.db.exec('PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA busy_timeout=5000; CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY CHECK(id=1), body TEXT NOT NULL)');this.db.prepare('INSERT OR IGNORE INTO state VALUES (1,?)').run(JSON.stringify({tasks:{},subscriptions:{},outbox:{}}));if(path!==':memory:')chmodSync(path,0o600);}
 read(){return JSON.parse(this.db.prepare('SELECT body FROM state WHERE id=1').get().body);}
 write(fn){this.db.exec('BEGIN IMMEDIATE');try{const state=this.read(),result=fn(state);const encoded=JSON.stringify(state);if(Buffer.byteLength(encoded)>16*1024*1024)throw new Fault(503,'Storage capacity reached');this.db.prepare('UPDATE state SET body=? WHERE id=1').run(encoded);this.db.exec('COMMIT');return result;}catch(e){this.db.exec('ROLLBACK');throw e;}}
 close(){this.db.close();}
}
