from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled,function_tool
from dotenv import load_dotenv
import os
from openai import AsyncOpenAI
from whatsapp import send_whatsapp_message
import asyncio
import chainlit as cl

load_dotenv()
set_tracing_disabled(True)

API_KEY = os.getenv("GEMINI_API_KEY")

external_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)


@function_tool
def get_user_data(min_age: int) -> list[dict]:
    "Retrieve user data based on a minimum age"
    users = [
        {"name": "Maisam", "age": 22},
        {"name": "Mudassir", "age": 25},
        {"name": "Mohsin", "age": 19},
    ]

    for user in users:
        if user["age"] < min_age:
            users.remove(user)
    
    return users


# Rishtay Wali Agent
rishty_agent = Agent(
    name="Rishty Wali",
    instructions="""
      You are Rishtay Wali Auntie. Find matches from a custom tool based on age only.
      Reply short and send WhatsApp message only if user asks.    """,
    model=model,
    tools=[get_user_data,send_whatsapp_message]
)



@cl.on_chat_start
async def start():
    cl.user_session.set("history",[])
    await cl.Message("Salam beta! Main Rishty Wali Auntie hoon. Apna rishta batain, age batain, aur WhatsApp number dein. 😄").send()


# Runner
@cl.on_message
async def main(message:cl.Message):
    await cl.Message("Thinking...").send() 
    history = cl.user_session.get("history") or []
    history.append({"role": "user", "content": message.content})
    
    result = Runner.run_sync(
        starting_agent=rishty_agent,
        input= history
    )
    
    
    history.append({"role": "assistant", "content": result.final_output})
    
    cl.user_session.set("history",history)
    
    await cl.Message(content=result.final_output).send() 