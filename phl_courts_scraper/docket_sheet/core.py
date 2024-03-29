"""Module for scraping docket sheet reports."""

# from pathlib import Path
# from typing import List, Optional

# import numpy as np
# import pandas as pd
# import pdfplumber

# from ..base import DownloadedPDFScraper
# from ..utils import Word, find_phrases
# from .schema import DocketSheetResults


# def parse(
#     words: List[Word],
#     pg: pdfplumber.page.Page,
#     start_keyword: str,
#     end_keywords: List[str],
#     keep_blank_chars: bool = True,
#     min_words_vertical: int = 0,
# ) -> Optional[pd.DataFrame]:
#     """
#     Parse a docket sheet.

#     Parameters
#     ----------
#     words: List[Word]
#         The list of words to parse
#     pg: pdfplumber.page.Page
#         The page object to parse
#     start_keyword: str
#         The keyword to start parsing at
#     end_keywords: List[str]
#         The keywords to stop parsing at
#     keep_blank_chars: bool
#         Whether to keep blank characters when parsing
#     min_words_vertical: int
#         The minimum number of words in a vertical line

#     Returns
#     -------
#     Optional[pd.DataFrame]
#         The parsed docket sheet, or None if no docket sheet was found

#     Raises
#     ------
#     ValueError
#         If no stop keyword is found when parsing
#     """
#     # Try to find the start phrase
#     start_match = find_phrases(words, *start_keyword.split())

#     # Match was found
#     if start_match:

#         # Where to start parsing
#         start_x = start_match[0].x0
#         start_y = start_match[0].top

#         # Look for the place to stop
#         stop_match = None
#         for end_keyword in end_keywords:
#             stop_match = find_phrases(words, *end_keyword.split())
#             if stop_match:
#                 break

#         if not stop_match:
#             raise ValueError("Could not identify end of section")
#         stop_y = stop_match[0].top

#         # Crop the page
#         cropped_pg = pg.crop((start_x, start_y, pg.width, stop_y))

#         # Extract the table
#         table = cropped_pg.extract_table(
#             table_settings=dict(
#                 vertical_strategy="text",
#                 horizontal_strategy="text",
#                 keep_blank_chars=keep_blank_chars,
#                 min_words_vertical=min_words_vertical,
#             )
#         )

#         # Convert to dataframe
#         df = pd.DataFrame(table).replace("", np.nan)

#         # Remove empty rows/columns
#         df = df.dropna(how="all", axis=1).dropna(how="all", axis=0)

#         # First two rows are headers, combine and reset column names
#         df = df.loc[2:].rename(
#             columns=dict(zip(df.columns, df.loc[0].fillna(df.loc[1]).tolist()))
#         )

#         # Format the columns
#         df.columns = ["_".join(col.lower().split()) for col in df.columns]
#         df = df.rename(columns={"date": "bail_date"}).fillna("")

#         return df.reset_index(drop=True).to_dict(orient="records")

#     return None


# class DocketSheetParser(DownloadedPDFScraper):
#     """
#     A class to parse docket sheet reports.

#     Call the class to parse a PDF. The class will return a
#     DocketSheetResults object.

#     Example
#     -------
#     >>> from phl_courts_scraper.docket_sheet import DocketSheetParser
#     >>> parser = DocketSheetParser()
#     >>> report = parser(pdf_path)
#     """

#     def __call__(
#         self, pdf_path: Path, section: str = "bail"
#     ) -> DocketSheetResults:
#         """Parse and return a docket sheet document."""
#         allowed_sections = ["bail"]
#         if section not in allowed_sections:
#             raise ValueError(f"Allowed sections to parse: {allowed_sections}")

#         start_keywords = {"bail": "Bail Action"}
#         stop_keywords = {"bail": ["CHARGES", "CPCMS"]}

#         # Open the PDF
#         out = None
#         with pdfplumber.open(pdf_path) as pdf:

#             # Loop through pages
#             for pg in pdf.pages:

#                 # Get the list of words
#                 words = [
#                     Word.from_dict(word_dict)
#                     for word_dict in pg.extract_words(keep_blank_chars=False)
#                 ]

#                 # Try to parse
#                 result = _parse(
#                     words, pg, start_keywords[section], stop_keywords[section]
#                 )

#                 # Return any results
#                 if result is not None:
#                     out = result
#                     break

#         if out is None:
#             raise ValueError("Parsing failed!")

#         return DocketSheetResults.from_dict({"data": out})
