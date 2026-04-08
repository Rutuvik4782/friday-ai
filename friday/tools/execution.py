"""
Code execution tool — run Python code snippets safely and return output.
"""

import subprocess
import sys
import io
import contextlib
import traceback
import re


def register(mcp):

    @mcp.tool()
    async def execute_code(code: str, language: str = "python") -> str:
        """
        Execute a code snippet and return stdout/stderr output.
        WARNING: Only safe for sandboxed/development environments.
        Supports: python
        """
        if language.lower() != "python":
            return f"Language '{language}' is not supported. Only Python is available."

        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()

        safe_globals = {
            "__builtins__": {
                "print": print,
                "len": len,
                "range": range,
                "str": str,
                "int": int,
                "float": float,
                "list": list,
                "dict": dict,
                "set": set,
                "tuple": tuple,
                "bool": bool,
                "abs": abs,
                "min": min,
                "max": max,
                "sum": sum,
                "sorted": sorted,
                "reversed": reversed,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
                "any": any,
                "all": all,
                "round": round,
                "open": None,
                "__import__": None,
            }
        }

        unsafe_patterns = [
            r"import\s+os\b",
            r"from\s+os\b",
            r"import\s+subprocess",
            r"from\s+subprocess",
            r"import\s+sys\b",
            r"from\s+sys\b",
            r"open\s*\(",
            r"__import__",
            r"eval\s*\(",
            r"exec\s*\(",
            r"os\.",
            r"subprocess\.",
            r"sys\.",
            r"pip\s",
            r"curl\s",
            r"wget\s",
            r"requests\.",
            r"urllib\.",
            r"socket\.",
            r"\.send\(",
            r"\.connect\(",
            r"ctypes\.",
        ]
        for pattern in unsafe_patterns:
            if re.search(pattern, code):
                return "Blocked: this code pattern is not allowed for safety reasons."

        try:
            with (
                contextlib.redirect_stdout(stdout_buf),
                contextlib.redirect_stderr(stderr_buf),
            ):
                exec(compile(code, "<friday>", "exec"), safe_globals)

            out = stdout_buf.getvalue()
            err = stderr_buf.getvalue()

            result = []
            if out:
                result.append(f"STDOUT:\n{out.rstrip()}")
            if err:
                result.append(f"STDERR:\n{err.rstrip()}")
            if not out and not err:
                result.append(
                    "(No output — code ran successfully with no print statements)"
                )

            return "\n".join(result)

        except Exception:
            tb = traceback.format_exc()
            return f"Error executing code:\n{tb}"
