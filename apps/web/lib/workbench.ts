export type Row = Record<string, unknown>;
export type Page = {items:Row[];total:number;offset:number;limit:number};
export const display=(value:unknown):string=>value===null||value===undefined?'Unavailable':typeof value==='object'?JSON.stringify(value):String(value);
export async function api<T>(path:string,token:string,body?:unknown):Promise<T> {
  const response=await fetch('/api/service/'+path,{method:body?'POST':'GET',headers:{'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{})},
    body:body?JSON.stringify(body):undefined,cache:'no-store',signal:AbortSignal.timeout(35000)});
  const value=await response.json();
  if(!response.ok) throw new Error(typeof value.detail==='string'?value.detail:JSON.stringify(value.detail??value));
  return value as T;
}
