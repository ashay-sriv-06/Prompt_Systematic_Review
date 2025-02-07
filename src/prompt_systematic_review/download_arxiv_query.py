from prompt_systematic_review import arxiv_source
from prompt_systematic_review.paperSource import Paper
import pandas as pd
from datetime import date
from prompt_systematic_review import keywords


def queryArchive(downloadName: str):
    """
    Download papers from arxiv and save them to a csv file.
    :param downloadName: The name of the csv file to save the data to.
    """

    aSource = arxiv_source.ArXivSource()

    papers = []

    for keyWord in keywords.keywords_list:
        # go through keywords list and download
        papers += aSource.getPapers(10000, keyWord)

    # make dataframe
    titles = [paper.title for paper in papers]
    firstAuthors = [paper.firstAuthor for paper in papers]
    urls = [paper.url for paper in papers]
    dateSubmitteds = [paper.dateSubmitted for paper in papers]
    keywordss = [paper.keywords for paper in papers]

    df = pd.DataFrame(
        {
            "title": titles,
            "firstAuthor": firstAuthors,
            "url": urls,
            "dateSubmitted": dateSubmitteds,
            "keywords": keywordss,
        }
    )
    # drop duplicates
    df = df.drop_duplicates(subset=["url"])
    df.to_csv(downloadName, index=False)
