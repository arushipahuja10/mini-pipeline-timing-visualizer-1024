class Instruction:
    def __init__(self, text, inst_id):
        self.text = text
        self.id = inst_id
        self.opcode = ""
        self.dest = None
        self.srcs = []
        self.is_bubble = False
        
        if text == "BUBBLE":
            self.is_bubble = True
        elif text:
            # Normalize commas and split
            parts = text.replace(',', ' ').split()
            if not parts:
                return
                
            self.opcode = parts[0].upper()
            
            # Parse based on opcode format
            if self.opcode in ['ADD', 'SUB']:
                self.dest = parts[1]
                self.srcs = [parts[2], parts[3]]
            elif self.opcode == 'LW':
                self.dest = parts[1]
                self.srcs = [parts[2]]
            elif self.opcode == 'SW':
                self.dest = None
                self.srcs = [parts[1], parts[2]]
            elif self.opcode == 'BEQ':
                self.dest = None
                self.srcs = [parts[1], parts[2]]