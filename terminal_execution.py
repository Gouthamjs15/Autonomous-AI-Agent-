import subprocess

def run_terminal_command(command: str) -> dict:
    """
    Executes a shell command safely and returns the output or error.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60  # optional safeguard
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode
        }

    except subprocess.TimeoutExpired as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Command timed out: {str(e)}",
            "exit_code": -1
        }

    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Execution failed: {str(e)}",
            "exit_code": -1
        }
