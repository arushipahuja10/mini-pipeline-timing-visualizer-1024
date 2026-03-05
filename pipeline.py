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
        
        # grid[instruction_index] = list of stages per cycle (e.g., ['', 'IF', 'ID', 'STALL', 'EX'...])
        self.grid = [[] for _ in self.instructions]

    def is_empty(self):
        return all(inst is None for inst in self.stages.values()) and self.pc >= len(self.instructions)

    def run(self):
        # Initial fetch
        if self.pc < len(self.instructions):
            self.stages['IF'] = self.instructions[self.pc]
            self.pc += 1

        while not self.is_empty():
            self.cycles += 1
            stall = detect_hazard(self.stages['ID'], self.stages['EX'], self.stages['MEM'], self.forwarding)

            # Record the state of each instruction for the current cycle
            for i, inst in enumerate(self.instructions):
                current_stage = ""
                for stage_name in ['IF', 'ID', 'EX', 'MEM', 'WB']:
                    if self.stages[stage_name] == inst:
                        current_stage = stage_name
                        break
                
                # If instruction is stuck in ID due to a stall, mark as STALL
                if current_stage == 'ID' and len(self.grid[i]) > 0 and self.grid[i][-1] in ['ID', 'STALL']:
                    self.grid[i].append('STALL')
                # If instruction is stuck in IF due to ID stall, just repeat IF
                elif current_stage == 'IF' and len(self.grid[i]) > 0 and self.grid[i][-1] == 'IF':
                    self.grid[i].append('IF')
                else:
                    self.grid[i].append(current_stage)

            # Shift stages
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