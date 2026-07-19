import csv
import io
import json
import logging
import re
import zipfile
from typing import Any

from app.schemas.document import Document, DocumentMetadata

logger = logging.getLogger("app.services.document_loader")


class DocumentLoader:
    @staticmethod
    def load_text(content_bytes: bytes, filename: str) -> tuple[str, dict[str, Any]]:
        """Parses plain text / markdown files."""
        try:
            text = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = content_bytes.decode("latin-1", errors="ignore")

        metadata = {
            "title": filename.rsplit(".", 1)[0].replace("_", " ").title(),
            "source": filename,
            "category": "general",
        }
        return text, metadata

    @staticmethod
    def load_json(content_bytes: bytes, filename: str) -> tuple[str, dict[str, Any]]:
        """Parses structured JSON documents."""
        try:
            data = json.loads(content_bytes.decode("utf-8"))
            if isinstance(data, dict):
                text_parts = []
                for k, v in data.items():
                    text_parts.append(f"{k}: {v}")
                text = "\n".join(text_parts)
                metadata = {
                    "title": data.get(
                        "title", filename.rsplit(".", 1)[0].replace("_", " ").title()
                    ),
                    "category": data.get("category", "faq"),
                }
            elif isinstance(data, list):
                text = json.dumps(data, indent=2)
                metadata = {"title": filename, "category": "kb_list"}
            else:
                text = str(data)
                metadata = {"title": filename}
        except Exception as e:
            logger.error(f"Failed to parse JSON file {filename}: {e}")
            text = content_bytes.decode("utf-8", errors="ignore")
            metadata = {"title": filename}

        metadata["source"] = filename
        return text, metadata

    @staticmethod
    def load_csv(content_bytes: bytes, filename: str) -> tuple[str, dict[str, Any]]:
        """Parses CSV files into table-like formatted text."""
        try:
            text_stream = io.StringIO(content_bytes.decode("utf-8"))
        except UnicodeDecodeError:
            text_stream = io.StringIO(content_bytes.decode("latin-1", errors="ignore"))

        reader = csv.reader(text_stream)
        rows = list(reader)

        if not rows:
            return "", {"source": filename}

        formatted_parts = []
        headers = rows[0]
        for idx, row in enumerate(rows[1:], start=1):
            row_str = ", ".join(
                [
                    f"{headers[i] if i < len(headers) else 'col_' + str(i)}: {val}"
                    for i, val in enumerate(row)
                ]
            )
            formatted_parts.append(f"Record {idx}: {row_str}")

        text = "\n".join(formatted_parts)
        metadata = {
            "title": filename.rsplit(".", 1)[0].replace("_", " ").title(),
            "source": filename,
            "category": "database_export",
        }
        return text, metadata

    @staticmethod
    def load_html(content_bytes: bytes, filename: str) -> tuple[str, dict[str, Any]]:
        """Parses HTML files, stripping tags and scripts."""
        try:
            html_content = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            html_content = content_bytes.decode("latin-1", errors="ignore")

        # Strip script and style tags
        html_content = re.sub(
            r"<script.*?>.*?</script>", "", html_content, flags=re.DOTALL | re.IGNORECASE
        )
        html_content = re.sub(
            r"<style.*?>.*?</style>", "", html_content, flags=re.DOTALL | re.IGNORECASE
        )
        # Strip all other HTML tags
        text = re.sub(r"<[^>]+>", " ", html_content)
        # Clean extra whitespace
        text = re.sub(r"\s+", " ", text).strip()

        title_match = re.search(r"<title>(.*?)</title>", html_content, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else filename.rsplit(".", 1)[0]

        metadata = {"title": title, "source": filename, "category": "web_page"}
        return text, metadata

    @staticmethod
    def load_docx(content_bytes: bytes, filename: str) -> tuple[str, dict[str, Any]]:
        """Parses DOCX files by reading its internal document.xml (Office Open XML)."""
        text_parts = []
        try:
            with zipfile.ZipFile(io.BytesIO(content_bytes)) as docx_zip:
                doc_xml = docx_zip.read("word/document.xml")
                # Simple regex XML paragraph parsing to avoid dependencies
                # Matches <w:t>...</w:t> tags
                text_runs = re.findall(r"<w:t.*?>(.*?)</w:t>", doc_xml.decode("utf-8"))
                text_parts.append(" ".join(text_runs))
        except Exception as e:
            logger.error(f"Failed to parse DOCX file {filename}: {e}")
            text_parts.append(content_bytes.decode("utf-8", errors="ignore"))

        text = "\n".join(text_parts)
        # Clean up XML entities
        text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")

        metadata = {
            "title": filename.rsplit(".", 1)[0].replace("_", " ").title(),
            "source": filename,
            "category": "document",
        }
        return text, metadata

    @staticmethod
    def load_pdf(content_bytes: bytes, filename: str) -> tuple[str, dict[str, Any]]:
        """Parses PDF files. Fallback to basic string extraction of text stream tokens."""
        text_parts = []
        try:
            pdf_data = content_bytes.decode("latin-1", errors="ignore")
            # PDF text streams are inside objects: Tj, TJ, BT ... ET
            # Simple extractor looking for Tj/TJ commands
            matches = re.findall(r"\((.*?)\)\s*Tj", pdf_data)
            if matches:
                text_parts.append(" ".join(matches))
            else:
                # Fallback: extract clean printable words
                words = re.findall(r"[A-Za-z0-9\s\-\.\,\?\!\'\"]{4,}", pdf_data)
                cleaned_words = [
                    w for w in words if "obj" not in w and "endobj" not in w and "stream" not in w
                ]
                text_parts.append(" ".join(cleaned_words[:5000]))  # cap to avoid binary dump
        except Exception as e:
            logger.error(f"Failed to parse PDF file {filename}: {e}")

        text = " ".join(text_parts)
        # Clean escape sequences common in PDF text
        text = re.sub(r"\\([0-7]{3})", "", text)  # octave escapes
        text = text.replace("\\(", "(").replace("\\)", ")")

        metadata = {
            "title": filename.rsplit(".", 1)[0].replace("_", " ").title(),
            "source": filename,
            "category": "manual",
        }
        return text, metadata

    @classmethod
    def load_document(cls, file_content: bytes, filename: str) -> Document:
        """Determines the loader based on the file extension and returns a Document."""
        ext = filename.split(".")[-1].lower() if "." in filename else "txt"

        if ext in ["json"]:
            text, meta_dict = cls.load_json(file_content, filename)
            mime = "application/json"
        elif ext in ["csv"]:
            text, meta_dict = cls.load_csv(file_content, filename)
            mime = "text/csv"
        elif ext in ["html", "htm"]:
            text, meta_dict = cls.load_html(file_content, filename)
            mime = "text/html"
        elif ext in ["docx"]:
            text, meta_dict = cls.load_docx(file_content, filename)
            mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif ext in ["pdf"]:
            text, meta_dict = cls.load_pdf(file_content, filename)
            mime = "application/pdf"
        else:  # txt, md, markdown
            text, meta_dict = cls.load_text(file_content, filename)
            mime = "text/plain"

        # Construct safe ID
        doc_id = f"DOC-{hash(filename) % 100000:05d}"

        metadata = DocumentMetadata(
            title=meta_dict.get("title"),
            source=meta_dict.get("source"),
            category=meta_dict.get("category", "general"),
            product=meta_dict.get("product"),
            author=meta_dict.get("author"),
            custom_metadata={
                k: v
                for k, v in meta_dict.items()
                if k not in ["title", "source", "category", "product"]
            },
        )

        return Document(
            document_id=doc_id,
            title=metadata.title or filename,
            content=text,
            metadata=metadata,
            mime_type=mime,
            chunk_count=0,
        )
