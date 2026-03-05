from instruction import Instruction
from hazard_detection import detect_hazard

class Pipeline:
    def __init__(self, instructions_text, forwarding=True):
        self.instructions = [Instruction(text, i) for i, text in enumerate(instructions_text)]
        self.forwarding = forwarding
        self.pc = 0
        self.cycles = 0
        self.stalls = 0
        
        # Pipeline registers
        self.stages = {'IF': None, 'ID': None, 'EX': None, 'MEM': None, 'WB': None}
        
        # Grid holds the visualization data row-by-row
        self.grid = [[] for _ in self.instructions]
        
        # Logs track exactly why stalls happen
        self.logs = [] 

    def is_empty(self):
        return all(inst is None for inst in self.stages.values()) and self.pc >= len(self.instructions)

    def run(self):
        # Initial fetch
        if self.pc < len(self.instructions):
            self.stages['IF'] = self.instructions[self.pc]
            self.pc += 1

        while not self.is_empty():
            self.cycles += 1
            
            # Check for hazards before moving instructions
            stall = detect_hazard(self.stages['ID'], self.stages['EX'], self.stages['MEM'], self.forwarding)

            # --- Event Logging ---
            id_inst = self.stages['ID']
            if stall and id_inst:
                if self.forwarding:
                    self.logs.append(f"Cycle {self.cycles}: ⚠️ Load-Use Hazard! Stalled '{id_inst.text}' to wait for memory fetch.")
                else:
                    self.logs.append(f"Cycle {self.cycles}: 🛑 RAW Hazard! Stalled '{id_inst.text}' to wait for Write Back.")
            # ---------------------

            # Record the state of each instruction for the current cycle
            for i, inst in enumerate(self.instructions):
                current_stage = ""
                for stage_name in ['IF', 'ID', 'EX', 'MEM', 'WB']:
                    if self.stages[stage_name] == inst:
                        current_stage = stage_name
                        break
                
                # Logic to print STALL or repeat IF visually on the grid
                if current_stage == 'ID' and len(self.grid[i]) > 0 and self.grid[i][-1] in ['ID', 'STALL']:
                    self.grid[i].append('STALL')
                elif current_stage == 'IF' and len(self.grid[i]) > 0 and self.grid[i][-1] == 'IF':
                    self.grid[i].append('IF')
                else:
                    self.grid[i].append(current_stage)

            # Shift stages (bottom-up to avoid overwriting)
            next_stages = {}
            next_stages['WB'] = self.stages['MEM']
            next_stages['MEM'] = self.stages['EX']

            if stall:
                next_stages['EX'] = Instruction("BUBBLE", -1)
                next_stages['ID'] = self.stages['ID']
                next_stages['IF'] = self.stages['IF']
                self.stalls += 1
            else:
                next_stages['EX'] = self.stages['ID']
                next_stages['ID'] = self.stages['IF']
                if self.pc < len(self.instructions):
                    next_stages['IF'] = self.instructions[self.pc]
                    self.pc += 1
                else:
                    next_stages['IF'] = None

            self.stages = next_stages