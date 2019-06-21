import attr


class JsonRpcError(Exception):
    pass


class ParseError(JsonRpcError):
    pass


@attr.s(frozen=True)
class InvalidRequest(JsonRpcError):
    code = attr.ib(type=int)
    message = attr.ib(type=str)
    data = attr.ib(default=None)
