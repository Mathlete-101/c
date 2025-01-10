import subprocess
import sys
import os

def attempt_4(command):
    """
    Run a shell command, stream the output (stdout and stderr) in real-time,
    and return the combined stdout + stderr result.
    
    Args:
        command (str): The shell command to run.
        
    Returns:
        str: The combined output of stdout and stderr.
    """
    combined_output = []  # List to store the output

    try:
        # Start the process
        process = subprocess.Popen(command, text=True, shell=True, stdin=sys.stdin, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)

        # Function to continuously read and output from stdout and stderr
        while True:
            # Read stdout and stderr in non-blocking mode
            stdout_char = os.read(process.stdout.fileno(), 1).decode('utf-8', errors="replace")  # Read 1 byte at a time

            if stdout_char:
                sys.stdout.write(stdout_char)
                sys.stdout.flush()  # Ensure immediate output
                combined_output.append(stdout_char)  # Store the output

            # Break if process has ended and there's no more output
            if stdout_char == '' and process.poll() is not None:
                break

    except KeyboardInterrupt:
        # Handle KeyboardInterrupt (Ctrl+C)
        print("\nProcess interrupted by user.")
        process.terminate()
        process.wait()
    
    # Combine the stdout and stderr outputs into a single string
    return ''.join(combined_output)

