def detect_hazard(id_inst, ex_inst, mem_inst, forwarding_enabled):
    if not id_inst or id_inst.is_bubble:
        return False

    srcs = id_inst.srcs
    if not srcs:
        return False

    # Ignore hazards for hardwired zero registers if used
    srcs = [s for s in srcs if s not in ['R0', '$0', '$zero']]

    # 1. EX Stage Hazards
    if ex_inst and not ex_inst.is_bubble and ex_inst.dest and ex_inst.dest in srcs:
        if not forwarding_enabled:
            return True # RAW hazard -> stall
        else:
            if ex_inst.opcode == 'LW':
                return True # Load-use hazard -> 1 stall cycle required

    # 2. MEM Stage Hazards
    if mem_inst and not mem_inst.is_bubble and mem_inst.dest and mem_inst.dest in srcs:
        if not forwarding_enabled:
            return True # RAW hazard -> stall

    return False