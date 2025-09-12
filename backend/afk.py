import subprocess

def run_commands(frequency, month):
    base_command = ["python3", "script.py", "US", "CanSIPS-IC3"]

    start = 0.5
    end = 11.5
    step = 1.0

    value = start
    while value <= end:
        value_str = f"{value:.1f}"
        command = base_command + [value_str, frequency, month]
        print("Running command:", " ".join(command))
        subprocess.run(command)
        value += step

# First loop: seasonal, Jan-Mar
run_commands("seasonal", "Jan-Mar")

# Second loop: monthly, Jan
run_commands("monthly", "Jan")
