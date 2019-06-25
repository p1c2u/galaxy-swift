import json

from galaxy_swift.jsonrpc.exceptions import InvalidRequest, ParseError


class JsonRpcParser:

    def parse(self, data):
        try:
            jsonrpc_request = json.loads(data, encoding="utf-8")
            if jsonrpc_request.get("jsonrpc") != "2.0":
                raise InvalidRequest()
            del jsonrpc_request["jsonrpc"]
            return jsonrpc_request
        except json.JSONDecodeError:
            raise ParseError()
        except TypeError:
            raise InvalidRequest()
