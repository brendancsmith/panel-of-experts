import asyncio
from operator import itemgetter
from pathlib import Path

import chainlit as cl
import openai
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

from config import Config
from constants import ROOT_DIR, TEMPLATES_DIR


@cl.on_chat_start
async def on_chat_start():
    config = Config()

    model = ChatOpenAI(
        model=config.openai.model,
        temperature=config.openai.temperature,
        timeout=config.openai.timeout,
        streaming=True,
    )

    system_prompt_file = TEMPLATES_DIR / "system.txt"
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

    with open(TEMPLATES_DIR / "consensus.txt", "r") as f:
        template = f.read()

    consensus_prompt = ChatPromptTemplate.from_messages(
        system_message
        + [
            MessagesPlaceholder(variable_name="history"),
            ("human", template),
        ]
    )

    consensus_chain = consensus_prompt | model | StrOutputParser()

    cl.user_session.set("config", config)
    cl.user_session.set("memory", ConversationBufferMemory(return_messages=True))
    cl.user_session.set("consensus_chain", consensus_chain)
    cl.user_session.set("query_chain", query_chain)


@cl.on_message
async def on_message(message: cl.Message):
    config: Config = cl.user_session.get("config")  # type: ignore
    runnable: Runnable = cl.user_session.get("query_chain")  # type: ignore
    consensus_chain: Runnable = cl.user_session.get("consensus_chain")  # type: ignore
    memory: BaseChatMemory = cl.user_session.get("memory")  # type: ignore

    response = cl.Message(content="")

    memory_passthrough = RunnablePassthrough.assign(
        history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
    )

    responses = await (memory_passthrough | runnable).abatch(
        [{"query": message.content}] * config.app.experts,
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    )
    responses = "\n\n".join(f"```\n{r.content}\n```" for r in responses)

    async for chunk in (memory_passthrough | consensus_chain).astream(
        {"query": message.content, "responses": responses},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await response.stream_token(chunk)

    memory.save_context({"input": message.content}, {"output": response.content})

    cl.user_session.set("memory", memory)

    await response.send()
