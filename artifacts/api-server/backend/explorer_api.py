import asyncio,json,sys
from functools import lru_cache
from pathlib import Path
from fastapi import APIRouter,HTTPException,Request,Query
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,StrictBool,model_validator
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from semantic_matching import AnalysisError, SemanticMatcher
from semantic_catalogue import MODEL, DIMENSIONS
from career_courses import for_job
from job_localization import public_job
from keyword_matching import enrich
router=APIRouter();SLOTS=asyncio.Semaphore(2);RECEIVE_SLOTS=asyncio.Semaphore(2);LIMIT=8*1024*1024


@lru_cache(maxsize=1)
def service():
    try:
        return SemanticMatcher()
    except (OSError,ValueError,KeyError):
        raise HTTPException(503,detail={'code':'catalogue_invalid','message':'职业目录缺失或格式不正确；请检查 catalogue/job_list.csv。'}) from None


class ExploreBody(BaseModel):
    model_config=ConfigDict(extra='forbid')
    text:str=Field(min_length=20,max_length=100000)
    is_synthetic:StrictBool=False
    processing_consent:StrictBool=False
    keyword_language:Literal['en','zh']='en'
    top_k:int=Field(default=65,ge=1,le=65,strict=True)
    @model_validator(mode='after')
    def must_confirm(self):
        if not self.is_synthetic and not self.processing_consent:
            raise ValueError('Confirm authorization and server-side processing before analyzing a resume.')
        return self


@router.get('/api/explorer/status')
def status():
    try:
        return service().status()
    except HTTPException:
        return {
            'mode':'local_text_embedding','model':MODEL,'dimensions':DIMENSIONS,
            'occupation_count':0,'catalogue_hash':'','model_ready':False,
            'cache_ready':False,'state':'catalogue_invalid',
            'message':'职业目录缺失或格式不正确，请恢复 catalogue/job_list.csv。',
            'score_semantics':'余弦相似度，不是录用概率。',
            'privacy':'需确认资料处理授权；分词与向量推理在本应用后端完成，不调用外部分析 API，不持久保存原文件或简历文本。',
            'catalogue_basis':'用户提供的职业描述 CSV。',
        }


@router.get('/api/explorer/jobs')
def jobs():
    matcher=service()
    return {'jobs':[public_job(job) for job in matcher.jobs],'catalogue_hash':matcher.configuration['catalogue_hash'],
            'source':'用户提供的 job_list.csv：65 个职业描述，不是实时职位或经过验证的能力标准。'}


@router.get('/api/explorer/skills')
def skills():
    return {'version':'local-semantic-384-v1','skills':[],
            'message':'新分析不使用旧 80 技能字典；向量维度没有单项技能标签。'}


@router.get('/api/explorer/jobs/{job_id}/courses')
def job_courses(job_id:str,language:Literal['en','zh']=Query(default='en')):
    job=next((j for j in service().jobs if j['job_id']==job_id),None)
    if job is None:
        raise HTTPException(404,detail={'code':'unknown_job','message':'职业不存在，请从当前职业目录选择。'})
    try:
        return for_job(job,language)
    except (OSError,ValueError,KeyError):
        raise HTTPException(503,detail={'code':'courses_unavailable','message':'课程目录暂不可用，请稍后重试；职业排名不受影响。'}) from None


@router.post('/api/explorer/match')
async def explore(body:ExploreBody):
    try:
        result=await service().match(body.text,body.top_k)
        return enrich(result,body.text,body.keyword_language)
    except AnalysisError as exc:
        raise HTTPException(exc.http_status,detail={'code':exc.code,'message':exc.message}) from None


@router.get('/api/healthz')
def healthz():
    return {'status':'ok'}


@router.get('/api/health/ready')
def ready():
    inspection=status()
    if inspection['state'] not in ('ready','awaiting_index'):
        raise HTTPException(503,detail={'code':inspection['state'],'message':inspection['message']})
    return {'status':'configured','embedding':inspection}
@router.post('/api/explorer/upload')
async def upload(request:Request):
    try:
        await asyncio.wait_for(RECEIVE_SLOTS.acquire(),timeout=0.05)
    except TimeoutError:
        raise HTTPException(429,'已有文件正在处理，请稍后重试。') from None
    try:
        return await extract_upload(request)
    finally:
        RECEIVE_SLOTS.release()


