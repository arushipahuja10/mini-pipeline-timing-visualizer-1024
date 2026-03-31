def detect_hazard(id_inst, ex_inst, mem_inst, forwarding_enabled):
    """
    Analyzes the current pipeline state to detect Data and Control hazards.
    Returns: (stall_required, flush_required)
    """
    # 1. Base Case: If ID is empty or a bubble, no hazard possible
    if not id_inst or id_inst.is_bubble:
        return False, False

    # Define source registers (RS, RT) and ignore R0/$zero as it's hardwired to 0
    srcs = [s for s in id_inst.srcs if s not in ['R0', '$0', '$zero', '0']]
    
    # --- DATA HAZARD SECTION ---
    
    # Check EX Stage for RAW (Read After Write) Hazards
    if ex_inst and not ex_inst.is_bubble and ex_inst.dest and ex_inst.dest in srcs:
        if not forwarding_enabled:
            # Without forwarding, any dependency on EX requires a stall
            return True, False
        else:
            # With forwarding, only a 'Load-Use' (LW followed by arithmetic) requires a stall
            if ex_inst.opcode == 'LW':
                return True, False 

    # Check MEM Stage for RAW Hazards
    if mem_inst and not mem_inst.is_bubble and mem_inst.dest and mem_inst.dest in srcs:
        if not forwarding_enabled:
            # Without forwarding, we must stall until WB finishes
            return True, False
        # Note: With forwarding, MEM -> EX bypass happens in hardware without a stall.

    # --- CONTROL HAZARD SECTION ---
    
    # Check for Branch Instructions (Control Hazards)
    # We simulate a "Branch Taken" scenario which requires a 1-cycle flush 
    # of the instruction currently being fetched (IF stage).
    if id_inst.opcode == 'BEQ':
        return False, True 

    return False, False