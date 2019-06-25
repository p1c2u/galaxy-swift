import socketserver


class GalaxyTCPHandler(socketserver.StreamRequestHandler):

    def handle(self):
        self.server.reader = self.rfile
        self.server.writer = self.wfile
        self.server.read()