async def extract_upload(request:Request):
    synthetic=request.headers.get('x-synthetic-profile')=='true'
    if not synthetic and request.headers.get('x-processing-consent')!='true':
        raise HTTPException(422,'请先确认你有权处理此简历，并同意本应用后端进行临时解析和分析。')
    kind=request.headers.get('x-document-format','').lower()
    mime=request.headers.get('content-type','').split(';')[0]
    expected={'pdf':'application/pdf','docx':'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}
    if kind not in expected or mime!=expected[kind]:raise HTTPException(415,'只支持可复制文字的 PDF 和 DOCX。')
    raw=bytearray()
    async for chunk in request.stream():
        if len(raw)+len(chunk)>LIMIT:raise HTTPException(413,'文件不能超过 8MB。')
        raw.extend(chunk)
    if not raw:raise HTTPException(422,'文件为空。')
    async with SLOTS:
        bootstrap='import sys,runpy;sys.path[:0]='+repr(sys.path)+';sys.argv=["resume_documents",'+repr(kind)+'];runpy.run_module("resume_documents",run_name="__main__")'
        proc=await asyncio.create_subprocess_exec(sys.executable,'-B','-c',bootstrap,stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.DEVNULL)
        try:stdout,_=await asyncio.wait_for(proc.communicate(bytes(raw)),timeout=15)
        except (asyncio.TimeoutError,asyncio.CancelledError) as exc:
            if proc.returncode is None:proc.kill()
            await proc.communicate()
            if isinstance(exc,asyncio.CancelledError):raise
            raise HTTPException(422,'文件解析超时，请使用更简单的文字文档。')
        finally:raw.clear()
    try:document=json.loads(stdout)
    except (UnicodeError,ValueError):raise HTTPException(422,'文档解析失败。')
    if 'error' in document:raise HTTPException(422,detail={'code':document['error'],'message':document['message']})
    # Extraction and the separately initiated semantic analysis are both local.
    return {'document':document,'is_synthetic':synthetic,
            'privacy':'解析与向量分析均在本应用后端完成，不调用外部分析 API；原文件不保存。'}
@router.get('/api/explorer/demos')
def demos():
    return {'profiles':[
      {'profile_id':'SYN-A','name':'传统数据分析师','synthetic':True,'text':'Synthetic resume\nName: Synthetic Applicant A\nSchool: Fictional Institute A\nI read structured files from CSV and extracted the requested fields for a synthetic report. I convert data types and validate dates in a synthetic sales dataset. I create data visualizations to explain differences in the sample. I have not deployed a model to production.'},
      {'profile_id':'SYN-B','name':'HR / 行政转型','synthetic':True,'text':'Synthetic resume\nName: Synthetic Applicant B\nGender: Synthetic female\nI organized fictional staff training and checked the outputs of an automated administrative workflow. I record human review decisions for synthetic hiring examples. I do not claim machine learning engineering experience.'},
      {'profile_id':'SYN-C','name':'IT 应届毕业生','synthetic':True,'text':'Synthetic resume\nName: Synthetic Applicant C\nGPA: 4.0\nI trained a classifier on a synthetic dataset and compared its outputs with a held-out reference. I evaluate model outputs and record test errors in my fictional coursework. 我从 JSON 中读取指定字段，并检查缺失值。'},
      {'profile_id':'SYN-D','name':'IT 运维人员','synthetic':True,'text':'Synthetic resume\nName: Synthetic Applicant D\nI monitored a fictional service and recorded recovery steps when the test system failed. I reviewed access permissions for synthetic records and documented the results. I am learning retrieval methods but have not completed a retrieval project.'},
      {'profile_id':'SYN-E','name':'职业辅导 / 培训规划','synthetic':True,'text':'Synthetic resume\nName: Synthetic Applicant E\nI compared fictional learning resources and documented prerequisites for a synthetic career plan. I verify source citations and report evidence gaps for each claim. I do not infer that a missing skill statement means a person lacks the skill.'}
    ]}
