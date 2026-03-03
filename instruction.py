class Instruction:
    def __init__(self, opcode, rd=None, rs=None, rt=None, imm=None):
        self.opcode = opcode
        self.rd = rd
        self.rs = rs
        self.rt = rt
        self.imm = imm

    def sources(self):
        if self.opcode in ["ADD", "SUB", "BEQ"]:
            return [self.rs, self.rt]
        if self.opcode == "LW":
            return [self.rs]
        if self.opcode == "SW":
            return [self.rs, self.rt]
        return []

    def destination(self):
        if self.opcode in ["ADD", "SUB", "LW"]:
            return self.rd
        return None

    def __str__(self):
        if self.opcode in ["ADD", "SUB"]:
            return f"{self.opcode} {self.rd},{self.rs},{self.rt}"
        if self.opcode == "LW":
            return f"LW {self.rd},0({self.rs})"
        if self.opcode == "SW":
            return f"SW {self.rt},0({self.rs})"
        if self.opcode == "BEQ":
            return f"BEQ {self.rs},{self.rt}"
        return self.opcode