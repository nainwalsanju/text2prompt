"""Entry point for text2prompt."""

import sys
from text2prompt.app import run_app


def main():
    """Main entry point."""
    run_app(sys.argv[1:])


if __name__ == "__main__":
    main()
