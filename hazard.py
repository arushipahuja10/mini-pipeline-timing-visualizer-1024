def detect_hazard(id_inst, ex_inst, mem_inst, forwarding):

    if id_inst is None:
        return False

    id_sources = id_inst.sources()

    # --- Check Load-Use Hazard ---
    if ex_inst and ex_inst.opcode == "LW":
        if ex_inst.destination() in id_sources:
            return True  # mandatory stall

    if not forwarding:
        # RAW hazard from EX
        if ex_inst and ex_inst.destination() in id_sources:
            return True

        # RAW hazard from MEM
        if mem_inst and mem_inst.destination() in id_sources:
            return True

    return False