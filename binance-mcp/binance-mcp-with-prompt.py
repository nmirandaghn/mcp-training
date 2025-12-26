import datetime
from pathlib import Path
from typing import Any

import requests
from mcp.server.fastmcp import FastMCP

THIS_FOLDER = Path(__file__).parent.absolute()
ACTIVITY_LOG_FILE = THIS_FOLDER / "activity.log"
SYMBOL_MAP = """crypto_name,symbol
btc,BTCUSDT
eth,ETHUSDT
bitcoin,BTCUSDT
ethereum,ETHUSDT"""

mcp = FastMCP("Binance MCP")


def get_symbol_from_name(name: str) -> str:
    if name.lower() in ["bitcoin", "btc"]:
        return "BTCUSDT"
    elif name.lower() in ["ethereum", "eth"]:
        return "ETHUSDT"
    else:
        return name.upper()

@mcp.prompt()
def executive_summary() -> str:
    """Returns an executive summary of Bitcoin and Ethereum"""
    return """
    Get the prices of the following crypto asset: btc, eth
    
    Provide me with an executive summary including the 
    two-sentence summary of the crypto asset, the current price, 
    the price change in the last 24 hours, and the percentage change
    in the last 24 hours.

    When using the get_price and get_price_price_change tools,
    use the symbol as the argument.
    
    Symbols: For bitcoin/btc, the symbol is "BTCUSDT".
    Symbols: For ethereum/eth, the symbol is "ETHUSDT".
    """
    
@mcp.tool()
def get_price(symbol: str) -> Any:
    """
    Get the current price of a crypto asset from Binance

    Args:
        symbol (str): The symbol of the crypto asset to get the price of

    Returns:
        Any: The current price of the crypto asset
    """
    symbol = get_symbol_from_name(symbol)
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url)
    if response.status_code != 200:
        with open(ACTIVITY_LOG_FILE, "a") as f:
            f.write(
                f"Error getting price change for {symbol}: {response.status_code} {response.text}\n"
            )
        raise Exception(
            f"Error getting price change for {symbol}: {response.status_code} {response.text}"
        )
    else:
        price = response.json()["price"]
        with open(ACTIVITY_LOG_FILE, "a") as f:
            f.write(
                f"Successfully got price change for {symbol}. Current price is {price}. Current time is {datetime.datetime.now(datetime.UTC)}\n"
            )
    return f"The current price of {symbol} is {price}"


@mcp.resource("file://activity.log")
def activity_log() -> str:
    with open(ACTIVITY_LOG_FILE, "r") as f:
        return f.read()


@mcp.resource("resource://crypto_price/{symbol}")
def get_crypto_price(symbol: str) -> str:
    return get_price(symbol)


@mcp.resource("resource://symbol_map")
def symbol_map() -> str:
    return SYMBOL_MAP


@mcp.tool()
def get_price_price_change(symbol: str) -> Any:
    """
    Get the price change of the last 24 hours of a crypto asset from Binance

    Args:
        symbol (str): The symbol of the crypto asset to get the price change of

    Returns:
        Any: The price change of the crypto asset in the last 24 hours
    """
    symbol = get_symbol_from_name(symbol)
    url = f"https://data-api.binance.vision/api/v3/ticker/24hr?symbol={symbol}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    if not Path(ACTIVITY_LOG_FILE).exists():
        Path(ACTIVITY_LOG_FILE).touch()
    mcp.run(transport="stdio")