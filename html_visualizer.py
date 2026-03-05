HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Interactive Pipeline Visualizer</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background-color: #f4f6f9; color: #333; display: flex; flex-direction: column; align-items: center; }
        .header-container { display: flex; justify-content: space-between; width: 95%; max-width: 1200px; margin-bottom: 20px; }
        .title { margin: 0; border-bottom: 2px solid #4b8b94; padding-bottom: 10px;}
        
        .main-content { display: flex; gap: 20px; width: 95%; max-width: 1200px; align-items: flex-start; }
        .controls { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); flex: 0 0 300px; }
        .visualization { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); flex: 1; overflow-x: auto; }
        
        textarea { width: 100%; height: 120px; font-family: monospace; font-size: 14px; padding: 10px; box-sizing: border-box; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 4px; resize: vertical;}
        button { background-color: #4b8b94; color: white; border: none; padding: 10px 15px; cursor: pointer; border-radius: 4px; width: 100%; font-size: 16px; font-weight: bold; transition: background 0.2s; }
        button:hover { background-color: #3a6f76; }
        .clear-btn { background-color: #f0f0f0; color: #333; margin-top: 10px; font-weight: normal; }
        .clear-btn:hover { background-color: #e0e0e0; }
        
        .toggle-container { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #eee; }
        .switch { position: relative; display: inline-block; width: 50px; height: 24px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; transition: .4s; border-radius: 24px; }
        .slider:before { position: absolute; content: ""; height: 16px; width: 16px; left: 4px; bottom: 4px; background-color: white; transition: .4s; border-radius: 50%; }
        input:checked + .slider { background-color: #4CAF50; }
        input:checked + .slider:before { transform: translateX(26px); }

        table { border-collapse: collapse; text-align: center; font-size: 14px; margin-top: 10px; width: 100%;}
        th, td { padding: 8px 12px; min-width: 40px; border: none; }
        .clock-row th { border-bottom: 2px solid #333; position: relative; font-weight: normal; }
        .clock-pulse { width: 100%; height: 15px; border-top: 2px solid #000; border-right: 2px solid #000; border-left: 2px solid #000; margin-bottom: 5px; box-sizing: border-box; border-bottom: none;}
        .inst-col { text-align: right; font-weight: bold; border-right: 2px solid transparent; padding-right: 20px; white-space: nowrap; font-family: monospace; }
        
        .stage-IF { background-color: #ffcc99; color: #000; }
        .stage-ID { background-color: #cce5cc; color: #000; }
        .stage-EX { background-color: #cce5ff; color: #000; }
        .stage-MEM { background-color: #ffcccc; color: #000; }
        .stage-WB { background-color: #e5ccff; color: #000; }
        .stage-STALL { background-color: #f0f0f0; color: #999; font-style: italic; border: 1px dashed #ccc; }
        .stage-empty { background-color: transparent; }
        
        .metrics { display: flex; gap: 20px; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 15px;}
        .metric-box { text-align: center; flex: 1;}
        .metric-box span { font-size: 20px; font-weight: bold; display: block; color: #2c3e50; }
        .metric-label { font-size: 12px; color: #7f8c8d; text-transform: uppercase; }

        /* Cell Animation */
        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.9); }
            to { opacity: 1; transform: scale(1); }
        }
        .animated-cell { animation: fadeIn 0.3s ease-out forwards; opacity: 0; }
        
        /* Event Log Styling */
        .log-container { margin-top: 25px; padding: 15px; background: #fff8e1; border-left: 5px solid #ffb300; border-radius: 4px; font-family: monospace; font-size: 14px;}
        .log-container h3 { margin-top: 0; font-family: 'Segoe UI', sans-serif; font-size: 16px; color: #333; margin-bottom: 10px;}
        .log-container ul { margin: 0; padding-left: 20px; }
        .log-container li { margin-bottom: 5px; }
    </style>
</head>
<body>

    <div class="header-container">
        <h1 class="title">Instruction Execution In 5-Stage Pipeline</h1>
    </div>

    <div class="main-content">
        <div class="controls">
            <div class="toggle-container">
                <strong>Data Forwarding</strong>
                <label class="switch">
                    <input type="checkbox" id="forwarding-toggle" checked>
                    <span class="slider"></span>
                </label>
            </div>
            
            <label for="code-input"><strong>MIPS Code / Query Input:</strong></label>
            <textarea id="code-input">
LW R1 R2
ADD R3 R1 R4
SW R3 R5
SUB R6 R2 R7
ADD R8 R6 R3</textarea>
            
            <button onclick="simulate()">Submit Code for Simulation</button>
            <button class="clear-btn" onclick="document.getElementById('code-input').value=''">Clear Input</button>
        </div>

        <div class="visualization" id="viz-container">
            <div style="text-align:center; color:#888; margin-top:50px;">
                Enter code and click "Submit Code for Simulation"
            </div>
        </div>
    </div>

    <script>
        async function simulate() {
            const code = document.getElementById('code-input').value;
            const forwarding = document.getElementById('forwarding-toggle').checked;
            
            const response = await fetch('/simulate', {
                method: 'POST',
                body: JSON.stringify({ code: code, forwarding: forwarding }),
                headers: { 'Content-Type': 'application/json' }
            });
            
            const data = await response.json();
            renderVisualization(data);
        }

        function renderVisualization(data) {
            const container = document.getElementById('viz-container');
            if(data.instructions.length === 0) {
                container.innerHTML = "<p>Please enter instructions.</p>"; return;
            }

            let html = `
                <div class="metrics">
                    <div class="metric-box"><span class="metric-label">Total Cycles</span><span>${data.cycles}</span></div>
                    <div class="metric-box"><span class="metric-label">Stalls</span><span>${data.stalls}</span></div>
                    <div class="metric-box"><span class="metric-label">CPI</span><span>${data.cpi.toFixed(2)}</span></div>
                </div>
                <table>
                    <tr class="clock-row">
                        <th class="inst-col" style="vertical-align: bottom;">Execution<br>Clock</th>
            `;
            
            for(let i = 1; i <= data.cycles; i++) {
                html += `<th><div class="clock-pulse"></div>${i}</th>`;
            }
            html += `</tr>`;

            data.instructions.forEach((inst, index) => {
                html += `<tr><td class="inst-col">Instruction ${index + 1}<br><span style="font-size:11px; color:#666;">${inst}</span></td>`;
                const rowGrid = data.grid[index];
                
                for(let i = 0; i < data.cycles; i++) {
                    const stage = i < rowGrid.length ? rowGrid[i] : "";
                    if(stage) {
                        const cssClass = stage === "STALL" ? "stage-STALL" : `stage-${stage}`;
                        const displayTxt = stage === "STALL" ? "STALL" : stage;
                        const delay = (i * 0.1).toFixed(2); // Stagger animation by column
                        html += `<td class="${cssClass} animated-cell" style="animation-delay: ${delay}s">${displayTxt}</td>`;
                    } else {
                        html += `<td class="stage-empty"></td>`;
                    }
                }
                html += `</tr>`;
            });

            html += `</table>`;

            // Render Event Log
            if (data.logs && data.logs.length > 0) {
                html += `<div class="log-container"><h3>📋 Simulation Event Log</h3><ul>`;
                data.logs.forEach(log => {
                    html += `<li>${log}</li>`;
                });
                html += `</ul></div>`;
            } else if (data.instructions.length > 0) {
                html += `<div class="log-container" style="background: #e8f5e9; border-left-color: #4caf50;">
                            <h3>📋 Simulation Event Log</h3><p>✅ Perfect execution. No hazards or stalls detected!</p>
                         </div>`;
            }

            container.innerHTML = html;
        }
        
        window.onload = simulate;
    </script>
</body>
</html>
"""