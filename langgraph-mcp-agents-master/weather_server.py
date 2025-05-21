from mcp import Server, Tool
from mcp.server.sse import sse_server

weather_server = Server()

@weather_server.tool("get_weather")
async def get_weather(location: str) -> str:
    """Get the weather for a given location"""
    # This is a mock implementation - in a real application, you would call a weather API
    return f"{location}의 날씨는 맑습니다."

if __name__ == "__main__":
    sse_server(weather_server, port=8005) 