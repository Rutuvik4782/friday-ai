"""
Reusable prompt templates registered with the MCP server.
"""


def register(mcp):

    @mcp.prompt()
    def summarize(text: str) -> str:
        """Prompt to summarize a block of text."""
        return f"Summarize the following text concisely:\n\n{text}"

    @mcp.prompt()
    def explain_code(code: str, language: str = "Python") -> str:
        """Prompt to explain a block of code."""
        return (
            f"Explain the following {language} code in plain English, "
            f"step by step:\n\n```{language.lower()}\n{code}\n```"
        )

    @mcp.prompt()
    def review_code(code: str, language: str = "Python") -> str:
        """Prompt to review code for bugs, performance issues, and best practices."""
        return (
            f"Review the following {language} code. Identify bugs, "
            f"performance issues, and suggest improvements:\n\n```{language.lower()}\n{code}\n```"
        )

    @mcp.prompt()
    def translate_text(text: str, target_language: str = "English") -> str:
        """Prompt to translate text to a target language."""
        return f"Translate the following text to {target_language}:\n\n{text}"
