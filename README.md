# Claude in Slack Server API

This project starts an HTTP server that provides an API to interact with Claude in Slack. 

This API is protected and configured by Slack's OAuth protocol, users only need to have a Slack account to interact with it.

Don't want to build your own? Try mine: [Add to slack](https://chatgpt-proxy.lss233.com/claude-in-slack/login)


## Installation

```bash
git clone https://github.com/LlmKira/claude-in-slack-server
cd claude-in-slack-server
pip install -r requirements.txt
```

## Usage

### 1. Create a slack app

1. Go to https://api.slack.com/apps, click `From an app manifest` - pick an workspace - next.  

2. Go to `OAuth & Permissions` > `Scopes`, and add following scopes:

Bot Token Scopes:  
| OAuth Scope | Reasons |
| ------------| ------------|
| `channels:history` | Read conversation history and find claude's conversations. |
| `users:read` | Find out the user id of claude and talk to it. |


User Token Scopes:  
| OAuth Scope | Reasons |
| ------------| ------------|
| `chat:write` | Send messages on a user’s behalf. |

3. Go to `OAuth & Permissions` > `Redirect URLs`, and add a OAuth Redirect URL: `http://your_server_ip:5000/callback`  
This should be the same as the environment variable `SLACK_OAUTH_REDIRECT_URI` we defined later.

Your `SLACK_BOT_TOKEN` is at `Bot User OAuth Token`.

4. Go to `Event Subscriptions` > `Enable Events` > `Subscribe to bot events`, add a event:

| Event Name | Reasons |
| ------------| ------------|
| `message.channels` | Receive claude's reply. |

5. Go to `Socket Mode` > `Enable Socket Mode`.

6. Go to `Baisc Information` > `App-Level Tokens` > `Generate Tokens and Scopes`: 

Token Name: `SocketMode`
Scope: `connection:write`

And you will get your `SLACK_APP_TOKEN` here.

### 2. Start the server

To start this project, you will need to declare following environment variables:  
| Key                        | Description                                            | Example                           |
| --------------------------| -------------------------------------------------------| ----------------------------------|
| APP_PORT                   | Server listen port                                     | 5000                              |
| APP_HOST                   | Server listen host                                     | 0.0.0.0                         |
| ENCRYPTION_KEY             | Key used to encrypt user's access_token                 | a_random_string                         |
| SLACK_APP_TOKEN            | App token for Slack API                                 | xapp-1-A05xxxxxLGN8-517xxxxxxxxxx-b853xxxxxxxxxxxxxxxd34850xxxxxxxxxxbed3084|
| SLACK_BOT_TOKEN            | Bot token for Slack API                                 | xoxb-517xxxxxxxxxx-51xxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxx|
| SLACK_OAUTH_CLIENT_ID      | Client ID for Slack API OAuth 2.0 authentication flow    | 1234567890                        |
| SLACK_OAUTH_CLIENT_SECRET  | Client secret for Slack API OAuth 2.0 authentication flow| AbCdEfGhIjKlMnOpQrStUvWxYz123456 |
| SLACK_OAUTH_REDIRECT_URI   | Redirect URI for Slack API OAuth 2.0 authentication flow | http://your_server_ip:5000/callback   |

Example:
```bash
export "APP_PORT"="5000",
export "APP_HOST"="0.0.0.0",
export "ENCRYPTION_KEY"="a_random_string",
export "SLACK_APP_TOKEN"="xapp-1-A05xxxxxLGN8-517xxxxxxxxxx-b853xxxxxxxxxxxxxxxd34850xxxxxxxxxxbed3084",
export "SLACK_BOT_TOKEN"="xoxb-517xxxxxxxxxx-51xxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxx",
export "SLACK_OAUTH_CLIENT_ID"="517xxxxxxxxxx.5xxxxxxxx",
export "SLACK_OAUTH_CLIENT_SECRET"="xxxxxxxxxxxxxxxxxxx",
export "SLACK_OAUTH_REDIRECT_URI"="http://your_server_ip:5000/callback",
```

### 3. Users: Setting up access_token

1. Visit `http://your_server_ip:5000/login`, Authorize your app to workspace.
Users will get a encrypted ACCESS_TOKEN.

2. Invite your app and Claude to a channel of the workspace, and take down the channel id from url (starts with `C0`).


### 4. Sending requests  

Once the server is started, you can visit `http://your_server_ip:5000/docs` to get the API docs.  

This API is designed to compatiable with OpenAI's ChatGPT web api, so you can interact with it using [revChatGPT (Python)](https://github.com/acheong08/ChatGPT) or [chatgpt-api (nodejs)](https://github.com/transitive-bullshit/chatgpt-api)  

Python example:
```python
import json
import uuid
import requests

def interact_with_server(channel_id, access_token, prompt, conversation_id=None):
    payload = {
        "action": "next",
        "messages": [
            {
                "id": str(uuid.uuid4()),
                "role": "user",
                "author": {
                    "role": "user"
                },
                "content": {
                    "content_type": "text",
                    "parts": [
                        prompt
                    ]
                }
            }
        ],
        "conversation_id": conversation_id,
        "parent_message_id": str(uuid.uuid4()),
        "model": "claude-unknown-version"
    }

    headers = {
        'Authorization': f'Bearer {channel_id}@{access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.post("http://your_server_ip:5000/backend-api/conversation", headers=headers, json=payload, timeout=60)
    response.raise_for_status()

    for line in response.iter_lines():
        if not line or line is None:
            continue
        if "data: " in line:
            line = line[6:]
        if "[DONE]" in line:
            break

        try:
            line = json.loads(line)
        except json.decoder.JSONDecodeError:
            continue

        conversation_id = line["conversation_id"]
        message = line["message"]["content"]["parts"][0]
        yield (conversation_id, message)

# Example usage
channel_id = 'C0XXXXXXX' # From Step 3
access_token = 'xxxxxxx' # From Step 3
conversation_id = None

# First call
for conversation_id, message in interact_with_server(channel_id, access_token, "Can you say some emojis?", conversation_id):
    print(f"Received message: {message}")

# Second call
for conversation_id, message in interact_with_server(channel_id, access_token, "Can you use them to make a joke?", conversation_id):
    print(f"Received message: {message}")
```




