class Instruction:
    def __init__(self, text, inst_id):
        self.text = text
        self.id = inst_id
        self.opcode = ""
        self.dest = None
        self.srcs = []
        self.is_bubble = False
        self.is_flush = False
        self.type = "Unknown"  # Used for the Instruction Mix Analysis

        if text == "BUBBLE":
            self.is_bubble = True
            self.opcode = "STALL"
        elif text == "FLUSH":
            self.is_flush = True
            self.is_bubble = True
            self.opcode = "FLUSH"
        elif text:
            # Clean up the input: remove commas and extra spaces
            parts = text.replace(',', ' ').split()
            if not parts:
                return
                
            self.opcode = parts[0].upper()
            
            # 1. Arithmetic/Logic (R-Type)
            if self.opcode in ['ADD', 'SUB', 'AND', 'OR', 'XOR']:
                self.type = "Arithmetic"
                if len(parts) >= 4:
                    self.dest = parts[1]
                    self.srcs = [parts[2], parts[3]]
            
            # 2. Load Word (I-Type)
            elif self.opcode == 'LW':
                self.type = "Memory"
                if len(parts) >= 3:
                    self.dest = parts[1]
                    # Handle format like LW R1, 0(R2)
                    raw_src = parts[2]
                    if '(' in raw_src:
                        base_reg = raw_src[raw_src.find('(')+1 : raw_src.find(')')]
                        self.srcs = [base_reg]
                    else:
                        self.srcs = [parts[2]]

            # 3. Store Word (I-Type)
            elif self.opcode == 'SW':
                self.type = "Memory"
                if len(parts) >= 3:
                    self.dest = None # SW doesn't write to a register
                    # SW R1, 0(R2) -> uses both R1 and R2
                    self.srcs = [parts[1]] 
                    raw_src = parts[2]
                    if '(' in raw_src:
                        base_reg = raw_src[raw_src.find('(')+1 : raw_src.find(')')]
                        self.srcs.append(base_reg)
                    else:
                        self.srcs.append(parts[2])

            # 4. Branch (Control-Type)
            elif self.opcode == 'BEQ' or self.opcode == 'BNE':
                self.type = "Control"
                if len(parts) >= 3:
                    self.dest = None
                    self.srcs = [parts[1], parts[2]]

    def __repr__(self):
        return f"[{self.opcode}]" if not self.is_bubble else "[---]"