import json, time
from collections import namedtuple

# Create a namedtuple to hold the values we expect to retrieve from json messages.
ErrorResponse = namedtuple('ErrorResponse', ['type', 'message'])
OkResponse = namedtuple('OkResponse', ['type', 'message', 'token'])

def join_generate(username: str, password:str, my_public_key:str = None) -> str:
  # join as existing or new user
  join_msg = f'{{"join": {{"username": "{username}","password": "{password}","token": "{my_public_key}" }} }}' #{"join": {"username": "ohhimark","password": "password123","token":"my_public_key"}}
  return join_msg


def post_generate(my_public_key:str, message:str, timestamp:float = 0) -> str:
  if timestamp == 0:
    timestamp = time.time()
  post_msg = f'{{"token": "{my_public_key}", "post": {{"entry": "{message}","timestamp": "{timestamp}" }} }}'
  return post_msg


def bio_generate(my_public_key:str, bio:str, timestamp:float = 0) -> str:
  if timestamp == 0:
    timestamp = time.time()
  bio_msg = f'{{"token": "{my_public_key}", "bio": {{"entry": "{bio}","timestamp": "{timestamp}" }} }}'
  return bio_msg


def response_generate(json_msg:str):     
  try:
    obj = json.loads(json_msg)
    tp = obj['response']['type']
    if tp == 'ok':      #ok =   '{"response": {"type": "ok", "message": "", "token":"server_public_key"}}'
      message = obj['response']['message']
      if 'token' in obj['response'].keys():
        token = obj['response']['token']
        return OkResponse(tp, message, token)
      else:
        return OkResponse(tp, message, '')

    elif tp == 'error': #error = '{"response": {"type": "error", "message": "An error message will be contained here."}}'
      message = obj['response']['message']

      return ErrorResponse(tp, message)

  except json.JSONDecodeError:
    print("Json cannot be decoded.")

