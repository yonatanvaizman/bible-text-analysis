import requests
import json
import os
import ipynbname
import pandas as pd
from bs4 import BeautifulSoup

class BookCode:
    GENESIS = "genesis"
    EXODUS = "exodus"
    LEVITICUS = "leviticus"
    NUMBERS = "numbers"
    DEUTERONOMY = "deuteronomy"
    ISAIAH = "isaiah"
    JEREMIAH = "jeremiah"

book_code2web = {
    BookCode.GENESIS: 'Tanakh/Torah/Genesis',
    BookCode.EXODUS: 'Tanakh/Torah/Exodus',
    BookCode.LEVITICUS: 'Tanakh/Torah/Leviticus',
    BookCode.NUMBERS: 'Tanakh/Torah/Numbers',
    BookCode.DEUTERONOMY: 'Tanakh/Torah/Deuteronomy',
    BookCode.ISAIAH: 'Tanakh/Prophets/Isaiah',
    BookCode.JEREMIAH: 'Tanakh/Prophets/Jeremiah'
}

class VersionCode:
    HE_TEXT_ONLY = "he.text_only"
    HE_MASORAH = "he.masorah"
    HE_TAAMEI = "he.taamei"
    HE_NIKKUD = "he.nikkud"
    EN_JEWISH = "en.jewish"
    EN_ADAM_COHN = "en.modern.adam_cohn"
    EN_JSP_1917 = "en.new.jps1917"
    EN_JSP_2006 = "en.contemp.jps2006"
    EN_KOREN = "en.koren"
    FR_RABBINAT_1899 = "fr.rabbinat1899"
    FR_SAMUEL_CAHEN_1831 = "fr.samuel_cahen1831"

version_code2web = {
    VersionCode.HE_TEXT_ONLY: 'Hebrew/Tanach%20with%20Text%20Only',
    VersionCode.HE_MASORAH: 'Hebrew/Miqra%20according%20to%20the%20Masorah',
    VersionCode.HE_TAAMEI: "Hebrew/Tanach%20with%20Ta'amei%20Hamikra",
    VersionCode.HE_NIKKUD: 'Hebrew/Tanach%20with%20Nikkud',
    VersionCode.EN_JEWISH: 'English/Jewish%20English%20Torah',
    VersionCode.EN_ADAM_COHN: 'English/Modernized%20Tanakh%20-%20Based%20on%20JPS%201917%2C%20Edited%20by%20Adam%20Cohn',
    VersionCode.EN_JSP_1917: 'English/The%20Holy%20Scriptures%20A%20New%20Translation%20JPS%201917',
    VersionCode.EN_JSP_2006: 'English/The%20Contemporary%20Torah%2C%20Jewish%20Publication%20Society%2C%202006',
    VersionCode.EN_KOREN: 'English/The%20Koren%20Jerusalem%20Bible',
    VersionCode.FR_RABBINAT_1899: 'English/Bible du Rabbinat 1899 [fr]',
    VersionCode.FR_SAMUEL_CAHEN_1831: 'English/La Bible, Traduction Nouvelle, Samuel Cahen, 1831 [fr]'
}

version_code2name = {
    VersionCode.HE_TEXT_ONLY: 'Hebrew (text only)',
    VersionCode.HE_MASORAH: 'Hebrew (Miqra according to the Masorah)',
    VersionCode.HE_TAAMEI: "Hebrew (with Ta'amei Hamikra)",
    VersionCode.HE_NIKKUD: 'Hebrew (with Nikkud)',
    VersionCode.EN_JEWISH: 'Jewish English Torah',
    VersionCode.EN_ADAM_COHN: 'Modernized Tanakh - Based on JPS 1917, Edited by Adam Cohn',
    VersionCode.EN_JSP_1917: 'The Holy Scriptures A New Translation JPS 1917',
    VersionCode.EN_JSP_2006: 'The Contemporary Torah, Jewish Publication Society, 2006',
    VersionCode.EN_KOREN: 'The Koren Jerusalem Bible',
    VersionCode.FR_RABBINAT_1899: 'Bible du Rabbinat 1899 [French]',
    VersionCode.FR_SAMUEL_CAHEN_1831: 'La Bible, Traduction Nouvelle, Samuel Cahen, 1831 [fr]'
}

