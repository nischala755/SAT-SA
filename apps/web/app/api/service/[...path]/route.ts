import { NextRequest, NextResponse } from 'next/server';
import { backendBaseUrl } from '../../../../lib/backend-url';

async function proxy(request: NextRequest, context: {params: Promise<{path:string[]}>}) {
  const {path}=await context.params;
  if (!path.length || path.some(p=>! /^[A-Za-z0-9_.:-]+$/.test(p) || p==='..')) return NextResponse.json({detail:'Invalid path'},{status:400});
  const base=backendBaseUrl(process.env);
  try {
    const body=request.method==='POST'?await request.text():undefined;
    if (body && new TextEncoder().encode(body).length>24000000) return NextResponse.json({detail:'Request exceeds 24 MB'},{status:413});
    const response=await fetch(`${base}/api/v1/${path.join('/')}${request.nextUrl.search}`,{
      method:request.method,body,headers:{'Content-Type':'application/json',Authorization:request.headers.get('authorization')??''},
      cache:'no-store',redirect:'error',signal:AbortSignal.timeout(30000)
    });
    return new NextResponse(await response.text(),{status:response.status,headers:{'Content-Type':'application/json','Cache-Control':'no-store'}});
  } catch { return NextResponse.json({detail:'Backend unavailable. Check the local API service and retry.'},{status:503}); }
}
export const GET=proxy;
export const POST=proxy;
