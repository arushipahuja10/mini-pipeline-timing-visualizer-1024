import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pipeline import Pipeline
from html_visualizer import HTML_TEMPLATE

class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass # Keep console output clean

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(HTML_TEMPLATE.encode('utf-8'))

    def do_POST(self):
        if self.path == '/simulate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request = json.loads(post_data)

            code_text = request.get('code', '')
            forwarding = request.get('forwarding', True)

            instructions = [line.strip() for line in code_text.split('\n') if line.strip()]

            pipeline = Pipeline(instructions, forwarding)
            if instructions:
                pipeline.run()

            response = {
                'cycles': pipeline.cycles,
                'stalls': pipeline.stalls,
                'cpi': pipeline.cycles / len(instructions) if instructions else 0,
                'grid': pipeline.grid,
                'instructions': instructions,
                'logs': pipeline.logs
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

def main():
    port = 8000
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    
    print("="*60)
    print(f"🚀 MIPS Pipeline Interactive Server Running!")
    print(f"👉 Open your browser and go to: http://localhost:{port}")
    print("Press CTRL+C to stop the server.")
    print("="*60)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
        httpd.server_close()

if __name__ == "__main__":
    main()