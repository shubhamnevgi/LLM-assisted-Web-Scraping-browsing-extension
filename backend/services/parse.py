from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import tiktoken

# Load environment variables
load_dotenv()

# Fetch Groq API key from environment variables
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables")

# Define the template for parsing instructions
template = (
    "You are tasked with extracting specific information from the following HTML content: {dom_content}\n\n"
    "Please follow these instructions carefully:\n\n"
    "1. Extract Information: Only extract the information that directly matches the provided description: {parse_description}.\n"
    "2. No Extra Content: Do not include any additional text, comments, or explanations in your response.\n"
    "3. Data Format: Format the data in CSV format with headers based on the parsed description.\n"
    "4. Empty Response: If no information matches the description, return an empty string ('').\n"
)

# Initialize the Groq model
model = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key=groq_api_key
)

### TOKEN-AWARE SPLITTING FUNCTIONS

def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """
    Count tokens in a text using the specified encoding.
    """
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text)
    return len(tokens)

def token_aware_split(text: str, max_tokens: int = 500, encoding_name: str = "cl100k_base") -> list:
    """
    Split text into chunks such that each chunk has no more than max_tokens.
    Uses newline boundaries and falls back to word splitting if needed.
    """
    paragraphs = text.splitlines()
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        candidate = current_chunk + "\n" + para if current_chunk else para
        if count_tokens(candidate, encoding_name) > max_tokens:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = para
            else:
                # If a single paragraph is too long, split by words.
                words = para.split()
                temp_chunk = ""
                for word in words:
                    candidate_word = temp_chunk + " " + word if temp_chunk else word
                    if count_tokens(candidate_word, encoding_name) > max_tokens:
                        if temp_chunk:
                            chunks.append(temp_chunk)
                        temp_chunk = word
                    else:
                        temp_chunk = candidate_word
                if temp_chunk:
                    chunks.append(temp_chunk)
                current_chunk = ""
        else:
            current_chunk = candidate
    
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def split_dom_content_token_aware(dom_content: str, max_tokens: int = 500, encoding_name: str = "cl100k_base") -> list:
    """
    Given cleaned DOM content (HTML), extract text via BeautifulSoup and then split into token-aware chunks.
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(dom_content, "html.parser")
    text_content = soup.get_text(separator="\n")
    return token_aware_split(text_content, max_tokens=max_tokens, encoding_name=encoding_name)

### CSV CLEANING FUNCTION

def clean_csv_data(csv_data: str) -> str:
    """
    Clean a CSV string by:
      1. Removing leading/trailing whitespace and blank lines.
      2. Using the first non-empty line as the header.
      3. Skipping duplicate header lines.
      4. Keeping only rows that have the same number of columns as the header.
      5. Stripping any BOM characters from each line.
    """
    # Remove extra whitespace and split into lines.
    lines = csv_data.strip().splitlines()
    lines = [line.strip() for line in lines if line.strip() != ""]
    if not lines:
        return ""
    
    # Use the first non-empty line as header; remove BOM if present.
    header = lines[0].lstrip("\ufeff")
    try:
        header_fields = next(csv.reader([header]))
    except Exception as e:
        raise ValueError("Error reading header from CSV data.") from e
    expected_field_count = len(header_fields)
    
    valid_lines = [header]
    for line in lines[1:]:
        line = line.lstrip("\ufeff")
        if line == header:
            continue
        try:
            fields = next(csv.reader([line]))
        except Exception as e:
            print(f"Skipping line due to parsing error: {line} | Error: {e}")
            continue
        if len(fields) == expected_field_count:
            valid_lines.append(line)
        else:
            print(f"Skipping invalid line: {line} (found {len(fields)} fields, expected {expected_field_count})")
    
    cleaned_csv = "\n".join(valid_lines)
    return cleaned_csv

### PARSING FUNCTION WITH GROQ AND THREADING

def parse_with_groq(dom_chunks, parse_description):
    """
    Parse DOM content using the Groq model with parallel processing.
    Each chunk is processed individually and cleaned.
    Then, the valid CSV chunks are merged by selecting the longest (most complete) header as master.
    """
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model | StrOutputParser()

    parsed_results = []

    def process_chunk(chunk):
        try:
            response = chain.invoke({
                "dom_content": chunk,
                "parse_description": parse_description
            })
            print(f"Parsed chunk: {response}")  # Debug output
            if response.strip():
                cleaned_csv = clean_csv_data(response)
                if cleaned_csv.strip():
                    return cleaned_csv
            else:
                print("Empty result for chunk")
        except Exception as e:
            print(f"Error processing chunk: {str(e)}")
        return ""
    
    # Process chunks in parallel.
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_chunk, chunk) for chunk in dom_chunks]
        for future in as_completed(futures):
            result = future.result()
            if result.strip():
                parsed_results.append(result.strip())

    # Filter out empty chunks.
    valid_chunks = [chunk for chunk in parsed_results if chunk.strip()]
    if not valid_chunks:
        print("No valid CSV chunks found.")
        return ""

    # Use the longest chunk as the master header.
    master_chunk = max(valid_chunks, key=len)
    master_lines = master_chunk.strip().splitlines()
    if not master_lines:
        return ""
    master_header = master_lines[0].lstrip("\ufeff")
    try:
        master_fields = next(csv.reader([master_header]))
    except Exception as e:
        print(f"Error parsing master header: {e}")
        return ""
    expected_field_count = len(master_fields)

    combined_lines = [master_header]
    for chunk in valid_chunks:
        lines = chunk.strip().splitlines()
        if not lines:
            continue
        current_header = lines[0].lstrip("\ufeff")
        if current_header != master_header:
            print(f"Warning: Skipping chunk due to header mismatch. Expected: {master_header} but got: {current_header}")
            continue
        for line in lines[1:]:
            try:
                fields = next(csv.reader([line]))
            except Exception as e:
                print(f"Skipping line due to parsing error: {line} | Error: {e}")
                continue
            if len(fields) == expected_field_count:
                combined_lines.append(line)
            else:
                print(f"Skipping invalid line: {line} (found {len(fields)} fields, expected {expected_field_count})")
    final_csv = "\n".join(combined_lines)
    return final_csv