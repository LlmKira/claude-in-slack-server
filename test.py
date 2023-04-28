from os import environ

environ['ENCRYPTION_KEY'] = 'TEST_KEY'

from secure import encrypt_token, decrypt_token


def encryption_test():
    test_token = 'xobo-this-is-a-fake-token'
    encrypted = encrypt_token(test_token)
    print("encrypted: ", encrypted)
    decrypted = decrypt_token(encrypted)
    print("decrypted: ", encrypted)
    print(test_token == decrypted)


encryption_test()

environ['CHATGPT_BASE_URL'] = 'http://localhost:3000/backend-api/'

from revChatGPT.V1 import Chatbot

bot = Chatbot(config={
    "access_token": environ['CLAUDE_TEST_ACCESS_TOKEN']})
for response in bot.ask(prompt="This is just a funny test. I will your ability of summarizing conversation context. "
                               "Let's begin to count from 1 to infinity. "
                               "I will begin with 1, you will say next."):
    print(response)

for response in bot.ask(prompt="3"):
    print(response)

for response in bot.ask(prompt="5"):
    print(response)
