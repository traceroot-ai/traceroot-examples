import os
import subprocess
import tempfile

class ExecutionAgent:
    def execute_code(self, code: str, timeout: int = 60) -> dict:
        """
        Executes the given Python code in a temporary file and returns execution results.
        """
        # Sanitize generated code to remove markdown fences
        clean_lines = []
        for line in code.splitlines():
            # Skip any markdown fence markers
            if line.strip().startswith('```'):
                continue
            clean_lines.append(line)
        sanitized_code = "\n".join(clean_lines)

        # Create temporary file for code execution
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
            tmp.write(sanitized_code)
            tmp_filename = tmp.name

        try:
            # Run the temp file using subprocess
            proc = subprocess.run(
                ['python', tmp_filename],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                check=False,
                text=True
            )

            return {
                'success': proc.returncode == 0,
                'stdout': proc.stdout,
                'stderr': proc.stderr,
                'return_code': proc.returncode
            }
        finally:
            try:
                os.remove(tmp_filename)
            except OSError:
                pass
