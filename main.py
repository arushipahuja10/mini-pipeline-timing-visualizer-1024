import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pipeline import Pipeline
from html_visualizer import HTML_TEMPLATE

class RequestHandler(BaseHTTPRequestHandler):
    # Suppress default server logging to keep terminal clean
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        # Serve the HTML UI
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(HTML_TEMPLATE.encode('utf-8'))

    def do_POST(self):
        # Handle simulation request from the UI
        if self.path == '/simulate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request = json.loads(post_data)

            code_text = request.get('code', '')
            forwarding = request.get('forwarding', True)

            # Clean empty lines
            instructions = [line.strip() for line in code_text.split('\n') if line.strip()]

            # Run Simulation
            pipeline = Pipeline(instructions, forwarding)
            if instructions:
                pipeline.run()

            # Prepare data to send back to JS
            response = {
                'cycles': pipeline.cycles,
                'stalls': pipeline.stalls,
                'cpi': pipeline.cycles / len(instructions) if instructions else 0,
                'grid': pipeline.grid,
                'instructions': instructions
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

def main():
    port = 8000
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    
    print("="*50)
    print(f"🚀 MIPS Pipeline Server Running!")
    print(f"👉 Open your browser and go to: http://localhost:{port}")
    print("Press CTRL+C to stop the server.")
    print("="*50)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
        httpd.server_close()

if __name__ == "__main__":
    main()