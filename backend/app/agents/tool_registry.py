from abc import ABC, abstractmethod
from typing import Dict, Any, List
from app.schemas.tool import ToolMetadata, ToolExecutionResult
import time

class BaseTool(ABC):
    @property
    @abstractmethod
    def metadata(self) -> ToolMetadata:
        """Returns the metadata describing the tool."""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Executes the tool's core logic."""
        pass

    async def run(self, **kwargs) -> ToolExecutionResult:
        """Wrapper to execute the tool, handle errors, and measure latency."""
        start_time = time.time()
        try:
            output = await self.execute(**kwargs)
            status = "success"
            error_message = None
        except Exception as e:
            output = None
            status = "error"
            error_message = str(e)
            
        latency_ms = (time.time() - start_time) * 1000
        
        return ToolExecutionResult(
            tool_name=self.metadata.name,
            status=status,
            output=output,
            latency_ms=latency_ms,
            error_message=error_message
        )

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        self._tools[tool.metadata.name] = tool

    def get_tool(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise ValueError(f"Tool {name} not found in registry.")
        return self._tools[name]

    def get_all_metadata(self) -> List[ToolMetadata]:
        return [tool.metadata for tool in self._tools.values()]

# Global registry instance
registry = ToolRegistry()
