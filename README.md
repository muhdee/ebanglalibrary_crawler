# ebanglalibrary_crawler
EbanglaLibrary is an online collection of books mostly in text format divided into multiple chapters. This repo contains python scripts that can crawl and extract texts from the books into a pdf file which makes reading more convenient.

## Instructions For Usage

I have investigated and found 3 page layouts in which the texts in the books are arranged in single or multiple chapters. These 3 layouts are described as follows:

1. **The chapters have the same name and are differentiated with numbers.** For example:
    
    - চিলেকোঠার-সেপাই-০১
    - চিলেকোঠার-সেপাই-০২
    - চিলেকোঠার-সেপাই-০৩

and so on. For books with this type of chapter layout, use the `sequential_chapters.py` script. The code will ask for necessary inputs with proper instructions.

2. **The chapters have different names.** For example:
     
     - ০১। প্রথম পর্ব
     - ০২। ইথাকায় তর্কযুদ্ধ
     - ০৩। নেস্টর সকাশে টেলিমেকাস

For books with this layout, use `updated_crawl.py`.

3. **The chapters have different names but the p tags don't have any class. Paragraphs are separated with br tags.** This layout is difficult to find out. But don't worry, just use the `only_p_tag.py` script if the layout 2 does not work or shows blank chapters.

## Dependencies

The following python modules must be installed beforehand:
  1. `requests`
  2. `beautifulsoup4`
  3. `fpdf2` (*)
  4. `urllib` (usually built-in)

(*) _Notice that the module name is `fpdf2`, not `fpdf`. Python also has another module named `fpdf` which is an older version and does not support complex text rendering which is required for bengali fonts. Installing `fpdf` will create rendering issues and will create conflict with the `fpdf2` module even if it is separately installed later as both libraries have the same name. So, please make sure you install the latest version of `fpdf2` to get the desired output._

## Final Words

It is recommended to clone the entire repository locally which also includes the font file. If you want to change the font or text formatting in the pdf file, the instructions are clearly commented in the code thanks to AI. But, I would highly recommend to use generative AI to change the text formatting according to your preferance as I have done so. Feel free to add new features through pull requests. Let me know about bugs. These 3 layouts cover most of the books, but for some books these still won't work. I am still looking for solutions to cover those books too, wish me luck.
