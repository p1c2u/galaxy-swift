from collections import namedtuple


Request = namedtuple("Request", ["method", "params", "id"], defaults=[{}, None])
Response = namedtuple("Response", ["result", "id"], defaults=[{}, None])
Error = namedtuple("Error", ["error", "id"], defaults=[{}, None])
Method = namedtuple("Method", ["callback", "signature", "internal", "sensitive_params"])
