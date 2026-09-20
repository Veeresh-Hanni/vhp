"""Top-level package for the Veeresh Hanni Project."""

__all__ = ["__version__", "main"]
__version__ = "0.1.0"


def main() -> None:
    """Run the small command-line entry point installed by the package."""
    print(f"Hello from vhp {__version__}!")
