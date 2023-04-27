import os
import httpx

import asyncio
import uuid
from typing import Dict
from urllib.parse import quote

import uvicorn
from fastapi import FastAPI, Request, Response, status, HTTPException
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from sse_starlette.sse import EventSourceResponse

from model import ConversationResponse, ConversationRequest, Message, Content, Author

message_mappings: Dict[str, asyncio.Queue[str]] = {}

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_CLIENT_ID = os.environ["SLACK_OAUTH_CLIENT_ID"]
SLACK_CLIENT_SECRET = os.environ["SLACK_OAUTH_CLIENT_SECRET"]
SLACK_REDIRECT_URI = os.environ["SLACK_OAUTH_REDIRECT_URI"]

async_client = httpx.AsyncClient()
fastapi_app = FastAPI()
slack_app = AsyncApp(token=SLACK_BOT_TOKEN)

templates = Jinja2Templates(directory="template")


@fastapi_app.get("/login")
async def login():
    return RedirectResponse(url=f"https://slack.com/oauth/v2/authorize?"
                                f"user_scope=chat%3Awrite"
                                f"&scope=chat%3Awrite"
                                f"&client_id={SLACK_CLIENT_ID}"
                                f"&redirect_uri={quote(SLACK_REDIRECT_URI)}")


@fastapi_app.get("/callback")
async def callback(code: str = None, error: str = None):
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    if not code:
        raise HTTPException(status_code=400, detail="Missing OAuth code")
    response = await async_client.post(
        "https://slack.com/api/oauth.v2.access",
        data={
            "client_id": SLACK_CLIENT_ID,
            "client_secret": SLACK_CLIENT_SECRET,
            "code": code,
            "redirect_uri": SLACK_REDIRECT_URI
        },
    )
    body = response.json()
    if body['ok']:
        return templates.TemplateResponse("success.html", {"access_token": body['authed_user']['access_token']})
    return body


@slack_app.command("/hello-socket-mode")
async def hello_command(ack, body):
    user_id = body["user_id"]
    ack(f"Hi, <@{user_id}>!")


@slack_app.event("message")
async def event_message(say, event, message):
    if message.get('subtype') == 'message_changed':
        user_id = message['message']['parent_user_id']
        user_ts = message['message']['thread_ts']
        text = message['message']['text']
        if queue := message_mappings.get(f"{user_id}-{user_ts}"):
            await queue.put(text)
            await queue.join()


@fastapi_app.get('/backend-api/conversations')
async def conversations():
    return {
        "items": []
    }


@fastapi_app.post('/backend-api/conversation', response_model=ConversationResponse)
async def conversation(request_data: ConversationRequest, request: Request, response: Response):
    # Perform some processing on the request data
    channel, access_token = request.headers \
        .get('Authorization', '@') \
        .removeprefix('Bearer ') \
        .split('@', 1)
    if not access_token:
        response.status_code = status.HTTP_403_FORBIDDEN
        return ConversationResponse(error="You need to provide CHANNEL_ID@ACCESS_TOKEN in Authorization header.")

    prompt = ''.join(request_data.messages[0].content.parts)
    payload = {
        'text': f'<@U0550SE0RQU> {prompt}',
        'channel': channel,
        "thread_ts": request_data.conversation_id
    }

    resp = await async_client.post(url="https://slack.com/api/chat.postMessage", headers={
        'Authorization': f'Bearer {access_token}'
    }, data=payload)
    body = resp.json()
    if error := body.get('error'):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ConversationResponse(error=error)

    user_id = body["message"]["user"]
    user_ts = request_data.conversation_id or body["message"]["ts"]
    message_mappings[f"{user_id}-{user_ts}"] = asyncio.Queue()
    queue = message_mappings[f"{user_id}-{user_ts}"]

    async def sse_emitter():
        while True:
            if await request.is_disconnected():
                del message_mappings[f"{user_id}-{user_ts}"]
                return
            message = await queue.get()
            message = message.strip()
            yield {
                'event': 'data',
                'data': ConversationResponse(
                    message=Message(
                        id=str(uuid.uuid4()),
                        role="assistant",
                        content=Content(content_type="text", parts=[message.removesuffix('\n\n_Typing…_')]),
                        author=Author(role="assistant"), ),
                    conversation_id=user_ts,
                    error=None,
                ).json()
            }
            queue.task_done()
            if not message.endswith('_Typing…_'):
                yield {
                    'event': 'data',
                    'data': '[DONE]'
                }
                del message_mappings[f"{user_id}-{user_ts}"]
                return

    return EventSourceResponse(sse_emitter())


@fastapi_app.on_event("startup")
async def startup_event():
    await AsyncSocketModeHandler(slack_app, os.environ["SLACK_APP_TOKEN"]).connect_async()


if __name__ == "__main__":
    uvicorn.run(fastapi_app, host="0.0.0.0", port=3000, reload=False)
