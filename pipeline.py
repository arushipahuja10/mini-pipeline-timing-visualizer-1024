from hazard import detect_hazard

class Pipeline:
    def __init__(self, instructions, forwarding=True):
        self.instructions = instructions
        self.forwarding = forwarding
        self.stages = [None] * 5  # IF ID EX MEM WB
        self.pc = 0
        self.cycle = 0
        self.completed = 0
        self.timeline = []
        self.stall_count = 0

    def step(self):

        self.cycle += 1

        # Check hazard between ID and EX/MEM
        stall = detect_hazard(
            self.stages[1],
            self.stages[2],
            self.stages[3],
            self.forwarding
        )

        if stall:
            self.stall_count += 1
            # Insert bubble in EX
            self.stages[4] = self.stages[3]
            self.stages[3] = self.stages[2]
            self.stages[2] = None
        else:
            self.stages[4] = self.stages[3]
            self.stages[3] = self.stages[2]
            self.stages[2] = self.stages[1]
            self.stages[1] = self.stages[0]

            if self.pc < len(self.instructions):
                self.stages[0] = self.instructions[self.pc]
                self.pc += 1
            else:
                self.stages[0] = None

        if self.stages[4]:
            self.completed += 1

        self.timeline.append(self.stages.copy())

    def run(self):
        while self.completed < len(self.instructions):
            self.step()

        return self.timeline