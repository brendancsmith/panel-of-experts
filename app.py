import asyncio
import tomllib
from operator import itemgetter
from pathlib import Path

import chainlit as cl
from langchain.chains.conversation.base import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory.buffer import ConversationBufferMemory
from langchain.memory.chat_memory import BaseChatMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import StrOutputParser
from langchain.schema.runnable import (
    Runnable,
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)
from langchain.schema.runnable.config import RunnableConfig

ROOT_DIR = Path(__file__).parent

with open("config.toml", "rb") as f:
    config = tomllib.load(f)


@cl.on_chat_start
async def on_chat_start():
    model = ChatOpenAI(
        model=config["openai"]["model"],
        temperature=config["openai"]["temperature"],
        timeout=config["openai"]["timeout"],
        streaming=True,
    )

    system_prompt_file = ROOT_DIR / "templates" / "system.txt"
    system_prompt = ""

    with open(system_prompt_file, "r") as f:
        system_prompt = f.read()

    system_message = [("system", system_prompt)] if system_prompt else []

    query_chain = (
        ChatPromptTemplate.from_messages(
            system_message
            + [
                MessagesPlaceholder(variable_name="history"),
                ("human", "{query}"),
            ]
        )
        | model
    )

    with open(ROOT_DIR / "templates" / "consensus.txt", "r") as f:
        template = f.read()

    consensus_prompt = ChatPromptTemplate.from_messages(
        system_message
        + [
            # ("system", "You are an expert in the fields discussed in this conversation."),
            MessagesPlaceholder(variable_name="history"),
            ("human", template),
        ]
    )

    cl.user_session.set("memory", ConversationBufferMemory(return_messages=True))

    consensus_chain = consensus_prompt | model | StrOutputParser()

    # TODO: figure out how to chain this with LCEL
    # runnable = (
    #     RunnableParallel(query=RunnablePassthrough(), responses=query_chain.batch)
    #     | consensus_chain
    # )
    cl.user_session.set("consensus_chain", consensus_chain)

    cl.user_session.set("query_chain", query_chain)


@cl.on_message
async def on_message(message: cl.Message):
    runnable: Runnable = cl.user_session.get("query_chain")  # type: ignore
    consensus_chain: Runnable = cl.user_session.get("consensus_chain")  # type: ignore
    memory: BaseChatMemory = cl.user_session.get("memory")  # type: ignore

    print("MEMORY BEFORE:", memory.chat_memory)

    msg = cl.Message(content="")

    # TODO: figure out how to chain this with LCEL
    # async for chunk in runnable.astream(
    #     {"query": message.content},
    #     config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    # ):
    #     await msg.stream_token(chunk)

    memory_passthrough = RunnablePassthrough.assign(
        history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
    )

    responses = await (memory_passthrough | runnable).abatch(
        [{"query": message.content}] * config["app"]["experts"],
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    )
    responses = "\n\n".join(f"```\n{r}\n```" for r in responses)

    async for chunk in (memory_passthrough | consensus_chain).astream(
        {"query": message.content, "responses": responses},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    memory.save_context({"input": message.content}, {"output": msg.content})

    print("MEMORY AFTER:", memory)

    cl.user_session.set("memory", memory)

    await msg.send()
