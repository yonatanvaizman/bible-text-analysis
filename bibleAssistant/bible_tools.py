"""
This module provides helpful tools for Biblical research and for an AI Agent assistant.
"""
import json
import requests
import urllib.parse
#from .. import sefaria_code as sef
import sefaria_code as sef

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
    book = book.strip().lower()
    if book not in supported_books:
        err_msg = f"We don't support book named '{book}'. Here are the supported books: {', '.join(supported_books)}"
        raise ValueError(err_msg)
    
    version = version.strip().lower()
    if version not in supported_versions:
        err_msg = f"We don't support text-version named '{version}'. Here are the supported version:"
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
