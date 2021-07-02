import functools
from typing import Any, Dict
from aiogram.dispatcher.handler.base import BaseHandler, T
from abc import abstractmethod, ABC
from functools import partial
import inspect

from aiogram.dispatcher.handler.base import BaseHandler


def partialclass(cls, *args, **kwds):
    class NewCls(cls):
        __init__ = functools.partialmethod(cls.__init__, *args, **kwds)

    return NewCls


class BaseHandlerContextWrapper(BaseHandler[T], ABC):
    def __init__(self, event: T, **kwargs: Any) -> None:
        super().__init__(event, **kwargs)

        callback = inspect.unwrap(self.unpack_handle)
        self.spec = inspect.getfullargspec(callback)

    async def handle(
        self,
    ) -> Any:
        wrapped = partial(
            self.unpack_handle,
            **self._prepare_kwargs(
                {
                    "bot": self.bot,
                    "event": self.event,
                    "update": self.update,
                    **self.data,
                }
            )
        )

        return await wrapped()

    def _prepare_kwargs(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        if self.spec.varkw:
            return kwargs

        return {k: v for k, v in kwargs.items() if k in self.spec.args}

    @abstractmethod
    async def unpack_handle(
        self,
    ) -> Any:  # pragma: no cover
        pass
