from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT_FOLDER = Path(__file__).parent.absolute()
MCP_FOLDER = ROOT_FOLDER / "binance_mcp_reference_implementation"

server_params = StdioServerParameters(
    command="python",  # Executable
    args=[str(MCP_FOLDER / "binance_mcp.py")],
    env=None,
)


async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            result = await session.call_tool(
                "get_price", arguments={"symbol": "BTCUSDXXX"}
            )
            print(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
