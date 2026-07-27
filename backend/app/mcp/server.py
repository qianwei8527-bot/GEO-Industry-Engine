from typing import Any, Callable, Dict


class MCPServerError(Exception):
    pass


class MCPServer:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}

    def register(self, name: str, fn: Callable):
        self._tools[name] = fn

    def list_tools(self) -> list:
        return [{"name": k, "description": v.__doc__ or ""} for k, v in self._tools.items()]

    async def call(self, name: str, params: dict = None) -> Any:
        if name not in self._tools:
            raise MCPServerError(f"Tool not found: {name}")
        fn = self._tools[name]
        if params:
            return await fn(**params)
        return await fn()
