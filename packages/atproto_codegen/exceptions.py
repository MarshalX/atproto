from atproto_core.exceptions import AtProtocolError


class CodegenError(AtProtocolError):
    """Base class for errors raised by the code generator."""


class LexiconsNotFoundError(CodegenError):
    """No lexicons to generate code for were found."""


class UnresolvedReferenceError(CodegenError):
    """A lexicon references a definition that is neither being generated nor available in the installed SDK."""


class RuffNotFoundError(CodegenError, FileNotFoundError):
    """Ruff is needed to format generated code but is not installed."""
