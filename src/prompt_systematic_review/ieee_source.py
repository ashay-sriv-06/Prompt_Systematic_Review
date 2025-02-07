import requests
from xml.etree import ElementTree as ET
from typing import List
import re
from datetime import date
from prompt_systematic_review.paperSource import Paper
from prompt_systematic_review.utils import headers


class IEEESource:
    """A class to represent a source of papers from IEEE."""

    baseURL = "https://ieeexploreapi.ieee.org/api/v1/search/articles"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def getPapers(self, count: int, keyWords: List[str]) -> List[Paper]:
        """
        Get a list of papers from IEEE that match the given keywords.


        :param count: The number of papers to retrieve.
        :type count: int
        :param keyWords: A list of keywords to match.
        :type keyWords: List[str]
        :return: A list of matching papers.
        :rtype: List[Paper]
        """
        papers = []
        for keyword in keyWords:
            params = {
                "querytext": keyword,
                "max_records": count,
                "apikey": self.api_key,
                "format": "xml",
            }

            data = requests.get(
                self.baseURL, params=params, headers=headers
            ).content.decode("utf-8", "ignore")
            f = open(f"ieee_{keyword}_data.xml", "w")
            f.write(data)
            f.close()

            parser = ET.XMLParser(encoding="utf-8")
            root = ET.fromstring(data, parser=parser)

            for entry in root.findall(".//article"):
                title = entry.find("title").text
                firstAuthor = (
                    entry.find("authors/author/full_name").text
                    if entry.find("authors/author/full_name") is not None
                    else ""
                )
                url = entry.find("pdf_url").text.replace("&amp;", "&")
                dateSubmitted = entry.find("publication_date")
                if dateSubmitted is not None:
                    dateSubmitted = dateSubmitted.text

                keywords = [
                    term.text
                    for term in entry.findall("index_terms/author_terms/terms")
                    if term.text
                ] + [
                    term.text
                    for term in entry.findall("index_terms/ieee_terms/term")
                    if term.text
                ]
                keywords = [k.lower() for k in keywords]

                # dateSubmitted = None # parse_date(dateSubmitted)

                paper = Paper(title, firstAuthor, url, dateSubmitted, keywords)
                papers.append(paper)

        return papers

    def getPaperSrc(self, paper: Paper, destinationFolder: str) -> str:
        num = paper.url.split("=")[-1]
        url = f"https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber={num}&ref="
        response = requests.get(url, headers=headers)
        with open(destinationFolder + num + ".pdf", "wb") as f:
            f.write(response.content)

        return ""


def parse_date(date_str):
    # Remove dots and normalize spacing
    date_str = date_str.replace(".", "").strip()

    # Convert month name to month number
    def month_to_num(month):
        month_dict = {
            "Jan": 1,
            "Feb": 2,
            "Mar": 3,
            "Apr": 4,
            "May": 5,
            "Jun": 6,
            "Jul": 7,
            "Aug": 8,
            "Sep": 9,
            "Sept": 9,
            "Oct": 10,
            "Nov": 11,
            "Dec": 12,
        }
        return month_dict.get(month, month_dict.get(month[:3]))

    # Patterns
    pattern1 = r"(\d+)-(\d+) ([A-Za-z]+) (\d{4})"
    pattern2 = r"(\d+) ([A-Za-z]+) (\d{4})"
    pattern3 = r"(\d+) ([A-Za-z]+)-(\d+) ([A-Za-z]+) (\d{4})"
    pattern4 = r"([A-Za-z]+) (\d{4})"

    if re.match(pattern1, date_str):
        day_start, _, month, year = re.search(pattern1, date_str).groups()
        return date(int(year), month_to_num(month), int(day_start))

    elif re.match(pattern2, date_str):
        day, month, year = re.search(pattern2, date_str).groups()
        return date(int(year), month_to_num(month), int(day))

    elif re.match(pattern3, date_str):
        day, month_start, _, _, year = re.search(pattern3, date_str).groups()
        return date(int(year), month_to_num(month_start), int(day))

    elif re.match(pattern4, date_str):
        month, year = re.search(pattern4, date_str).groups()
        return date(int(year), month_to_num(month), 1)

    else:
        raise ValueError("Unsupported date format")
