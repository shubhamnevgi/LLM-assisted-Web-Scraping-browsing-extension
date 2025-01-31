from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed


# Load environment variables
load_dotenv()

# Fetch Groq API key from environment variables
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables")

# Define the template for parsing instructions
template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}\n\n"
    "Please follow these instructions carefully:\n\n"
    "1. Extract Information: Only extract the information that directly matches the provided description: {parse_description}\n"
    "2. No Extra Content: Do not include any additional text, comments, or explanations in your response.\n"
    "3. Data Format: Format the data in CSV format with headers based on the parsed description.\n"
    "4. Empty Response: If no information matches the description, return an empty string ('')."
)

# Initialize the Groq model
model = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key=groq_api_key
)

def parse_with_groq(dom_chunks, parse_description):
    """
    Parse DOM content using the Groq model with parallel processing.
    """
    # Create a prompt template and chain
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model | StrOutputParser()

    parsed_results = []

    # Function to process a single chunk
    def process_chunk(chunk):
        try:
            response = chain.invoke({
                "dom_content": chunk,
                "parse_description": parse_description
            })
            print(f"Parsed chunk: {response}")  # Debug parsed response

            if response.strip():
                # Clean and validate the CSV data
                cleaned_csv = clean_csv_data(response)
                if cleaned_csv:
                    return cleaned_csv
            else:
                print("Empty result for chunk")
        except Exception as e:
            print(f"Error processing chunk: {str(e)}")
        return ""  # Return empty string for failed or empty chunks

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor() as executor:
        # Submit all chunks for processing
        futures = [executor.submit(process_chunk, chunk) for chunk in dom_chunks]

        # Collect results as they complete
        for future in as_completed(futures):
            result = future.result()
            if result:
                parsed_results.append(result)

    # Handle empty results
    if not parsed_results:
        print("No valid results were parsed.")
        return ""  # Return an empty string

    # Combine all parsed results into a single CSV string
    return "\n".join(parsed_results)


def clean_csv_data(csv_data):
    """
    Clean and validate the CSV data to ensure it has the correct number of columns.
    """
    cleaned_rows = []
    lines = csv_data.splitlines()

    # Determine the number of columns from the header
    header = lines[0].split(",")
    num_columns = len(header)

    for line in lines:
        if not line.strip():  # Skip empty lines
            continue

        # Split the line into columns
        columns = line.split(",")

        # Ensure the row has the correct number of columns
        if len(columns) == num_columns:
            cleaned_rows.append(line)
        else:
            print(f"Skipping invalid row: {line}")

    return "\n".join(cleaned_rows)