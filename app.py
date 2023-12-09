from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig

import chainlit as cl

import tomllib


@cl.on_chat_start
async def on_chat_start():
    with open("config.toml", "rb") as f:
        config = tomllib.load(f)

    model = ChatOpenAI(
        model=config["openai"]["model"],
        temperature=config["openai"]["temperature"],
        timeout=config["openai"]["timeout"],
        streaming=True,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            # (
            #     "system",
            #     "You are an expert in the fields discussed in this conversation.",
            # ),
            ("human", "{question}"),
        ]
    )
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)


@cl.on_message
async def on_message(message: cl.Message):
    runnable: Runnable = cl.user_session.get("runnable")  # type: ignore

    msg = cl.Message(content="")

    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()
