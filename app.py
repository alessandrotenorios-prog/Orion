import os
import threading
import time
from collections import defaultdict,deque
from contextlib import asynccontextmanager
from typing import Literal
from fastapi import FastAPI, HTTPException, Request, Depends, Header
import auth
from pydantic import BaseModel,Field,ConfigDict
from router import route
from research import research
from engine import Engine

engine=Engine()
@asynccontextmanager
async def lifespan(app):
    engine.start()
    yield
app=FastAPI(title="ORION",version="0.4.0",lifespan=lifespan)

class Message(BaseModel):
    role: Literal['user','assistant']
    content: str=Field(max_length=1200)
class Chat(BaseModel):
    model_config=ConfigDict(extra='forbid')
    question: str=Field(min_length=1,max_length=1000)
    web: bool=True
    history: list[Message]=Field(default_factory=list,max_length=2)

_gate=threading.BoundedSemaphore(2)
_rate=defaultdict(deque)
_rate_lock=threading.Lock()
def throttle(ip):
    now=time.monotonic()
    with _rate_lock:
        if len(_rate)>2000:
            for key in list(_rate):
                if not _rate[key] or now-_rate[key][-1]>60:del _rate[key]
            if len(_rate)>2000:raise HTTPException(429,"Servidor ocupado. Tente mais tarde.")
        events=_rate[ip]
        while events and now-events[0]>60:events.popleft()
        if len(events)>=8:raise HTTPException(429,"Limite temporário de pesquisas. Aguarde um minuto.")
        events.append(now)

@app.get('/health')
def health():
    return {"status":"ok","version":"0.4.0","model":engine.state,"ready":engine.state=="ready","research":True,"google_configured":bool(auth.client_id())}

class GoogleLogin(BaseModel):
    id_token: str=Field(min_length=1,max_length=10000)
    challenge_id: str=Field(min_length=1,max_length=200)

@app.post('/auth/challenge')
def auth_challenge(request:Request):
    throttle(request.client.host if request.client else 'unknown')
    return auth.challenge()

@app.post('/auth/google')
def auth_google(body:GoogleLogin,request:Request):
    throttle(request.client.host if request.client else 'unknown')
    return auth.login(body.id_token,body.challenge_id)

@app.post('/auth/logout')
def auth_logout(authorization:str|None=Header(default=None)):
    return auth.logout(authorization)

@app.post('/chat')
def chat(body:Chat,request:Request,user:dict=Depends(auth.require_user)):
    question=body.question.strip()
    if not question:raise HTTPException(422,"Escreva uma pergunta.")
    throttle('user:'+user['sub'])
    if not _gate.acquire(blocking=False):raise HTTPException(429,"ORION está ocupado. Tente novamente em instantes.")
    try:
        selected=route(question)
        findings=research(question) if body.web else {"sources":[],"notices":[]}
        sources=findings['sources']
        synthesized=False
        if body.web and not sources:
            answer="Não consegui ler fontes para confirmar esta pesquisa. Tente uma pergunta mais específica."
        elif engine.state=='ready':
            try:answer=engine.answer(question,selected,sources,body.history);synthesized=True
            except ValueError as exc:raise HTTPException(422,str(exc)) from exc
            except Exception:raise HTTPException(503,"O modelo não conseguiu concluir a resposta. Tente novamente.")
        elif sources:
            answer="Trechos encontrados — sem síntese da IA:\n\n"+'\n\n'.join(f"[{i+1}] {s['title']}\n{s['excerpt']}" for i,s in enumerate(sources))
            findings['notices'].append("O modelo ainda não está pronto; estes são trechos das fontes, não uma resposta gerada.")
        else:
            raise HTTPException(503,"O modelo está indisponível ou ainda iniciando. Ative a pesquisa ou tente mais tarde.")
        return {"assistant":selected.assistant,"routing_reason":selected.reason,"answer":answer,"sources":sources,"notices":findings['notices'],"synthesized":synthesized,"model_status":engine.state,"web_used":bool(sources)}
    finally:_gate.release()
