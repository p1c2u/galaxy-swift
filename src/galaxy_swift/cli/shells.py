try:
    from IPython.terminal.embed import InteractiveShellEmbed
except ImportError:
    exit("Install IPython")


class GalaxyInteractiveShellEmbed(InteractiveShellEmbed):

    usage = "Galaxy shell usage"
    banner1 = """Galaxy shell"""
    banner2 = """
starting client .. OK
starting plugin .. OK
establishing plugin<->client connection .. OK

Environment:
  client            -> Galaxy client stub.

Client methods:
  shutdown          -> plugin shutdown.
  get_capabilities  -> plugin capabilities.
    """
    display_banner = True

    def __call__(self, client):
        local_ns = {
            'client': client,
        }
        return super(GalaxyInteractiveShellEmbed, self).__call__(
            local_ns=local_ns,
        )
