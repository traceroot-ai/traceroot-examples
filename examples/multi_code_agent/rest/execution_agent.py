import logging
import os
from tempfile import NamedTemporaryFile

logger = logging.getLogger(__name__)


def execute_code(code_str: str, namespace: dict):
    """
    Execute dynamically generated code within the given namespace.
    Syntax errors are caught at compile time for clearer debugging.
    """
    # Sanitize code: remove Markdown fences and lines with backticks to avoid syntax errors
    lines = code_str.splitlines()
    filtered = [
        line for line in lines
        if not line.strip().startswith("```") and "`" not in line
    ]
    clean_code = "\n".join(filtered)

    # Write sanitized code to a temporary file
    with NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
        temp_file.write(clean_code.encode('utf-8'))
        temp_file_name = temp_file.name

    try:
        # Read back the code for execution
        with open(temp_file_name) as f:
            code = f.read()

        # Compile first to catch syntax errors
        try:
            compiled_code = compile(code, temp_file_name, 'exec')
        except SyntaxError as se:
            logger.error(
                f"Syntax error in generated code at {temp_file_name}: {se}")
            raise

        # Execute the compiled code
        exec(compiled_code, namespace)

    except Exception as e:
        logger.error(f"Error executing code: {e}")
        raise

    finally:
        # Cleanup temp file
        if os.path.exists(temp_file_name):
            os.unlink(temp_file_name)
