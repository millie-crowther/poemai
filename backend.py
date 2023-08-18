import asyncio
from websockets.server import serve
import json
import openai
import random

openai.api_key="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"

model_name = 'gpt-3.5-turbo'
models = openai.Model.list()['data']
model_names = {model['id'] for model in models}
if 'gpt-4' in model_names:
    model_name = 'gpt-4'

print(f"Using model = '{model_name}'")

def get_poem():
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "please write four phrases of up to eight syllables from separate experimental prose texts inspired by two of the following authors: walter benjamin, octavia butler, Ursula le guin, k allado-mcdowell and Samuel Delaney. Please also do not use the worlds 'realm' or 'tapestry' or any adverbs.  please organise these into one paragraph of four lines."}
    ]
    try:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=messages,
            temperature=0.5,
            max_tokens=128,
            n=1,
            stop=None,
            presence_penalty=0,
            frequency_penalty=0.1,
        )
        poem = response['choices'][0]['message']['content']
    except:
        poem = "Unable to create poem"
    print(f"new poem: {poem}")
    return poem

poems = []
all_clients = set()

async def update_poems():
    message = json.dumps({
        "type": "poemUpdate",
        "poems": poems
    })
    for websocket in all_clients.copy():
        try:
            await websocket.send(message)
        except:
            pass
    print(poems)

async def update_strike():
    message = json.dumps({
        "type": "poemStrike"
    })
    for websocket in all_clients.copy():
        try:
            await websocket.send(message)
        except:
            pass

async def update_quote():
    message = json.dumps({
        "type": "poemQuote"
    })
    for websocket in all_clients.copy():
        try:
            await websocket.send(message)
        except:
            pass

async def echo(websocket):
    global poems
    print("new client")
    all_clients.add(websocket)
    async for message in websocket:
        print(f"received message = {message}")
        try:
            request = json.loads(message)
            if request["type"] == "buttonClick":
                print("New Poem Requested!!!")
                choice = random.randint(0, 2)
                if choice == 0:
                    poems.append(get_poem())
                    await update_poems()
                elif choice == 1:
                    await update_strike()
                else:
                    await update_quote()
            elif request["type"] == "updatePoems":
                await update_poems()
            elif request["type"] == "reset":
                poems = []
                await update_poems()
        except Exception as e:
            print(str(e))
            print("Failed to process message")      

async def main():
    async with serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever

asyncio.run(main())
