#    Copyright (c) 2024 Rafal Wytrykus
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""
Example of a chat agent that uses the Py2Mac package and OpenAI models to interact with the UI.

To run this example, run the following command:
```bash
chainlit run py2mac_agent.py -w
```
"""
import logging
from typing import cast

import chainlit as cl
from chainlit.input_widget import Select
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI

import py2mac.application
import py2mac.langchain_py2mac.tools

logger = logging.getLogger(__name__)


def build_chain(model: str, selected_application: py2mac.application.Application | None) -> Runnable:
    if selected_application is None:
        return RunnableLambda(lambda _: "Please select an application to interact with.")

    llm = ChatOpenAI(streaming=True, model=model)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""You're an AI assistant that can interact with macos applications via accessibility APIs.
                You will interact with the application "{selected_application.localized_name}".
                Use tools to interact with the application:
                get_ui_state - Get the current state of the UI elements of the application.
                set_ui_attribute - Set an attribute of a UI element.
                trigger_ui_action - Trigger an action on a UI element.

                Typically, your task will start with a call to get_ui_state to get the current state of the UI elements.
                After that, you can set attributes or trigger actions on the UI elements.
                If you expect the application to change state, you should call get_ui_state again to get the updated state.

                If your task involves multiple steps, please provide plan for your next actions after each time you retrieve the UI state.
                """,
            ),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )
    tools = [
        py2mac.langchain_py2mac.tools.get_ui_state_tool(application=selected_application),
        py2mac.langchain_py2mac.tools.get_ui_set_attribute_tool(application=selected_application),
        py2mac.langchain_py2mac.tools.get_ui_action_tool(application=selected_application),
    ]
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor


@cl.on_chat_start
async def on_chat_start():
    logger.info("Starting chat...")
    running_applications = py2mac.application.get_running_applications()
    running_applications_dict = {f"{app.localized_name} <PID: {app.pid}>": app for app in running_applications}
    cl.user_session.set("running_applications_dict", running_applications_dict)
    cl.user_session.set("message_history", [])

    settings = await cl.ChatSettings(
        [
            Select(
                id="Application",
                label="Application to interact with",
                values=list(sorted(running_applications_dict.keys())),
            ),
            Select(
                id="Model",
                label="OpenAI - Model",
                values=["gpt-4o", "gpt-4o-mini"],
                initial_index=0,
            ),
        ]
    ).send()

    selected_application = cl.user_session.get("running_applications_dict").get(
        cl.user_session.get("chat_settings")["Application"]
    )
    runnable = build_chain(model=settings["Model"], selected_application=selected_application)
    cl.user_session.set("runnable", runnable)


@cl.on_settings_update
async def setup_agent(settings):
    logger.info("Settings updated: %s", settings)
    selected_application = cl.user_session.get("running_applications_dict").get(
        cl.user_session.get("chat_settings")["Application"]
    )
    runnable = build_chain(model=settings["Model"], selected_application=selected_application)
    cl.user_session.set("runnable", runnable)


@cl.on_message
async def on_message(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})

    runnable = cast(Runnable, cl.user_session.get("runnable"))  # type: Runnable

    msg = cl.Message(content="")

    async for chunk in runnable.astream(
        {"input": message.content, "chat_history": message_history},
        config=RunnableConfig(
            callbacks=[cl.LangchainCallbackHandler(stream_final_answer=True, force_stream_final_answer=True)]
        ),
    ):
        # final answer and intermediate steps are streamed as part of the callback
        pass

        # if "output" in chunk:
        #     await msg.stream_token(chunk["output"])

    message_history.append({"role": "assistant", "content": msg.content})
    await msg.update()
