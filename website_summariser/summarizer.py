import os
from dotenv import load_dotenv
from openai import OpenAI
from .parser import Website # Relative import for the Website class

# Load environment variables
load_dotenv(override=True)

def get_openai_client():
    """
    Initializes and returns an OpenAI client.
    Checks for the API key and prints appropriate messages.
    Returns:
        OpenAI client instance or None if API key is invalid.
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("No API key was found. Please set the OPENAI_API_KEY environment variable.")
        return None
    if not api_key.startswith("sk-proj-"):
        # Updated this message to be more informative as it's a common pitfall
        print("Warning: Your OpenAI API key does not start with 'sk-proj-'. "
              "This might indicate you are using an old key format or a personal key instead of a project-specific key. "
              "Please ensure you are using a valid Project API key from your OpenAI dashboard for optimal compatibility and features.")
    
    try:
        client = OpenAI()
        # A light check to confirm client usability (optional, uncomment if needed for immediate validation)
        # try:
        #     client.models.list(limit=1)
        # except Exception as e:
        #     print(f"OpenAI client initialized, but a test call failed: {e}. Key might be invalid or network issues.")
        #     return None 
        print("OpenAI client initialized successfully.")
        return client
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        return None

def summarize_website(url: str, output_file: str | None = None, openai_client: OpenAI | None = None) -> str | None:
    """
    Summarizes the content of a given URL in Markdown format.

    Args:
        url: The URL of the website to summarize.
        output_file: Optional. If provided, the summary is written to this file.
        openai_client: Optional. An existing OpenAI client instance. If None, a new one will be created.

    Returns:
        The summary as a Markdown string, or None if summarization fails.
    """
    print(f"Attempting to summarize URL: {url}")
    website = Website(url)
    
    if "Error fetching content." == website.text or "No main textual content found after filtering." == website.text:
        print(f"Could not retrieve or parse meaningful content from {url}. Aborting summarization.")
        return None
    if not website.text.strip(): # Double check if text is empty after all
        print(f"Extracted text from {url} (Title: {website.title}) is empty. Aborting summarization.")
        return None

    client = openai_client
    if client is None:
        client = get_openai_client()
    
    if client is None:
        print("OpenAI client is not available. Cannot summarize.")
        return None

    system_prompt = (
        "You are an expert assistant that analyzes the textual content of a website "
        "and provides a concise, well-structured summary in Markdown format. "
        "Focus on the main information, ignoring navigation, boilerplate, advertisements, and irrelevant repeated phrases. "
        "If the content appears to be an article or blog post, summarize its key arguments and conclusions. "
        "If it's a homepage or a product page, describe its main purpose, offerings, and value proposition. "
        "Ensure the output is clean, readable Markdown. Extract the most salient points."
    )

    # Truncate website.text if it's too long to avoid excessive token usage/cost or API errors
    # A rough limit, as token count is more accurate but harder to quickly calculate here.
    # GPT-4o-mini context window is 128k tokens. Max input for completion is typically less.
    # Let's aim for roughly 20,000 characters as a safe input limit for the text content part.
    max_text_chars = 20000 
    truncated_text = website.text
    if len(website.text) > max_text_chars:
        print(f"Original text length ({len(website.text)} chars) exceeds limit, truncating to {max_text_chars} chars.")
        truncated_text = website.text[:max_text_chars] + "... [content truncated]"

    user_prompt = (
        f"The website I am analyzing is titled '{website.title}'.\n"
        "Here is the extracted (and potentially truncated) textual content from the website:\n\n---
"
        f"{truncated_text}\n"
        "---\n\n"
        "Please provide a concise, well-structured summary of this website in Markdown format, focusing on its core message and key information. "
        "Ignore any boilerplate or irrelevant text that might have slipped through the parsing."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        print(f"Requesting summary from OpenAI for {url} (Title: {website.title})...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.5, # Slightly lower temperature for more factual summaries
            max_tokens=1000  # Limit output tokens to prevent overly long summaries
        )
        summary = response.choices[0].message.content

        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(summary)
                print(f"Summary successfully written to {output_file}")
            except IOError as e:
                print(f"Error writing summary to file {output_file}: {e}")
        
        return summary

    except Exception as e:
        print(f"Error during OpenAI API call for {url}: {e}")
        return None 