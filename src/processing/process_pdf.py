import fitz
import pdfplumber
import PyPDF2
import re
import json
import os

# Задаємо шлях до папки з PDF-файлами
folder_path = r"in/files"
output_path = r"in/json"

# Функція для витягу тексту з PDF за допомогою PyMuPDF

def extract_text_pymupdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text("text")
        doc.close()
        return text
    except fitz.errors.FormatError as e:
        print(f"Error processing '{pdf_path}' with PyMuPDF: {e}")
        return extract_text_pdfplumber_no_tables(pdf_path)

# Функція для витягу тексту з PDF за допомогою PDFPlumber, без витягу таблиць
def extract_text_pdfplumber_no_tables(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            # Витягуємо всі блоки, які не є таблицями
            non_table_text = " ".join([block["text"] for block in page.extract_words() if block["top"] not in page.extract_tables()])
            text += non_table_text + "\n"
    return text

# Функція для витягу метаданих за допомогою PyPDF2
def extract_keywords_pypdf2(pdf_path):
    with open(pdf_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        metadata = pdf_reader.metadata

    # Перевіряємо, чи є метадані, і вибираємо лише поле "Keywords", якщо воно існує
    keywords = metadata.get("/Keywords", None) if metadata else None
    if keywords:
        return keywords.replace(';', ',').split(', ')
    else:
        return None

# Оновлена функція для очищення тексту
def clean_text(text):
    # Видаляємо зайві розриви рядків
    text = re.sub(r'\n+', ' ', text)
    # Видаляємо заголовки сторінок або номери
    text = re.sub(r'(Page \d+|Journal Name.*?\n)', ' ', text)
    # Видаляємо посилання на літературу у вигляді [1], [12] тощо
    text = re.sub(r'\[\d+\]', '', text)
    # Видаляємо веб-посилання
    text = re.sub(r'http\S+|doi\.org\S+|DOI:\S+|doi:\S+', ' ', text)
    # Видаляємо згадки про PMID, PMCID, DOI
    text = re.sub(r'(PMID|PMCID|DOI):?\s?\d+', '', text)
    # Видаляємо зайві пробіли та зайву інформацію
    text = re.sub(r'(\s{2,}|\t|\r)', ' ', text)
    # Видаляємо фрази про застереження авторів чи видавців
    text = re.sub(r'(Disclaimer.*|Publisher’s Note.*|responsibility.*|editor(s)?.*|injury.*)', ' ', text, flags=re.IGNORECASE)
    # Remove lines that look like section headers, page numbers, or table of contents
    text = re.sub(r'\b(?:Table of Contents|Abstract|Summary|References|Glossary|Appendix|Annex)\b.*\n', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\b\d+\.\d+\b|\b[A-Z]+\b|\bAppendix\b|[0-9]{1,3}\s*\b', '', text)
    text = re.sub(r'(\b[A-Z][a-z]*\b(\s|\.)){1,3}\d+\b.*\n', '', text)  # for patterns like "Chapter 3.4.2"
    return text.strip()

# Функція для обробки всіх PDF у папці
def process_pdfs_in_folder(folder_path):
    processed_pdfs = []
    
    for filename in os.listdir(folder_path):
        if not filename.endswith(".pdf") or filename in ['gymbeam_hackathon_x7thy75bw9.pdf', 'gymbeam_hackathon_7lvcr8vpdu.pdf']:
            continue
            
        print(f"Processing '{filename}'...")
        pdf_path = os.path.join(folder_path, filename)

        try:
            # Виконуємо витяг тексту з PDF
            raw_text = extract_text_pymupdf(pdf_path)
            alt_text = extract_text_pdfplumber_no_tables(pdf_path)
            combined_text = raw_text if raw_text else alt_text
            cleaned_text = summarize(clean_text(combined_text))

            # Збираємо дані у JSON-формат
            data = {
                "name": filename,
                "text": cleaned_text,
                "keywords": extract_keywords_pypdf2(pdf_path)
            }
            if data["keywords"] is None:
                # Look for keywords in the cleaned text
                pattern = r'\bKeywords\b(?:[^a-zA-Z]|$)(.*?)(?=Introduction|Abstract|A B S T R A C T)'
                keywords = re.findall(pattern, cleaned_text, re.DOTALL)
                keywords = [k.replace(';', ',').split(', ') for k in keywords]
                data["keywords"] = keywords

            # Збереження у JSON-файл
            processed_pdfs.append(data)
        except Exception as e:
            print(f"Error processing file {filename}: {str(e)}")
    
    json_filename = "processed_pdfs.json"
    json_path = os.path.join(output_path, json_filename)
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(processed_pdfs, json_file, ensure_ascii=False, indent=4)


def summarize(text):
    return text

# Виклик функції для обробки всіх PDF у папці
process_pdfs_in_folder(folder_path)
