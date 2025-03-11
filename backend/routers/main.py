from fastapi import APIRouter, HTTPException
from backend.models import ScrapeRequest, ScrapeResponse
from backend.services.scrape import scrape_website, extract_body_content, clean_body_content
from backend.services.parse import parse_with_groq, clean_csv_data, split_dom_content_token_aware
import pandas as pd
import io
import xml.etree.ElementTree as ET
import xml.sax.saxutils as saxutils
import logging
import base64

router = APIRouter()
logger = logging.getLogger(__name__)

from fastapi.responses import JSONResponse

@router.post("/scrape_and_parse/", response_model=ScrapeResponse)
async def scrape_and_parse(request: ScrapeRequest):
    try:
        logger.info(f"Received request: {request}")

        # Validate output format
        if request.output_format not in ["csv", "json", "excel", "xml"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid output format. Allowed values: csv, json, excel, xml."
            )

        all_csvs = []

        # 1. Scrape & parse each URL into CSV
        for url in request.urls:
            i = request.urls.index(url) + 1
            logger.info(f"Processing URL: {url}")
            dom_content = scrape_website(url)
            if not dom_content:
                logger.warning(f"Failed to scrape website: {url}")
                continue  # Skip if scraping fails

            body_content = extract_body_content(dom_content)
            cleaned_content = clean_body_content(body_content)

            dom_chunks = split_dom_content_token_aware(cleaned_content, max_tokens=500)
            print(f"Parsing Website {i}: {url}")
            parsed_csv = parse_with_groq(dom_chunks, request.parse_description)
            if not parsed_csv:
                logger.warning(f"No relevant information found for URL: {url}")
                continue

            cleaned_csv = clean_csv_data(parsed_csv)
            if cleaned_csv.strip():
                all_csvs.append(cleaned_csv)

        if not all_csvs:
            raise HTTPException(
                status_code=400,
                detail="No valid data extracted from provided URLs."
            )

        # 2. Combine all CSV strings into a single DataFrame
        master_df = None

        for csv_str in all_csvs:
            csv_str = csv_str.strip()
            if not csv_str:
                continue
            try:
                # Parse this CSV chunk into a DataFrame
                df_chunk = pd.read_csv(io.StringIO(csv_str))
            except pd.errors.ParserError as e:
                logger.warning(f"Skipping invalid CSV chunk due to parsing error: {e}")
                continue

            # If this is the first valid DataFrame, store it as master
            if master_df is None:
                master_df = df_chunk
            else:
                # Check if column counts match
                if len(df_chunk.columns) == len(master_df.columns):
                    # Force rename columns to match master columns
                    df_chunk.columns = master_df.columns
                    master_df = pd.concat([master_df, df_chunk], ignore_index=True)
                else:
                    logger.warning(
                        f"Skipping chunk due to column count mismatch. "
                        f"Expected {len(master_df.columns)}, got {len(df_chunk.columns)}"
                    )

        if master_df is None or master_df.empty:
            raise HTTPException(
                status_code=400,
                detail="All CSV chunks were invalid or mismatched column counts."
            )

        # 3. Convert the unified DataFrame to the desired output format
        if request.output_format == "csv":
            data = master_df.to_csv(index=False)
        elif request.output_format == "json":
            data = master_df.to_json(orient="records", indent=4)
        elif request.output_format == "excel":
            excel_file = io.BytesIO()
            with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:
                master_df.to_excel(writer, index=False)
            excel_file.seek(0)
            encoded_excel = base64.b64encode(excel_file.getvalue()).decode("utf-8")
            html_table = master_df.to_html(
                index=False,
                escape=False,
                classes="table table-bordered table-striped"
            )
            return JSONResponse(
                content={
                    "status": "success",
                    "data": encoded_excel,
                    "preview": html_table,
                    "message": "Excel data generated successfully."
                }
            )
        elif request.output_format == "xml":
            root = ET.Element("data")
            for _, row in master_df.iterrows():
                item = ET.SubElement(root, "item")
                for key, value in row.items():
                    sanitized_key = (
                        key.replace(" ", "_").replace("(", "").replace(")", "")
                    )
                    sanitized_value = saxutils.escape(str(value))
                    ET.SubElement(item, sanitized_key).text = sanitized_value
            data = ET.tostring(root, encoding="unicode", method="xml")
        else:
            raise HTTPException(
                status_code=400, detail="Invalid output format."
            )

        return ScrapeResponse(
            status="success",
            data=data,
            message="Data processed successfully."
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
