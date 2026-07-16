import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from fpdf import FPDF

# -------------------------------------------------------------------
# User input
# -------------------------------------------------------------------
intro_url = input("Enter the full URL of the introduction page: ").strip()
chapter_base_url = input(
    "Enter the base URL for chapters "
    "(leave blank for default 'https://www.ebanglalibrary.com/lessons/'): "
).strip() or "https://www.ebanglalibrary.com/lessons/"
if not chapter_base_url.endswith("/"):
    chapter_base_url += "/"
chapter_name = input(
    "Enter the chapter name as it appears in the URL, without the chapter number "
    "(e.g. হেমলকের-নিমন্ত্রণ): "
).strip()
digit_choice = input(
    "Are chapter numbers in the URL single-digit (e.g. ৪) or double-digit "
    "(e.g. ০৪)? Enter 1 for single, 2 for double: "
).strip()
digit_width = 2 if digit_choice == "2" else 1
total_chapters = int(input("Enter the total number of chapters: ").strip())
output_filename = input(
    "Enter the output PDF filename (leave blank for 'output.pdf'): "
).strip() or "output.pdf"

# -------------------------------------------------------------------
# Initialize FPDF
# -------------------------------------------------------------------
pdf = FPDF(format="A4")
pdf.set_margins(15, 15, 15)  # left, top, right margins
pdf.set_auto_page_break(auto=True, margin=15)

# Enable complex text shaping for Bengali
pdf.set_text_shaping(True)

# Add Bengali font (Ensure Kalpurush.ttf is in the same directory)
pdf.add_font("Kalpurush", "", "Kalpurush.ttf")

# Dark red color for chapter titles
DARK_RED = (139, 0, 0)
BLACK = (0, 0, 0)

# English → Bengali digit map
digit_map = {
    "0": "০", "1": "১", "2": "২", "3": "৩", "4": "৪",
    "5": "৫", "6": "৬", "7": "৭", "8": "৮", "9": "৯"
}


def to_bengali_number(n, width=1):
    """Converts n to Bengali digits, zero-padded to the given width."""
    return "".join(digit_map[d] for d in str(n).zfill(width))


def indent(paragraph):
    """Add a small tab (two spaces) at the start of a paragraph."""
    return "  " + paragraph


def extract_from_p_with_br(p_tag):
    """
    Given a <p> tag that may contain one or more <br> tags, split its
    contents into separate paragraphs at each <br>.
    """
    # Replace every <br> with a newline marker, then split on it.
    for br in p_tag.find_all("br"):
        br.replace_with("\n")
    text = p_tag.get_text()
    return [chunk.strip() for chunk in text.split("\n") if chunk.strip()]


def extract_paragraphs(soup):
    """
    Extracts paragraphs from a page, handling multiple known site layouts:

    1. <p class="wp-block-paragraph"> tags directly on the page.
    2. A <div class="ld-tab-content ld-visible entry-content"> containing
       one or more unclassed <p> tags, where paragraphs may be separated
       by <br> tags either within a single <p> or across multiple <p> tags.
    """
    # --- Layout 1: wp-block-paragraph ---
    wp_paragraphs = soup.find_all("p", class_="wp-block-paragraph")
    if wp_paragraphs:
        return [p.get_text(strip=True) for p in wp_paragraphs
                if p.get_text(strip=True)]

    # --- Layout 2: ld-tab-content entry-content div ---
    content_div = soup.find(
        "div", class_="ld-tab-content ld-visible entry-content"
    )
    if content_div:
        p_tags = content_div.find_all("p")
        paragraphs = []
        for p_tag in p_tags:
            paragraphs.extend(extract_from_p_with_br(p_tag))
        if paragraphs:
            return paragraphs

    return []


def fetch_intro(url):
    """Fetches the introduction/book description page once."""
    response = requests.get(url)
    if response.status_code != 200:
        print("Warning: Could not fetch the introduction page.")
        return None

    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    return extract_paragraphs(soup)


def fetch_chapter(base_url, name, chapter_num, width=1):
    full_chapter_name = f"{name}-{to_bengali_number(chapter_num, width)}"
    encoded_url = base_url + quote(full_chapter_name)

    response = requests.get(encoded_url)
    if response.status_code != 200:
        return None

    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    return extract_paragraphs(soup)


# -------------------------------------------------------------------
# Introduction page
# -------------------------------------------------------------------
print("Fetching introduction page...")
intro_paragraphs = fetch_intro(intro_url)

if intro_paragraphs:
    pdf.add_page()

    # Header for the Intro page (dark red)
    pdf.set_font("Kalpurush", size=22)
    pdf.set_text_color(*DARK_RED)
    pdf.multi_cell(180, 14, "বইয়ের পরিচিতি", align="C")
    pdf.ln(10)

    # Body for the Intro page (black)
    pdf.set_font("Kalpurush", size=16)
    pdf.set_text_color(*BLACK)
    for para in intro_paragraphs:
        if not para.strip():
            continue
        pdf.multi_cell(180, 10, indent(para))
        pdf.ln(5)
else:
    print("Skipping intro page layout as no paragraphs were found.")

# -------------------------------------------------------------------
# Chapters
# -------------------------------------------------------------------
for chapter_num in range(1, total_chapters + 1):
    paragraphs = fetch_chapter(chapter_base_url, chapter_name, chapter_num, digit_width)
    if not paragraphs:
        print(f"Warning: No content found for chapter {chapter_num}, skipping.")
        continue

    # Start a new page for each chapter
    pdf.add_page()

    # --- Heading (dark red) ---
    pdf.set_font("Kalpurush", size=22)
    pdf.set_text_color(*DARK_RED)
    pdf.multi_cell(180, 14, f"অধ্যায় {to_bengali_number(chapter_num, digit_width)}", align="C")
    pdf.ln(10)

    # --- Body Text (black) ---
    pdf.set_font("Kalpurush", size=16)
    pdf.set_text_color(*BLACK)
    print(f"{len(paragraphs)} paragraphs found in chapter {chapter_num}")

    for para in paragraphs:
        if not para.strip():
            continue
        pdf.multi_cell(180, 10, indent(para))
        pdf.ln(5)

# -------------------------------------------------------------------
# Output the complete document
# -------------------------------------------------------------------
pdf.output(output_filename)
print(f"PDF saved successfully as '{output_filename}'!")