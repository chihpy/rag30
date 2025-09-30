"""
reference: https://github.com/run-llama/llama_index/blob/main/docs/examples/examples/workflow/react_agent.ipynb
"""
# helper for get React agent chat_history and parse output
from llama_index.core.agent.react import ReActChatFormatter, ReActOutputParser  
# typing
from typing import List, Any, Optional, Literal
from llama_index.core.tools.types import BaseTool

from llama_index.core.tools import FunctionTool
from llama_index.core.tools import ToolSelection, ToolOutput
from llama_index.core.agent.react.types import (
    ActionReasoningStep,  # parsed ReActAgent output for tool use case
    ObservationReasoningStep,  # reasoning_step for tool output case include fail
)

import os
from dotenv import find_dotenv, load_dotenv
_ = load_dotenv(find_dotenv())

from llama_index.core.llms.llm import LLM
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
from llama_index.core.memory import Memory
from llama_index.utils.workflow import draw_all_possible_flows
from llama_index.core.workflow import (
    Context,
    Workflow,
    StartEvent,
    StopEvent,
    Event,
    step,
)

##### Workflow define block

###### event:
class PrepEvent(Event):
    pass

class InputEvent(Event):
    input: list[ChatMessage]

class ToolCallEvent(Event):
    tool_calls: list[ToolSelection]

class FunctionOutputEvent(Event):
    output: ToolOutput

class StreamEvent(Event):
    msg: Optional[str] = None
    delta: Optional[str] = None

