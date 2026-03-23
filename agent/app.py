import asyncio
import json
import os
from mcp import Resource
from mcp.types import Prompt
from agent.mcp_client import MCPClient
from agent.dial_client import DialClient
from agent.models.message import Message, Role
from agent.prompts import SYSTEM_PROMPT


async def main():
    # 1. Create MCP client and open connection
    async with MCPClient(mcp_server_url="http://localhost:8005/mcp") as mcp_client:

        # 2. Get Available MCP Resources and print them
        resources: list[Resource] = await mcp_client.get_resources()
        print("\n📦 Available MCP Resources:")
        for resource in resources:
            print(f"  - {resource.name}: {resource.uri}")

        # 3. Get Available MCP Tools, assign to `tools`, print them
        tools = await mcp_client.get_tools()
        print("\n🔧 Available MCP Tools:")
        for tool in tools:
            print(f"  - {tool['function']['name']}: {tool['function']['description']}")

        # 4. Create DialClient
        dial_client = DialClient(
            api_key="dial-rebxmsuuq0txunfpergznh7zhaz",
            endpoint="https://ai-proxy.lab.epam.com",
            tools=tools,
            mcp_client=mcp_client
        )

        # 5. Create messages list and add SYSTEM_PROMPT
        messages: list[Message] = [
            Message(role=Role.SYSTEM, content=SYSTEM_PROMPT)
        ]

        # 6. Add MCP Prompts as User messages
        prompts: list[Prompt] = await mcp_client.get_prompts()
        print("\n📝 Available MCP Prompts:")
        for prompt in prompts:
            print(f"  - {prompt.name}: {prompt.description}")
            prompt_content = await mcp_client.get_prompt(prompt.name)
            messages.append(Message(role=Role.USER, content=prompt_content))

        # 7. Console chat loop
        print("\n💬 User Management Agent ready. Type 'exit' or 'quit' to stop.\n")
        while True:
            user_input = input("👤: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit"):
                print("Goodbye!")
                break

            messages.append(Message(role=Role.USER, content=user_input))

            ai_message = await dial_client.get_completion(messages)
            messages.append(ai_message)


if __name__ == "__main__":
    asyncio.run(main())