"""Google ID-token verification and short-lived, in-memory ORION sessions."""
import hashlib
import os
import secrets
import threading
import time
from fastapi import Header,HTTPException

_lock=threading.Lock()
_challenges={}
_sessions={}
def client_id():return os.getenv('GOOGLE_WEB_CLIENT_ID','').strip()
def _purge():
 now=time.time()
 for bucket in (_challenges,_sessions):
  for key in list(bucket):
   if bucket[key]['expires']<=now:del bucket[key]

def challenge():
 if not client_id():raise HTTPException(503,'Login Google ainda não configurado pelo responsável pelo servidor.')
 with _lock:
  _purge()
  if len(_challenges)>=200:raise HTTPException(429,'Muitas tentativas de login. Aguarde.')
  identifier=secrets.token_urlsafe(24);nonce=secrets.token_urlsafe(32)
  _challenges[identifier]={'nonce':nonce,'expires':time.time()+300}
 return {'challenge_id':identifier,'nonce':nonce,'client_id':client_id()}

def verify_google(token,audience):
 from google.oauth2 import id_token
 from google.auth.transport.requests import Request
 import requests
 from cachecontrol import CacheControl
 # Google library validates signature, audience, issuer and expiration.
 return id_token.verify_oauth2_token(token,Request(session=CacheControl(requests.Session())),audience)

def login(token,identifier):
 audience=client_id()
 if not audience:raise HTTPException(503,'Login Google ainda não configurado.')
 with _lock:
  _purge();pending=_challenges.pop(identifier,None)
 if not pending:raise HTTPException(401,'Tentativa expirada ou já utilizada. Entre novamente.')
 try:claims=verify_google(token,audience)
 except Exception as exc:raise HTTPException(401,'Não foi possível validar o login Google. Tente novamente.') from exc
 if not claims.get('sub') or claims.get('email_verified') is not True or not secrets.compare_digest(str(claims.get('nonce','')),pending['nonce']):
  raise HTTPException(401,'Identidade ou tentativa de login inválida.')
 expires=min(float(claims.get('exp',0)),time.time()+3600)
 if expires<=time.time():raise HTTPException(401,'Login expirado. Entre novamente.')
 session=secrets.token_urlsafe(40);key=hashlib.sha256(session.encode()).hexdigest()
 user={'sub':claims['sub'],'name':claims.get('name','Usuário Google'),'email':claims.get('email',''),'expires':expires}
 with _lock:
  _purge()
  if len(_sessions)>=2000:raise HTTPException(503,'Limite de sessões atingido. Tente mais tarde.')
  _sessions[key]=user
 return {'access_token':session,'expires_at':int(expires),'user':{'name':user['name'],'email':user['email']}}

def require_user(authorization:str|None=Header(default=None)):
 if not authorization or not authorization.startswith('Bearer '):raise HTTPException(401,'Entre com Google para conversar.')
 key=hashlib.sha256(authorization[7:].encode()).hexdigest()
 with _lock:
  _purge();user=_sessions.get(key)
 if not user:raise HTTPException(401,'Sessão encerrada. Entre com Google novamente.')
 return user

def logout(authorization):
 if authorization and authorization.startswith('Bearer '):
  key=hashlib.sha256(authorization[7:].encode()).hexdigest()
  with _lock:_sessions.pop(key,None)
 return {'status':'signed_out'}
