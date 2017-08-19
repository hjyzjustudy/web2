#test
import socket
import StringIO
import sys

class WSGIServer(object):
	
	#define class variable
	address_family = socket.AF_INET
	socket_type = socket.SOCK_STREAM
	request_queue_size = 1

	def __init__(self, server_address):
		self.listen_socket = listen_socket = socket.socket(
			self.address_family,
			self.socket_type
		)

		#create listen socket
		listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		listen_socket.bind(server_address)
		listen_socket.listen(self.request_queue_size)

		host, port = self.listen_socket.getsockname()[:2]
		self.server_name = socket.getfqdn(host)
		self.server_port = port

		self.headers_set = []

	def set_app(self, application):
		self.application = application

	def serve_forever(self):
		listen_socket = self.listen_socket
		while True:
			#new connection
			self.client_connection, client_address = listen_socket.accept()
			
			self.handle_one_request()

	def handle_one_request(self):
		self.request_data = request_data = self.client_connection.recv(1024)

		print(''.join(
			'< {lint}\n'.format(line=line)
			for line in request_data.splitlines()
		))

		#parse request
		self.parse_request(request_data)

		#set env and start_response

		env = self.get_environ()

		#call our application
		result = self.application(env, self.start_response)

		#construct a response and send it back to the client
		self.finish_response(result)

	def parse_request(self, text):
		request_line = text.splitlines()[0]
		request_line = request_line.rstrip('\r\n')

		(self.request_method,
		 self.path,
		 self.request_version
		 ) = request_line.split()

	def get_environ(self):
		env = {}

		env['wsgi.version'] = (1, 0)
		env['wsgi.url_scheme'] = 'http'
		env['wsgi.input'] = StringIO.StringIO(self.request_data)
		env['wsgi.errors'] sys.stderr
		env['wsgi.multithread'] = False
		env['wsgi.multiprocess'] = False
		env['wsgi.run_once'] = False
		#CGI variables
		env['REQUEST_METHOD'] = self.request_method
		env['PAHT_INOF'] = self.path
		env['SERVER_NAME'] = self.server_name
		env['SERVER_PORT'] = str(self.server_port)

		return env

	def start_response(self, status, response_headers, exc_info=None);
		server_headers = [
			('Date', '22:04'),
			('Server', 'WSGIServer 0.3'),
		]

		self.headers_set = [status, response_headers + server_headers]

	def finish_response(self, result):
		try:
			status, response_headers = self.headers_set
			response = 'HTTP/1.1 {status}\r\n'.format(status=status)
			for header in response_headers:
				response += '{0}: {1}\r\n'.format(*header)
			response += '\r\n'
			for data in result:
				response += data

			print(''.join(
				'> {line}\n'.format(line=line)
				for line in response.splitlines()
			))
			self.client_connection.sendall(response)
		finally:
			self.client_connection.close()
