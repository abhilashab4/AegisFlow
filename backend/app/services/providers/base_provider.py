from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: str
    ):
        pass

    @abstractmethod
    async def stream_generate(
        self,
        prompt: str,
        model: str
    ):
        pass