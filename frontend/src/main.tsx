import React,{useState} from 'react';
import{createRoot}from'react-dom/client';
import{Activity,BookOpen,CheckCircle2,Copy,KeyRound,LockKeyhole,RefreshCw,ScrollText,ShieldCheck,Terminal,UserPlus}from'lucide-react';
import'./styles.css';

type Result={ok:boolean;status:number;body:unknown;duration:number};
const api=async(path:string,init:RequestInit={}):Promise<Result>=>{const start=performance.now();try{const response=await fetch(`/api${path}`,{...init,headers:{'Content-Type':'application/json',...(init.headers||{})}});const text=await response.text();return{ok:response.ok,status:response.status,body:text?JSON.parse(text):null,duration:Math.round(performance.now()-start)}}catch(error){return{ok:false,status:0,body:{error:String(error)},duration:Math.round(performance.now()-start)}}};

const features=[['JWT','Short-lived signed access tokens'],['Refresh rotation','One-time refresh tokens'],['OAuth2 ready','Bearer flow and OpenAPI'],['RBAC','User, auditor and admin policy'],['API keys','Hashed machine credentials'],['Rate limits','Redis distributed counters'],['Validation','Strict Pydantic schemas'],['Argon2','Modern password hashing'],['Revocation','Server-side token invalidation'],['Audit logs','Security event trail']];

function App(){
 const[email,setEmail]=useState('demo@example.com'),[password,setPassword]=useState('Portfolio123'),[access,setAccess]=useState(''),[refresh,setRefresh]=useState(''),[key,setKey]=useState(''),[result,setResult]=useState<Result|null>(null),[busy,setBusy]=useState('');
 const run=async(name:string,fn:()=>Promise<Result>)=>{setBusy(name);const value=await fn();setResult(value);setBusy('');return value};
 const register=()=>run('register',()=>api('/auth/register',{method:'POST',body:JSON.stringify({email,password})}));
 const login=()=>run('login',async()=>{const r=await api('/auth/login',{method:'POST',body:JSON.stringify({email,password})});if(r.ok){const b=r.body as any;setAccess(b.access_token);setRefresh(b.refresh_token)}return r});
 const profile=()=>run('profile',()=>api('/me',{headers:{Authorization:`Bearer ${access}`}}));
 const rotate=()=>run('refresh',async()=>{const r=await api('/auth/refresh',{method:'POST',body:JSON.stringify({refresh_token:refresh})});if(r.ok){const b=r.body as any;setAccess(b.access_token);setRefresh(b.refresh_token)}return r});
 const revoke=()=>run('revoke',()=>api('/auth/revoke',{method:'POST',body:JSON.stringify({refresh_token:refresh})}));
 const makeKey=()=>run('key',async()=>{const r=await api('/api-keys',{method:'POST',headers:{Authorization:`Bearer ${access}`},body:JSON.stringify({name:'Portfolio demo'})});if(r.ok)setKey((r.body as any).key);return r});
 const service=()=>run('service',()=>api('/service/data',{headers:{'X-API-Key':key}}));
 const audits=()=>run('audit',()=>api('/audit',{headers:{Authorization:`Bearer ${access}`}}));
 return <>
  <header><div className="nav"><div className="brand"><ShieldCheck/><span>SENTINEL</span><small>GATEWAY</small></div><nav><a href="#lab">Security Lab</a><a href="/api/docs" target="_blank">API Docs</a><a href="https://github.com/mikaelllll/API-Gateway-and-Authentication-Service-example" target="_blank">GitHub</a></nav><span className="live"><i/>SYSTEM ONLINE</span></div></header>
  <main>
   <section className="hero"><div><div className="eyebrow"><LockKeyhole size={14}/> ZERO-TRUST IDENTITY LAYER</div><h1>Every request.<br/><em>Verified.</em></h1><p>A production-style API gateway demonstrating modern authentication, authorization and security observability—built as an interactive engineering portfolio.</p><div className="heroActions"><a className="primary" href="#lab"><Terminal/>Launch security lab</a><a className="secondary" href="/api/docs"><BookOpen/>Explore OpenAPI</a></div></div><div className="terminal"><div className="termTop"><span/><span/><span/><b>gateway.request.log</b></div><pre><code><s>$</s> curl /api/me \
  -H <q>"Authorization: Bearer eyJ..."</q>

<m>HTTP/2 200 OK</m>
<d>x-gateway:</d> Sentinel
<d>x-content-type-options:</d> nosniff

{'{'}
  <q>"identity"</q>: <q>"verified"</q>,
  <q>"policy"</q>: <m>"allow"</m>,
  <q>"latency_ms"</q>: 18
{'}'}</code></pre><div className="scan"><span/></div></div></section>
   <section className="strip"><div><Activity/>ASYNC PYTHON</div><div>FASTAPI</div><div>POSTGRESQL</div><div>REDIS</div><div>REACT + TYPESCRIPT</div><div>DOCKER</div></section>
   <section className="features"><div className="sectionTitle"><span>DEFENSE IN DEPTH</span><h2>A complete identity perimeter</h2><p>Each layer addresses a distinct threat, from credential theft to abusive traffic.</p></div><div className="featureGrid">{features.map(([title,desc],i)=><article key={title}><b>{String(i+1).padStart(2,'0')}</b><CheckCircle2/><h3>{title}</h3><p>{desc}</p></article>)}</div></section>
   <section id="lab" className="lab"><div className="sectionTitle"><span>INTERACTIVE SECURITY LAB</span><h2>Test the gateway yourself</h2><p>Run the real authentication lifecycle. Every action calls the live backend and shows its response.</p></div><div className="labGrid"><div className="controls"><div className="fields"><label>Email<input value={email} onChange={e=>setEmail(e.target.value)}/></label><label>Password<input type="password" value={password} onChange={e=>setPassword(e.target.value)}/></label></div><h3>01 · Establish identity</h3><div className="buttons"><button onClick={register} disabled={!!busy}><UserPlus/>Register</button><button onClick={login} disabled={!!busy}><KeyRound/>Sign in</button><button onClick={profile} disabled={!access||!!busy}><ShieldCheck/>Verify JWT</button></div><h3>02 · Manage credentials</h3><div className="buttons"><button onClick={rotate} disabled={!refresh||!!busy}><RefreshCw/>Rotate token</button><button onClick={revoke} disabled={!refresh||!!busy}><LockKeyhole/>Revoke token</button><button onClick={makeKey} disabled={!access||!!busy}><KeyRound/>Create API key</button></div><h3>03 · Access protected resources</h3><div className="buttons"><button onClick={service} disabled={!key||!!busy}><Terminal/>Call service</button><button onClick={audits} disabled={!access||!!busy}><ScrollText/>View audit trail</button></div><div className="credential"><span>JWT</span><code>{access?access.slice(0,44)+'…':'Sign in to issue a token'}</code><Copy size={15}/></div></div><div className="response"><div><span/><b>LIVE RESPONSE</b>{busy&&<i>REQUESTING…</i>}</div>{result?<><div className="metrics"><span className={result.ok?'success':'failure'}>{result.status} {result.ok?'SUCCESS':'ERROR'}</span><span>{result.duration} ms</span></div><pre>{JSON.stringify(result.body,null,2)}</pre></>:<div className="empty"><Terminal/><p>Run an action to inspect the gateway response.</p></div>}</div></div></section>
  </main><footer><div className="brand"><ShieldCheck/><span>SENTINEL</span></div><p>Built to demonstrate production-minded backend engineering.</p><a href="/api/docs">OpenAPI specification →</a></footer>
 </>}
createRoot(document.getElementById('root')!).render(<App/>);

