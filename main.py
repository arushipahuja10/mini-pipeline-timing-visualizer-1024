import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pipeline import Pipeline
from html_visualizer import HTML_TEMPLATE

class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Keep the console clean for a professional look during the demo
        pass 

    def do_GET(self):
        # Serve the Visualizer UI
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(HTML_TEMPLATE.encode('utf-8'))

    def do_POST(self):
        # Handle the Simulation logic
        if self.path == '/simulate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request = json.loads(post_data)

            # Extract user input
            code_text = request.get('code', '')
            forwarding = request.get('forwarding', True)

            # Parse lines into a list of strings
            instructions_list = [line.strip() for line in code_text.split('\n') if line.strip()]

            # Initialize and Run the Pipeline
            pipeline = Pipeline(instructions_list, forwarding)
            if instructions_list:
                pipeline.run()

            # Calculate Performance Metrics for the "100/100" Case Study
            num_inst = len(instructions_list)
            cpi = pipeline.cycles / num_inst if num_inst > 0 else 0
            
            # Generate the JSON Response
            response = {
                'cycles': pipeline.cycles,
                'stalls': pipeline.stalls,
                'flushes': pipeline.flushes,
                'cpi': cpi,
                'instructions': instructions_list,
                'grid': pipeline.grid,
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
    
    print("="*65)
    print(f"🚀 ADVANCED MIPS PIPELINE SIMULATOR ACTIVE")
    print(f"🔗 URL: http://localhost:{port}")
    print("="*65)
    print("Status: Monitoring for hazard detection requests...")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Server shutting down safely.")
        httpd.server_close()

if __name__ == "__main__":
    main()