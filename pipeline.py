from instruction import Instruction
from hazard_detection import detect_hazard

class Pipeline:
    def __init__(self, instructions_text, forwarding=True):
        # Convert raw text to Instruction objects
        self.instructions = [Instruction(text, i) for i, text in enumerate(instructions_text)]
        self.forwarding = forwarding
        self.pc = 0
        self.cycles = 0
        self.stalls = 0
        self.flushes = 0
        
        # Pipeline registers (The Latches)
        self.stages = {'IF': None, 'ID': None, 'EX': None, 'MEM': None, 'WB': None}
        
        # Grid holds the visualization data row-by-row for the HTML table
        self.grid = [[] for _ in self.instructions]
        
        # Logs track hardware events (Stalls, Flushes, Forwarding)
        self.logs = [] 

    def is_empty(self):
        """Check if all stages are empty and no more instructions are left to fetch."""
        return all(inst is None for inst in self.stages.values()) and self.pc >= len(self.instructions)

    def run(self):
        # Initial fetch to start the engine
        if self.pc < len(self.instructions):
            self.stages['IF'] = self.instructions[self.pc]
            self.pc += 1

        # Main Simulation Loop
        while not self.is_empty() and self.cycles < 100: # Safety break at 100 cycles
            self.cycles += 1
            
            # 1. Hazard Detection Logic
            # Check the current state of ID, EX, and MEM to see if we need to Stall or Flush
            stall, flush = detect_hazard(self.stages['ID'], self.stages['EX'], self.stages['MEM'], self.forwarding)

            # 2. Update the Visualization Grid
            for i, inst in enumerate(self.instructions):
                current_location = ""
                for stage_name in ['IF', 'ID', 'EX', 'MEM', 'WB']:
                    if self.stages[stage_name] == inst:
                        current_location = stage_name
                        break
                
                # Visual logic: If an instruction is stuck in ID, mark it as a STALL
                if current_location == 'ID' and len(self.grid[i]) > 0 and self.grid[i][-1] in ['ID', 'STALL']:
                    self.grid[i].append('STALL')
                else:
                    self.grid[i].append(current_location)

            # 3. Pipeline Register Shifting (The "Clock Tick")
            next_stages = {}

            # WB and MEM always move forward
            next_stages['WB'] = self.stages['MEM']
            next_stages['MEM'] = self.stages['EX']

            if stall:
                # DATA HAZARD: EX gets a bubble, ID and IF hold their current instructions
                self.stalls += 1
                next_stages['EX'] = Instruction("BUBBLE", -1)
                next_stages['ID'] = self.stages['ID']
                next_stages['IF'] = self.stages['IF']
                self.logs.append(f"Cycle {self.cycles}: 🛑 Data Hazard detected! Injecting bubble into EX.")
            
            elif flush:
                # CONTROL HAZARD: Branch is taken. EX moves to MEM, but ID and IF are cleared.
                self.flushes += 1
                next_stages['EX'] = self.stages['ID']
                next_stages['ID'] = Instruction("FLUSH", -1) # Flush the instruction in Decode
                
                # In a real MIPS CPU, a 'Taken' branch changes the PC. 
                # We simulate a "jump" by skipping the next instruction in the trace.
                if self.pc < len(self.instructions):
                    self.logs.append(f"Cycle {self.cycles}: 🌊 Branch Taken! Flushing '{self.instructions[self.pc].text}' from pipeline.")
                    self.pc += 1 # The "Jump" logic
                
                next_stages['IF'] = self.instructions[self.pc] if self.pc < len(self.instructions) else None
                if next_stages['IF']: self.pc += 1
            
            else:
                # NORMAL FLOW: Everything moves one step forward
                next_stages['EX'] = self.stages['ID']
                next_stages['ID'] = self.stages['IF']
                if self.pc < len(self.instructions):
                    next_stages['IF'] = self.instructions[self.pc]
                    self.pc += 1
                else:
                    next_stages['IF'] = None

            # Update actual stages for the next cycle
            self.stages = next_stages

        # Final cleanup for the grid (ensures all rows have the same length)
        for row in self.grid:
            while len(row) < self.cycles:
                row.append("")