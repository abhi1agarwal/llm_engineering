import argparse
import sys
from .summarizer import summarize_website
from .parser import Website # Though not directly used by CLI, good to ensure it's importable if CLI logic expands

def main():
    """
    Main function to handle command-line arguments for website summarization.
    """
    parser = argparse.ArgumentParser(
        description="Summarize a website using OpenAI's GPT model.",
        formatter_class=argparse.RawTextHelpFormatter # For better help text formatting
    )
    parser.add_argument(
        "url", 
        help="The URL of the website to summarize."
    )
    parser.add_argument(
        "-o", "--output", 
        help="Optional. The file path to save the Markdown summary. If not provided, prints to console.",
        default=None
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s 0.1.0", # A simple version for now
        help="Show program's version number and exit."
    )

    # Check if any arguments were passed (other than script name)
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    print(f"CLI: Requesting summary for URL: {args.url}")
    if args.output:
        print(f"CLI: Output will be saved to: {args.output}")

    summary = summarize_website(url=args.url, output_file=args.output)

    if summary:
        if not args.output: # If no output file was specified, print to console
            print("\n--- Summary ---")
            print(summary)
            print("--- End of Summary ---")
        else:
            # summarize_website already prints a confirmation if output_file is provided
            pass 
        print("CLI: Summarization process completed.")
    else:
        print("CLI: Failed to generate summary.")
        sys.exit(1) # Exit with an error code if summarization failed

if __name__ == "__main__":
    main() 