"""
This module provides helpful tools for Biblical research and for an AI Agent assistant.
"""
import json
import requests
import urllib.parse
import sefaria.sefaria_code as sef
from bs4 import BeautifulSoup

supported_books = [
    sef.BookCode.GENESIS,
    sef.BookCode.EXODUS,
    sef.BookCode.LEVITICUS,
    sef.BookCode.NUMBERS,
    sef.BookCode.DEUTERONOMY,
    sef.BookCode.ISAIAH,
    sef.BookCode.JEREMIAH
]

supported_versions = [
    sef.VersionCode.HE_TEXT_ONLY,
    sef.VersionCode.HE_MASORAH,
    sef.VersionCode.EN_JSP_1917,
    sef.VersionCode.EN_KOREN,
]

def lookup_verse(version:str, book:str, chapter_num:int, verse_num:int) -> dict:
    """
    Get the text of a specific verse from the bible.

    Args:
    - version (str): the code name of a specific bible version or translation
    - book (str): the name of the book from the bible
    - chapter_num (int): chapter number inside the book
    - verse_num (int): verse number inside the chapter

    Returns:
    - dictionary with fields version, book, chapter_num, and verse_num coppied from the input arguments, and an additional field:
        - text (str): the text of the requested verse
    """
    book = book.strip().lower()
    if book not in supported_books:
        err_msg = f"We don't support book named '{book}'. Here are the supported books: {', '.join(supported_books)}"
        raise ValueError(err_msg)
    
    version = version.strip().lower()
    if version not in supported_versions:
        err_msg = f"We don't support text-version named '{version}'. Here are the supported versions:"
        for version in supported_versions:
            (version_name, desc, exam) = sef.version_code2metadata(version, use_short_desc=True)
            err_msg += f"\n  Version: '{version}'. Description: {desc}"
        raise ValueError(err_msg)
    
    local = sef.sefaria_local(book, version)
    with open(local, 'r', encoding='utf-8') as f:
        book_data = json.load(f)
    verse = book_data["text"][chapter_num-1][verse_num-1]
    verse = sef.clean_html_with_bs4(verse)
    ret = {
        "version": version,
        "book": book,
        "chapter_num": chapter_num,
        "verse_num": verse_num,
        "text": verse
    }
    return ret

def clean_html_with_bs4(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser") # Parse the HTML content
    clean_text = soup.get_text(strip=False) # Extract all text, stripping extra whitespace
    return clean_text

def search_phrase(phrase:str, n_max_results:int=10) -> dict:
    '''
    Search the bible for all the verses that contain a specific phrase.
    Currently supporting Hebrew text only (searching in WLCC version - Westminster Leningrad Codex (Consonants)).

    Args:
    - phrase (str): the word or phrase to search for. Currently only supporting a phrase in Hebrew without Nikkud (consonants only).
    - n_max_results (int): the maximum number of results to return. Default: 10

    Returns:
    - dictionary with a field "results" of the verses that have the phrase - a list items, each is a dictionary with fields:
        - book_name (str): the name of the biblical book
        - chapter_num (int): the chapter number inside the book
        - verse_num (int): the verse number inside the chapter
        - text (str): the text of the found verse (this text should include the searched phrase as a substring)
    '''
    book_map_url = "https://bolls.life/get-books/YLT/"
    try:
        book_map_resp = requests.get(book_map_url)
    except Exception as ex:
        error = f"Failed to get the book ID-Name mapping from {book_map_url}. Got error: {str(ex)}"
        raise ValueError(error)
    book_id2name = {item['bookid']:item['name'] for item in book_map_resp.json()}

    phrase_url = urllib.parse.quote(phrase)
    url = f"https://bolls.life/v2/find/WLCC?search={phrase_url}&match_case=false&match_whole=true&limit=128&page=1"
    try:
        response = requests.get(url)
    except Exception as ex:
        error = f"Failed to search {phrase}. Tried url {url}. Got error: {str(ex)}"
        raise ValueError(error)
    
    results = []
    for item in response.json().get('results'):
        if len(results) >= n_max_results:
            break
        res = {
#            'book_id': item['book'],
            'book_name': book_id2name[item['book']],
            'chapter_num': item['chapter'],
            'verse_num': item['verse'],
            'text': clean_html_with_bs4(item['text'])
        }
        results.append(res)

    results_dict = {"results": results}
    return results_dict