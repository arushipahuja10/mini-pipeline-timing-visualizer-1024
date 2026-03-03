def generate_html(timeline, instructions, total_cycles, stall_count, forwarding):

    html = """
    <html>
    <head>
    <style>
    body { font-family: Arial; background:#f4f6f8; padding:30px;}
    table { border-collapse: collapse; margin-top:20px;}
    th, td { border:1px solid #444; padding:8px; text-align:center;}
    th { background:#1e3d59; color:white;}
    .stall { background:#ffcccb;}
    </style>
    </head>
    <body>
    """

    html += f"<h1>Mini Pipeline Timing Visualizer</h1>"
    html += f"<h3>Forwarding: {'ON' if forwarding else 'OFF'}</h3>"
    html += f"<h3>Total Cycles: {total_cycles}</h3>"
    html += f"<h3>Total Stalls: {stall_count}</h3>"
    html += f"<h3>CPI: {round(total_cycles/len(instructions),2)}</h3>"

    html += "<table>"
    html += "<tr><th>Cycle</th><th>IF</th><th>ID</th><th>EX</th><th>MEM</th><th>WB</th></tr>"

    for i, state in enumerate(timeline):
        html += f"<tr><td>{i+1}</td>"
        for stage in state:
            if stage is None:
                html += "<td class='stall'>-</td>"
            else:
                html += f"<td>{stage}</td>"
        html += "</tr>"

    html += "</table></body></html>"

    with open("output.html", "w") as f:
        f.write(html)