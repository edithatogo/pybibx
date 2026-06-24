from __future__ import annotations

from typing import TYPE_CHECKING

__version__ = "5.9.2"

if TYPE_CHECKING:
    from .base.pbx import pbx_probe

    bibliometrix = pbx_probe

__all__ = [
    "__version__",
    "bibliometrix",
    "pbx_probe",
    "web_app",
    "web_stop",
]


def __getattr__(name: str) -> object:
    if name in {"bibliometrix", "pbx_probe"}:
        from .base.pbx import pbx_probe as _pbx_probe  # noqa: PLC0415

        return _pbx_probe
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)


def web_app(port: int = 5173, open_browser: bool = True) -> str | None:  # noqa: FBT001, FBT002
    from .base.app import web_app as _web_app  # noqa: PLC0415

    return _web_app(port=port, open_browser=open_browser)


def web_stop() -> bool:
    from .base.app import web_stop as _web_stop  # noqa: PLC0415

    return _web_stop()
