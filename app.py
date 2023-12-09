import asyncio
from pathlib import Path
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable, RunnableParallel, RunnablePassthrough
from langchain.schema.runnable.config import RunnableConfig

import chainlit as cl

import tomllib

ROOT_DIR = Path(__file__).parent


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
    query_chain = (
        ChatPromptTemplate.from_messages(
            [
                # (
                #     "system",
                #     "You are an expert in the fields discussed in this conversation.",
                # ),
                ("human", "{query}"),
            ]
        )
        | model
        | StrOutputParser()
    )

    with open(ROOT_DIR / "templates" / "consensus.txt", "r") as f:
        consensus_prompt = ChatPromptTemplate.from_template(f.read())

    consensus_chain = consensus_prompt | model | StrOutputParser()

    # TODO: figure out how to chain this with LCEL
    # runnable = (
    #     RunnableParallel(query=RunnablePassthrough(), responses=query_chain.batch)
    #     | consensus_chain
    # )
    cl.user_session.set("consensus_runnable", consensus_chain)

    runnable = query_chain
    cl.user_session.set("runnable", runnable)


@cl.on_message
async def on_message(message: cl.Message):
    runnable: Runnable = cl.user_session.get("runnable")  # type: ignore
    consensus_runnable: Runnable = cl.user_session.get("consensus_runnable")  # type: ignore

    msg = cl.Message(content="")

    # TODO: figure out how to chain this with LCEL
    # async for chunk in runnable.astream(
    #     {"query": message.content},
    #     config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    # ):
    #     await msg.stream_token(chunk)

    responses = await runnable.abatch(
        [{"query": message.content}] * 10,
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    )

    responses = "\n\n".join(f"```\n{r}\n```" for r in responses)

    async for chunk in consensus_runnable.astream(
        {"query": message.content, "responses": responses},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()
