import {adminAuthState} from './admin-auth.mjs';
import {env} from 'cloudflare:workers';
import manifest from '../work/user_study/site/trials.json';
import config from '../work/user_study/site/config.json';
import {validateResponse} from '../work/user_study/site/core.mjs';
export {manifest,config,validateResponse};
export function db(){if(!env.DB)throw Error('Response database unavailable');return env.DB;}
export function isOwner(request:Request){return adminAuthState({userId:request.headers.get('oai-authenticated-user-id'),email:request.headers.get('oai-authenticated-user-email')},env.ADMIN_EMAIL).kind==='owner';}
export function cors(request:Request):{allowed:boolean;headers:Record<string,string>}{const origin=request.headers.get('Origin'),own=new URL(request.url).origin;const allowed=!origin||origin===own||origin==='https://ming053l.github.io';return {allowed,headers:origin&&allowed?{'Access-Control-Allow-Origin':origin,'Access-Control-Allow-Credentials':'true','Vary':'Origin'}:{}};}
export function json(data:unknown,status=200,headers:HeadersInit={}){return Response.json(data,{status,headers:{'Cache-Control':'no-store',...headers}});}
