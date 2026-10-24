import asyncio
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
from typing import Literal
from uuid import uuid4
from fastapi import FastAPI,HTTPException,Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,ConfigDict,Field,model_validator
from .engine import CATALOG,CATALOG_HASH,DEMOS,IDS,ROOT,candidates,normalize

app=FastAPI(title='Skills Profile Intake',version='1.0.0',docs_url='/api/docs')
LIMIT=8*1024*1024
PARSE_SLOTS=asyncio.Semaphore(2)

@app.middleware('http')
async def headers(request,call_next):
    response=await call_next(request)
    response.headers.update({'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','X-Frame-Options':'DENY','Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'"})
    return response

@app.get('/api/health')
def health():return {'status':'ok','module':'skills-intake','dictionary_version':CATALOG['version']}

@app.get('/api/skills')
def skills():return {**CATALOG,'dictionary_hash':CATALOG_HASH}

@app.get('/api/demo-profiles')
def demos():return {'profiles':DEMOS,'notice':'全部为合成档案，不代表真实个人能力。'}

@app.post('/api/profile/parse')
async def parse(request:Request):
    if request.headers.get('x-synthetic-profile')!='true':
        raise HTTPException(422,detail={'code':'synthetic_only','message':'Competition mode accepts synthetic PDFs only. Confirm synthetic provenance.'})
    if request.headers.get('content-type','').split(';')[0]!='application/pdf':
        raise HTTPException(415,detail={'code':'unsupported_type','message':'请上传PDF文件。'})
    raw=bytearray()
    async for chunk in request.stream():
        raw.extend(chunk)
        if len(raw)>LIMIT:raise HTTPException(413,detail={'code':'file_too_large','message':'PDF不能超过8MB。'})
    if not raw:raise HTTPException(422,detail={'code':'empty_file','message':'文件为空。'})
    async with PARSE_SLOTS:
        # -c bootstraps project-local dependencies for the worker subprocess too.
        bootstrap='import sys,runpy;sys.path[:0]='+repr(sys.path)+';runpy.run_path('+repr(str(Path(__file__).with_name('pdf_worker.py')))+',run_name="__main__")'
        proc=await asyncio.create_subprocess_exec(sys.executable,'-c',bootstrap,stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.DEVNULL)
        try:
            stdout,_=await asyncio.wait_for(proc.communicate(bytes(raw)),timeout=15)
        except (asyncio.TimeoutError,asyncio.CancelledError) as exc:
            if proc.returncode is None:proc.kill()
            await proc.communicate()
            if isinstance(exc,asyncio.CancelledError):raise
            raise HTTPException(422,detail={'code':'parse_timeout','message':'解析超时，请使用简化PDF或手动表单。'})
        try: result=json.loads(stdout)
        except (ValueError,UnicodeError):raise HTTPException(422,detail={'code':'parse_failed','message':'PDF解析失败，请使用表单。'})
    if 'error' in result:raise HTTPException(422,detail={'code':result['error'],'message':result['message']})
    hits=candidates(result['pages'])
    return {'status':'needs_review','dictionary_version':CATALOG['version'],'dictionary_hash':CATALOG_HASH,
        'page_count':result['page_count'],'characters':result['characters'],'candidates':hits,
        'message':'候选来自词典匹配，可能遗漏或误识别；全部等级保持未知，请审核20项技能后提交。',
        'warnings':['仅支持中英文词典候选识别；否定和学习意向判断是启发式。','简历未写出的技能不能视为不会。','PDF仅在本地服务内存中处理；应用不保存原文件或全文。']}

class Evidence(BaseModel):
    model_config=ConfigDict(extra='forbid')
    page:int=Field(ge=1,le=20)
    start:int=Field(ge=0)
    end:int=Field(ge=0)
    matched_text:str=Field(max_length=200)
    alias:str=Field(max_length=200)
    snippet:str=Field(max_length=500)
    mention_type:Literal['mention','learning','negated']

class SkillInput(BaseModel):
    model_config=ConfigDict(extra='forbid')
    skill_id:str
    level:int|None=Field(default=None,ge=0,le=3,strict=True)
    source:Literal['unknown','self_report','cv_keyword','demo']='unknown'
    confirmed:bool=False
    evidence:list[Evidence]=Field(default_factory=list,max_length=5)
    @model_validator(mode='after')
    def valid(self):
        if self.skill_id not in IDS:raise ValueError('Unknown skill_id')
        if self.level is not None and not self.confirmed:raise ValueError('Known levels must be confirmed by user')
        if self.level is None and self.confirmed:raise ValueError('Unknown skill cannot be confirmed')
        if self.level is not None and self.source=='unknown':raise ValueError('Known level requires source')
        return self

class ProfileInput(BaseModel):
    model_config=ConfigDict(extra='forbid')
    schema_version:Literal['1.0']='1.0'
    skill_dictionary_version:str
    dictionary_hash:str
    display_name:str=Field(default='我的技能档案',min_length=1,max_length=80)
    is_synthetic:Literal[True]
    skills:list[SkillInput]=Field(max_length=20)
    @model_validator(mode='after')
    def valid(self):
        if len({s.skill_id for s in self.skills})!=len(self.skills):raise ValueError('Duplicate skill_id')
        if any(s.source=='demo' for s in self.skills) and not self.is_synthetic:raise ValueError('Demo skill sources require synthetic profile')
        return self

@app.post('/api/profile')
def profile(body:ProfileInput):
    if body.skill_dictionary_version!=CATALOG['version'] or body.dictionary_hash!=CATALOG_HASH:
        raise HTTPException(409,detail={'code':'dictionary_changed','message':'技能字典已更新，请刷新并重新确认。'})
    data=normalize([s.model_dump() for s in body.skills])
    known=sum(data['vectors']['known_mask'])
    return {'schema_version':'1.0','profile_id':str(uuid4()),'skill_dictionary_version':CATALOG['version'],'dictionary_hash':CATALOG_HASH,
        'created_at':datetime.now(timezone.utc).isoformat(),'display_name':body.display_name,'is_synthetic':body.is_synthetic,
        'assessment_status':'self_confirmed_not_independently_assessed','storage':'not_persisted',
        'summary':{'known':known,'unknown':20-known,'present':sum(v is not None and v>0 for v in data['vectors']['levels'])},**data}

