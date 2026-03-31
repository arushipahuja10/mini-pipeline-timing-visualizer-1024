HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced MIPS Pipeline Visualizer Pro</title>
    <style>
        :root {
            --primary: #2c3e50;
            --accent: #3498db;
            --stall: #f3f3f3;
            --flush: #ffebee;
            --text: #333;
        }
        body { font-family: 'Segoe UI', system-ui, sans-serif; margin: 0; background-color: #f8f9fa; color: var(--text); display: flex; flex-direction: column; align-items: center; }
        
        /* Layout */
        .container { width: 95%; max-width: 1300px; padding: 20px; }
        .header { text-align: left; margin-bottom: 30px; border-bottom: 3px solid var(--primary); width: 100%; }
        .main-layout { display: grid; grid-template-columns: 320px 1fr; gap: 25px; align-items: start; }
        
        /* Controls & Dashboard */
        .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin-bottom: 20px; }
        h3 { margin-top: 0; color: var(--primary); font-size: 1.1rem; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        
        textarea { width: 100%; height: 150px; font-family: 'Cascadia Code', monospace; font-size: 13px; padding: 12px; border: 1px solid #ddd; border-radius: 8px; resize: none; box-sizing: border-box; }
        button { background: var(--primary); color: white; border: none; padding: 12px; border-radius: 6px; width: 100%; font-weight: 600; cursor: pointer; transition: 0.2s; margin-top: 10px; }
        button:hover { background: var(--accent); transform: translateY(-1px); }
        .secondary-btn { background: #e0e0e0; color: #444; margin-top: 8px; }

        /* Metrics Grid */
        .metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px; }
        .metric-item { background: #f1f4f8; padding: 10px; border-radius: 8px; text-align: center; }
        .metric-value { display: block; font-size: 1.4rem; font-weight: 800; color: var(--primary); }
        .metric-label { font-size: 0.7rem; text-transform: uppercase; color: #7f8c8d; letter-spacing: 1px; }

        /* Visualization Table */
        .viz-scroll { overflow-x: auto; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
        table { border-collapse: separate; border-spacing: 4px; width: 100%; }
        th { font-weight: 600; color: #7f8c8d; padding: 10px; font-size: 0.8rem; }
        .inst-cell { text-align: right; font-family: monospace; padding-right: 15px; border-right: 2px solid #eee; min-width: 150px; }
        
        /* Stage Colors */
        .stage { padding: 10px; border-radius: 4px; font-weight: bold; font-size: 0.85rem; text-align: center; min-width: 45px; transition: 0.3s; }
        .IF { background: #FFE0B2; color: #E65100; }
        .ID { background: #C8E6C9; color: #1B5E20; }
        .EX { background: #BBDEFB; color: #0D47A1; }
        .MEM { background: #F8BBD0; color: #880E4F; }
        .WB { background: #E1BEE7; color: #4A148C; }
        .STALL { background: #EEEEEE; color: #9E9E9E; border: 1px dashed #BDBDBD; }
        .FLUSH { background: #FFCDD2; color: #B71C1C; text-decoration: line-through; opacity: 0.7; }

        /* Animation */
        @keyframes slideIn { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: translateX(0); } }
        .animate { animation: slideIn 0.4s ease forwards; }

        /* Log */
        .log { margin-top: 20px; font-family: monospace; font-size: 0.9rem; max-height: 200px; overflow-y: auto; background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 8px; }
        .log-entry { margin-bottom: 5px; border-left: 3px solid var(--accent); padding-left: 10px; }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <h1>Architecture Lab: Pipeline Timing Visualizer</h1>
        <p style="color: #666; margin-top: -10px;">Diagnostic Tool for Structural, Data, and Control Hazards</p>
    </div>

    <div class="main-layout">
        <aside>
            <div class="card">
                <h3>System Configuration</h3>
                <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                    <span>Data Forwarding</span>
                    <input type="checkbox" id="forwarding-toggle" checked>
                </div>
                <textarea id="code-input">
LW R1, 0(R2)
ADD R3, R1, R4
BEQ R3, R0, 2
SUB R6, R2, R7
ADD R8, R6, R3</textarea>
                <button onclick="simulate()">Generate Timing Diagram</button>
                <button class="secondary-btn" onclick="document.getElementById('code-input').value=''">Clear Trace</button>
            </div>

            <div class="card" id="metrics-panel" style="display:none;">
                <h3>Performance Analysis</h3>
                <div class="metrics-grid">
                    <div class="metric-item"><span class="metric-value" id="m-cycles">-</span><span class="metric-label">Cycles</span></div>
                    <div class="metric-item"><span class="metric-value" id="m-cpi">-</span><span class="metric-label">CPI</span></div>
                    <div class="metric-item"><span class="metric-value" id="m-stalls">-</span><span class="metric-label">Stalls</span></div>
                    <div class="metric-item"><span class="metric-value" id="m-flushes">-</span><span class="metric-label">Flushes</span></div>
                </div>
            </div>
        </aside>

        <main>
            <div class="viz-scroll" id="viz-container">
                <div style="padding: 100px; text-align: center; color: #aaa;">
                    <p>Waiting for Instruction Trace...</p>
                </div>
            </div>
            
            <div id="log-container"></div>
        </main>
    </div>
</div>

<script>
    async function simulate() {
        const code = document.getElementById('code-input').value;
        const forwarding = document.getElementById('forwarding-toggle').checked;
        
        try {
            const response = await fetch('/simulate', {
                method: 'POST',
                body: JSON.stringify({ code: code, forwarding: forwarding }),
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();
            updateMetrics(data);
            renderGrid(data);
        } catch (e) {
            alert("Connection to Python Backend Failed!");
        }
    }

    function updateMetrics(data) {
        document.getElementById('metrics-panel').style.display = 'block';
        document.getElementById('m-cycles').innerText = data.cycles;
        document.getElementById('m-cpi').innerText = data.cpi.toFixed(2);
        document.getElementById('m-stalls').innerText = data.stalls;
        document.getElementById('m-flushes').innerText = data.flushes;
    }

    function renderGrid(data) {
        const container = document.getElementById('viz-container');
        let html = `<table><thead><tr><th>Instruction Trace</th>`;
        for(let i=1; i<=data.cycles; i++) html += `<th>CC ${i}</th>`;
        html += `</tr></thead><tbody>`;

        data.instructions.forEach((inst, i) => {
            html += `<tr><td class="inst-cell"><strong>I${i+1}:</strong> ${inst}</td>`;
            data.grid[i].forEach((stage, cycleIdx) => {
                const content = stage || "";
                const delay = (cycleIdx * 0.05).toFixed(2);
                html += `<td><div class="stage ${content} animate" style="animation-delay: ${delay}s">${content}</div></td>`;
            });
            html += `</tr>`;
        });

        html += `</tbody></table>`;
        container.innerHTML = html;

        // Render Logs
        let logHtml = `<div class="log"><h3>Hardware Event Log</h3>`;
        data.logs.forEach(msg => {
            logHtml += `<div class="log-entry">> ${msg}</div>`;
        });
        logHtml += `</div>`;
        document.getElementById('log-container').innerHTML = logHtml;
    }
</script>
</body>
</html>
"""