from xrpc_client.request import Request


class ClientBase:
    """Low level methods are here"""

    def __init__(self, request=None):
        if request is None:
            request = Request()

        self._request = request

    @property
    def request(self):
        return self.request

    def invoke(self, nsid: str):
        print('invoke', nsid)
        # should be something like this:

        # but it requires work with parsed lexicon. I don't want to parse all lexicon each script run
        # we can resolve all necessary data during generation and place near of nsid

        # if is_post(resolve_http_method_by_nced(nsid)):
        #     self.request.post(...)
        # else:
        #     self.request.get(...)
