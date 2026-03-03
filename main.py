from instruction import Instruction
from pipeline import Pipeline
from html_generator import generate_html

# ---- Sample Program ----
instructions = [
    Instruction("LW", rd="R1", rs="R2"),
    Instruction("ADD", rd="R3", rs="R1", rt="R4"),
    Instruction("SUB", rd="R5", rs="R3", rt="R6"),
    Instruction("ADD", rd="R7", rs="R5", rt="R8"),
]

forwarding = True   # Change to False to compare

pipeline = Pipeline(instructions, forwarding)
timeline = pipeline.run()

generate_html(
    timeline,
    instructions,
    pipeline.cycle,
    pipeline.stall_count,
    forwarding
)

print("Simulation complete. Open output.html in browser.")