###### The Workflow itself:
class ReActAgent(Workflow):
    def __init__(
        self,
        *args: Any,
        llm: LLM | None = None,
        tools: list[BaseTool] | None = None,
        extra_context: str | None = None,
        streaming: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.tools = tools or []
        self.llm = llm or OpenAI()
        self.formatter = ReActChatFormatter.from_defaults(
            context=extra_context or ""
        )
        self.streaming = False
        self.output_parser = ReActOutputParser()

    @step
    async def new_user_msg(self, ctx: Context, ev: StartEvent) -> PrepEvent:
        # clear sources
        await ctx.store.set("sources", [])

        # init memory if needed
        memory = await ctx.store.get("memory", default=None)
        if not memory:
            memory = Memory.from_defaults()

        # get user input
        user_input = ev.input
        user_msg = ChatMessage(role="user", content=user_input)
        memory.put(user_msg)

        # clear current reasoning
        await ctx.store.set("current_reasoning", [])

        # set memory
        await ctx.store.set("memory", memory)

        return PrepEvent()

    @step
    async def prepare_chat_history(
        self, ctx: Context, ev: PrepEvent
    ) -> InputEvent:
        # get chat history
        memory = await ctx.store.get("memory")
        chat_history = memory.get()
        current_reasoning = await ctx.store.get(
            "current_reasoning", default=[]
        )

        # format the prompt with react instructions
        llm_input = self.formatter.format(
            self.tools, chat_history, current_reasoning=current_reasoning
        )
        return InputEvent(input=llm_input)

    @step
    async def handle_llm_input(
        self, ctx: Context, ev: InputEvent
    ) -> ToolCallEvent | StopEvent:
        chat_history = ev.input
        current_reasoning = await ctx.store.get(
            "current_reasoning", default=[]
        )
        memory = await ctx.store.get("memory")

        if self.streaming:
            response_gen = await self.llm.astream_chat(chat_history)
            async for response in response_gen:
                ctx.write_event_to_stream(StreamEvent(delta=response.delta or ""))
        else:
            response = await self.llm.achat(chat_history)
            ctx.write_event_to_stream(StreamEvent(msg=response.message.content))

        try:
            reasoning_step = self.output_parser.parse(response.message.content)  # output_parser.parse
            current_reasoning.append(reasoning_step)

            if reasoning_step.is_done:
                memory.put(
                    ChatMessage(
                        role="assistant", content=reasoning_step.response
                    )
                )
                await ctx.store.set("memory", memory)
                await ctx.store.set("current_reasoning", current_reasoning)

                sources = await ctx.store.get("sources", default=[])

                return StopEvent(
                    result={
                        "response": reasoning_step.response,
                        "sources": [sources],
                        "reasoning": current_reasoning,
                    }
                )
            elif isinstance(reasoning_step, ActionReasoningStep):
                tool_name = reasoning_step.action
                tool_args = reasoning_step.action_input
                return ToolCallEvent(
                    tool_calls=[
                        ToolSelection(
                            tool_id="fake",
                            tool_name=tool_name,
                            tool_kwargs=tool_args,
                        )
                    ]
                )
        except Exception as e:
            current_reasoning.append(
                ObservationReasoningStep(
                    observation=f"There was an error in parsing my reasoning: {e}"
                )
            )
            await ctx.store.set("current_reasoning", current_reasoning)

        # if no tool calls or final response, iterate again
        return PrepEvent()

    @step
    async def handle_tool_calls(
        self, ctx: Context, ev: ToolCallEvent
    ) -> PrepEvent:
        tool_calls = ev.tool_calls
        tools_by_name = {tool.metadata.get_name(): tool for tool in self.tools}
        current_reasoning = await ctx.store.get(
            "current_reasoning", default=[]
        )
        sources = await ctx.store.get("sources", default=[])

        # call tools -- safely!
        for tool_call in tool_calls:
            tool = tools_by_name.get(tool_call.tool_name)
            if not tool:
                current_reasoning.append(
                    ObservationReasoningStep(
                        observation=f"Tool {tool_call.tool_name} does not exist"
                    )
                )
                continue

            try:
                tool_output = tool(**tool_call.tool_kwargs)
                sources.append(tool_output)
                current_reasoning.append(
                    ObservationReasoningStep(observation=tool_output.content)
                )
            except Exception as e:
                current_reasoning.append(
                    ObservationReasoningStep(
                        observation=f"Error calling tool {tool.metadata.get_name()}: {e}"
                    )
                )

        # save new state in context
        await ctx.store.set("sources", sources)
        await ctx.store.set("current_reasoning", current_reasoning)

        # prep the next iteraiton
        return PrepEvent()

def get_tool_list():

    def add(a: Literal[0, 1], b: Literal[0, 1]) -> Literal[0, 1]:
        """這是一個在二元代數結構上定義的「加法」，你可以藉由呼叫這個工具來釐清它的運作邏輯。

        此加法滿足以下公理性特徵：
        - 交換律：a ⊕ b = b ⊕ a
        - 結合律：(a ⊕ b) ⊕ c = a ⊕ (b ⊕ c)
        - 冪等律：a ⊕ a = a
        - 加法單位元：0，使得 a ⊕ 0 = a
        - 定義域僅含 0 與 1

        Parameters:
            a: either 0 or 1
            b: either 0 or 1
        Returns:
            0 or 1
        """
        if a not in (0, 1) or b not in (0, 1):
            raise ValueError("add is only defined on {0,1}.")
        return 1 if (a == 1 or b == 1) else 0
    
    tools = [
        FunctionTool.from_defaults(add)
    ]
    return tools

async def main():
    # get tool_list
    tool_list = get_tool_list()
    # llm
    llm = OpenAI(model="gpt-5-mini")
    # workflow
    w = ReActAgent(llm=llm, tools=tool_list, timeout=120, verbose=False)
    print('---query1: no tool use')

    query1 = '簡單的問題不要呼叫工具，不用想太多，請問1+1=?'
    print(query1)
    handler = w.run(input=query1)
    async for ev in handler.stream_events(expose_internal=False):
        if isinstance(ev, StopEvent):
            print(ev.result['response'])
        else:
            print(ev.msg)
    print('-----' * 10)
    print('---query2: suggest tool use')

    query2 = '請重新思考一下， 1+1 等於多少，他真的等於 2 嗎? 還是會有其他可能，你有用其他工具查證嗎?'
    print(query2)
    handler = w.run(input=query2)
    async for ev in handler.stream_events(expose_internal=False):
        if isinstance(ev, StopEvent):
            print("====final response")
            print(ev.result['response'])
        else:
            print(ev.msg)

if __name__ == "__main__":
    # let's visualize our workflow first
#    dest_html = "day15_ReActAgent.html"
#    print(f'write workflow viz result to {dest_html}')
#    draw_all_possible_flows(ReActAgent, filename=dest_html)
    # then query the workflow
    import asyncio
    asyncio.run(main())