def version_code2metadata(code, use_short_desc=True):
    """
    For a biblical version (code) provide metadata, including:
    name: Official name for this version
    desc: Description of what is special about this version (1-2 sentences)
    exam: Example verse written in that particual version
    """
    version_name = version_code2name[code]
    if code == VersionCode.HE_TEXT_ONLY:
        full_desc = "This is the Hebrew Bible text in the original Hebrew langauge with only the letters, but without the Nikkud markings or Ta'amei-Hamikra markings (trop)."
        short_desc = "Hebrew language, only letters."
        exam = "בראשית ברא אלהים את השמים ואת הארץ"
    elif code == VersionCode.HE_MASORAH:
        full_desc = "This is the Hebrew Bible text in the original Hebrew language according to the Masorah (the traditional script passed from generation to generation). This script has more than letters; it includes Nikkud and other markings as printed in Torah books."
        short_desc = "Hebrew language, traditional script version (full markings)."
        exam = "בְּרֵאשִׁ֖ית בָּרָ֣א אֱלֹהִ֑ים אֵ֥ת הַשָּׁמַ֖יִם וְאֵ֥ת הָאָֽרֶץ׃"
    elif code == VersionCode.HE_NIKKUD:
        full_desc = "This is the Hebrew Bible text in the original Hebrew language, with only the letters and the Nikkud (the vowel markings)."
        short_desc = "Hebrew language, with Nikkud (vowel symbols)."
        exam = "בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ׃"
    elif code == VersionCode.HE_TAAMEI:
        full_desc = "This is the Hebrew Bible text in the original Hebrew language, with Ta'amei Hamikra (special markings that indicate the melodic way to sing the text - also known as cantillation or trop signs)."
        short_desc = "Hebrew langauge, with cantillation (trop) signs."
        exam = "בְּרֵאשִׁ֖ית בָּרָ֣א אֱלֹהִ֑ים אֵ֥ת הַשָּׁמַ֖יִם וְאֵ֥ת הָאָֽרֶץ׃"
    elif code == VersionCode.EN_JSP_1917:
        full_desc = "This is a translation of the Bible to Modern English, done by the Jewish Publication Society in 1917."
        short_desc = "English language, JPS."
        exam = "In the beginning God created the heaven and the earth."
    elif code == VersionCode.EN_KOREN:
        full_desc = "This is a translation to English by Koren."
        short_desc = "English language, Koren."
        exam = "IN THE BEGINNING God created the heaven and the earth."
    elif code == VersionCode.FR_RABBINAT_1899:
        full_desc = "This is a translation to French, from 1899."
        short_desc = "French language, 1899."
        exam = "Au commencement, Dieu créa le ciel et la terre."
    elif code == VersionCode.FR_SAMUEL_CAHEN_1831:
        full_desc = "This is a translation to French, from 1831."
        short_desc = "French language, 1831."
        exam = "Au commencement Dieu créa le ciel et la terre;"
    else:
        raise ValueError(f"Unrecognized version code: {code}")
    desc = short_desc if use_short_desc else full_desc
    return (version_name, desc, exam)

def sefaria_url(book_code, version_code):
    book_web = book_code2web[book_code]
    version_web = version_code2web[version_code]
    url = f"https://raw.githubusercontent.com/Sefaria/Sefaria-Export/master/json/{book_web}/{version_web}.json"
    return url

def sefaria_local(book_code, version_code):
#    cur_dir = os.path.abspath(ipynbname.path().parent)
#    cur_dir = os.path.dirname(os.path.abspath(__file__))
#    sefaria_folder =  os.path.join(cur_dir, 'data', 'sefaria')
    sefaria_folder = os.environ["SEFARIA_DATA_DIR"]
    filename = f"{book_code}.{version_code}.json"
    filepath = os.path.join(sefaria_folder, filename)
    return filepath

def download_json_file(url, local_file, skip_fail=False) -> bool:
    try:
        response = requests.get(url)
        response.raise_for_status()  # raises error if download failed
    except Exception as ex:
        if skip_fail:
            print(f"!!! Failed fetching {url}")
            return False
        else:
            raise ex
    data = response.json()
    with open(local_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"++ {local_file}")
    return True

def sefaria_json2verses(book_data):
    verses = [verse for chapter in book_data['text'] for verse in chapter]
    return verses

def sefaria_json2text(book_data, separate_chapters=False):
    verse_delim = '\n'
    chapter_delim = '\n'
    chapters = [verse_delim.join(chapter_verses) for chapter_verses in book_data['text']]
    if separate_chapters:
        return chapters
    whole_book = chapter_delim.join(chapters)
    return whole_book

def sefaria_read_content(only_book=None, only_version=None, only_torah=True):
    books = [only_book] if only_book else list(book_code2web.keys())
    if only_torah:
        books = [BookCode.GENESIS, BookCode.EXODUS, BookCode.LEVITICUS, BookCode.NUMBERS, BookCode.DEUTERONOMY]
    versions = [only_version] if only_version else list(version_code2web.keys())
    verses = []
    for book in books:
        for version in versions:
            local = sefaria_local(book, version)
            if not os.path.exists(local):
                print(f"-- Missing {local}")
                continue
            with open(local, 'r', encoding='utf-8') as f:
                book_data = json.load(f)
            book_verses = sefaria_json2verses(book_data)
            verses.extend(book_verses)
            print(f"++ {len(book_verses)} from {book} ({version})")
    
    print(f"Read total {len(verses)} verses.")
    return verses

def clean_html_with_bs4(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser") # Parse the HTML content
    clean_text = soup.get_text(strip=True) # Extract all text, stripping extra whitespace
    return clean_text

def sefaria_read_verses_and_metadata(book, version, strip_html=True) -> list[dict]:
    local = sefaria_local(book, version)
    if not os.path.exists(local):
        print(f"-- Missing {local}")
        return []
    with open(local, 'r', encoding='utf-8') as f:
        book_data = json.load(f)
    verses = []
    for c, chapter in enumerate(book_data['text']):
        for v, verse in enumerate(chapter):
            if strip_html:
                verse = clean_html_with_bs4(verse)
            verses.append({
                'book':book, 
                'version': version,
                'chapter_num': c + 1,
                'verse_num': v + 1,
                'verse_text': verse
                })
    return verses

def sefaria_read_multiversions_of_book(book, versions, col_per_version=False, strip_html=True) -> pd.DataFrame:
    verses = []
    for version in versions:
        verses_i = sefaria_read_verses_and_metadata(book, version, strip_html=strip_html)
        verses.extend(verses_i)
    verses_df = pd.DataFrame(verses)
    if col_per_version:
        verses_df = verses_df.pivot(columns=['version'], index=['book', 'chapter_num', 'verse_num'], values=['verse_text']).reset_index()
    verses_df.columns = [''.join(map(str, col)).strip().replace('verse_text','text.') for col in verses_df.columns]
    return verses_df