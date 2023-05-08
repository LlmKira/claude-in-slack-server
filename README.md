# Claude in Slack Server API

This project starts an HTTP server that provides an API to interact with Claude in Slack.

## Installation

```bash
git clone https://github.com/LlmKira/claude-in-slack-server
cd claude-in-slack-server
pip install -r requirements.txt
```

## Usage

To start this project, you will need to declare following environment variables:  
| Key                        | Description                                            | Example                           |
| --------------------------| -------------------------------------------------------| ----------------------------------|
| APP_PORT                   | Server listen port                                     | 5000                              |
| APP_HOST                   | Server listen host                                     | localhost                         |
| ENCRYPTION_KEY             | Key used to encrypt user's access_token                 | S3cr3tK3y                         |
| SLACK_APP_TOKEN            | App token for Slack API                                 | xoxa-123456789012-123456789012-1234|
| SLACK_BOT_TOKEN            | Bot token for Slack API                                 | xoxb-123456789012-123456789012-1234|
| SLACK_OAUTH_CLIENT_ID      | Client ID for Slack API OAuth 2.0 authentication flow    | 1234567890                        |
| SLACK_OAUTH_CLIENT_SECRET  | Client secret for Slack API OAuth 2.0 authentication flow| AbCdEfGhIjKlMnOpQrStUvWxYz123456 |
| SLACK_OAUTH_REDIRECT_URI   | Redirect URI for Slack API OAuth 2.0 authentication flow | http://your_server_ip:5000/callback   |

Example:
```bash
export "APP_PORT"="5000",
export "APP_HOST"="0.0.0.0",
export "ENCRYPTION_KEY"="random_encryption_key_here",
export "SLACK_APP_TOKEN"="xapp-1-A05xxxxxLGN8-517xxxxxxxxxx-b853xxxxxxxxxxxxxxxd34850xxxxxxxxxxbed3084",
export "SLACK_BOT_TOKEN"="xoxb-517xxxxxxxxxx-51xxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxx",
export "SLACK_OAUTH_CLIENT_ID"="517xxxxxxxxxx.5xxxxxxxx",
export "SLACK_OAUTH_CLIENT_SECRET"="xxxxxxxxxxxxxxxxxxx",
export "SLACK_OAUTH_REDIRECT_URI"="http://your_server_ip:5000/callback",
```

## Example Server
Don't want to build your own? try mine:  [Add to slack](https://chatgpt-proxy.lss233.com/claude-in-slack/login)
