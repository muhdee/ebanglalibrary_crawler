import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from fpdf import FPDF

# Initialize FPDF
pdf = FPDF(format="A4")
pdf.set_margins(15, 15, 15)  # left, top, right margins
pdf.set_auto_page_break(auto=True, margin=15)

# Enable complex text shaping for Bengali
pdf.set_text_shaping(True)

# Add Bengali font (Ensure Kalpurush.ttf is in the same directory)
pdf.add_font("Kalpurush", "", "Kalpurush.ttf")


def fetch_page_paragraphs(url):
    """Fetches a page and returns its list of paragraph texts (class=wp-block-paragraph)."""
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Warning: Could not fetch {url} (status {response.status_code})")
        return None

    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.find_all("p", class_="wp-block-paragraph")
    return [p.get_text(strip=True) for p in paragraphs]


def fetch_chapter_links(intro_url):
    """Fetches the introduction page and extracts chapter hyperlinks in order.

    Chapter links are <a> tags with class="ld-item-name ld-primary-color-hover".
    Returns a list of (chapter_title, chapter_url) tuples, in the order they
    appear on the page.
    """
    response = requests.get(intro_url)
    if response.status_code != 200:
        print(f"Warning: Could not fetch the introduction page (status {response.status_code}).")
        return []

    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    anchors = soup.find_all("a", class_="ld-item-name ld-primary-color-hover")

    chapters = []
    seen = set()
    for a in anchors:
        href = a.get("href")
        if not href:
            continue
        full_url = urljoin(intro_url, href)
        if full_url in seen:
            continue
        seen.add(full_url)
        title = a.get_text(strip=True)
        chapters.append((title, full_url))

    return chapters


def add_section(title, paragraphs):
    """Adds a new page with a heading and body paragraphs, matching the
    original styling (22pt heading, 16pt body, same cell widths/heights)."""
    pdf.add_page()

    # --- Heading ---
    pdf.set_font("Kalpurush", size=22)
    pdf.set_text_color(139, 0, 0)  # dark red
    pdf.multi_cell(180, 14, title, align="C")
    pdf.ln(10)

    # --- Body Text ---
    pdf.set_text_color(0, 0, 0)  # reset to black
    pdf.set_font("Kalpurush", size=16)
    indent = "    "  # 4 spaces act as a tab at the start of each paragraph
    for para in paragraphs:
        if not para.strip():
            continue
        pdf.multi_cell(180, 10, indent + para)
        pdf.ln(5)


def main():
    intro_url = input("Enter the URL of the book's introduction page: ").strip()
    output_name = input("Enter output PDF filename (e.g. book.pdf): ").strip() or "book.pdf"

    print("Fetching introduction page...")
    intro_paragraphs = fetch_page_paragraphs(intro_url)

    if intro_paragraphs:
        add_section("বইয়ের পরিচিতি", intro_paragraphs)
    else:
        print("Skipping intro page layout as no paragraphs were found.")

    print("Extracting chapter list from introduction page...")
    chapters = fetch_chapter_links(intro_url)

    if not chapters:
        print("No chapter links found. Check the intro URL or the <a> tag class.")
    else:
        print(f"Found {len(chapters)} chapters.")

    for i, (title, url) in enumerate(chapters, start=1):
        print(f"Fetching chapter {i}/{len(chapters)}: {title} -> {url}")
        paragraphs = fetch_page_paragraphs(url)
        if not paragraphs:
            print(f"  No paragraphs found for chapter '{title}', skipping.")
            continue
        print(f"  {len(paragraphs)} paragraphs found.")
        # Use the chapter's own title text as the heading, falling back to a
        # generic "Chapter N" heading if the link had no visible text.
        heading = title if title else f"অধ্যায় {i}"
        add_section(heading, paragraphs)

    pdf.output(output_name)
    print(f"PDF saved successfully as '{output_name}'!")


if __name__ == "__main__":
    main()