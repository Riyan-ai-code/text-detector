import io
import re
import uuid
import datetime
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
import pypdf
import docx

from backend.app.models.schemas import (
    DocumentAnalyzeResponse,
    DocumentAnomaly
)
from backend.app.database.models import Analysis, DocumentRecord
from backend.app.services.text_service import text_service

ZERO_WIDTH_CHARS = {
    '\u200b': "Zero-width space (ZWSP)",
    '\u200c': "Zero-width non-joiner (ZWNJ)",
    '\u200d': "Zero-width joiner (ZWJ)",
    '\ufeff': "Zero-width no-break space / BOM",
    '\u2060': "Word joiner"
}

SUSPICIOUS_PRODUCERS = [
    "pdfcpu", "canvas", "canva", "wkhtmltopdf", "reportlab",
    "dompdf", "tcpdf", "fpdf", "headlesschrome", "puppeteer"
]


class DocumentForensicsEngine:
    """
    Phase 4 Document Forensics & Structural Inconsistency Engine.
    Inspects PDF, DOCX, and TXT files for:
    - Metadata provenance & chronometry anomalies
    - Typography, font switching, and styling variances
    - Invisible / zero-width characters (watermarks & prompt-injection filters)
    - Citation vs Bibliography coherence
    - Integrated AI text authenticity scoring
    """

    @classmethod
    def find_invisible_characters(cls, text: str) -> List[DocumentAnomaly]:
        """Detects zero-width and adversarial invisible characters in text."""
        anomalies = []
        counts: Dict[str, int] = {}
        for char, name in ZERO_WIDTH_CHARS.items():
            c = text.count(char)
            if c > 0:
                counts[name] = c

        if counts:
            details = ", ".join(f"{name}: {c}" for name, c in counts.items())
            anomalies.append(DocumentAnomaly(
                page=1,
                type="font",
                description=f"Invisible adversarial unicode characters detected ({details}) — frequently used to watermark or bypass AI detectors",
                severity="HIGH"
            ))
        return anomalies

    @classmethod
    def audit_citations(cls, text: str) -> Tuple[int, List[str], List[DocumentAnomaly]]:
        """Audits in-text citation patterns and checks for a valid Bibliography/References section."""
        citations = re.findall(
            r'\([A-Z][a-zA-Z]+(?:\s+et\s+al\.)?,\s*\d{4}\)|\[\d+\]',
            text
        )
        citation_count = len(citations)
        issues = []
        anomalies = []

        lower_text = text.lower()
        has_bibliography = (
            "references" in lower_text or
            "bibliography" in lower_text or
            "works cited" in lower_text
        )

        if citation_count >= 2 and not has_bibliography:
            msg = "Document contains in-text citations but lacks a formal References/Bibliography section."
            issues.append(msg)
            anomalies.append(DocumentAnomaly(
                page=1,
                type="citation",
                description=msg,
                severity="MEDIUM"
            ))

        return citation_count, issues, anomalies

    @classmethod
    def inspect_pdf(cls, contents: bytes) -> Tuple[str, Dict[str, Any], int, List[DocumentAnomaly]]:
        """Performs deep inspection of PDF metadata, fonts, and page layers."""
        anomalies: List[DocumentAnomaly] = []
        reader = pypdf.PdfReader(io.BytesIO(contents))
        pages = len(reader.pages)

        # 1. Metadata inspection
        meta = reader.metadata or {}
        author = str(meta.get("/Author") or meta.get("author") or "Unknown")
        creator = str(meta.get("/Creator") or meta.get("creator") or "Unknown")
        producer = str(meta.get("/Producer") or meta.get("producer") or "Unknown")
        creation_date = str(meta.get("/CreationDate") or meta.get("creationDate") or "Unknown")
        mod_date = str(meta.get("/ModDate") or meta.get("modDate") or "Unknown")

        metadata: Dict[str, Any] = {
            "author": author,
            "creator": creator,
            "producer": producer,
            "creationDate": creation_date,
            "modDate": mod_date,
            "page_count": pages,
            "file_size_bytes": len(contents)
        }

        if author == "Unknown" or not author.strip():
            anomalies.append(DocumentAnomaly(
                page=1,
                type="metadata",
                description="Missing document author provenance in metadata headers",
                severity="LOW"
            ))

        # Check automated generation software in producer / creator
        p_lower = (producer + " " + creator).lower()
        for susp in SUSPICIOUS_PRODUCERS:
            if susp in p_lower:
                anomalies.append(DocumentAnomaly(
                    page=1,
                    type="metadata",
                    description=f"Automated compiler signature detected in metadata: '{susp}'",
                    severity="MEDIUM"
                ))
                break

        # Check creation vs modification chronology
        if creation_date != "Unknown" and mod_date != "Unknown":
            if creation_date == mod_date:
                metadata["chronology_note"] = "Created and saved instantaneously (single-session generation)"

        # 2. Page & Font inspection
        extracted_text_parts = []
        all_fonts = set()

        for idx, page in enumerate(reader.pages):
            page_num = idx + 1
            text = page.extract_text() or ""
            extracted_text_parts.append(text)

            # Check font dictionary
            resources = page.get("/Resources", {})
            if isinstance(resources, dict) and "/Font" in resources:
                fonts_dict = resources["/Font"]
                if isinstance(fonts_dict, dict):
                    for font_key in fonts_dict.keys():
                        all_fonts.add(str(font_key))

            # Flag extremely sparse text on later pages
            words = text.split()
            if len(words) < 5 and pages > 1 and page_num > 1:
                anomalies.append(DocumentAnomaly(
                    page=page_num,
                    type="spacing",
                    description=f"Page {page_num} contains unusually sparse text (< 5 words)",
                    severity="LOW"
                ))

        full_text = "\n".join(extracted_text_parts)
        metadata["embedded_font_count"] = len(all_fonts)

        if len(all_fonts) > 8:
            anomalies.append(DocumentAnomaly(
                page=1,
                type="font",
                description=f"Excessive embedded font diversity ({len(all_fonts)} distinct fonts) indicative of composite document merging",
                severity="MEDIUM"
            ))

        # Zero-width character scan
        anomalies.extend(cls.find_invisible_characters(full_text))

        return full_text, metadata, pages, anomalies

    @classmethod
    def inspect_docx(cls, contents: bytes) -> Tuple[str, Dict[str, Any], int, List[DocumentAnomaly]]:
        """Inspects DOCX typography, run-level font consistency, and core properties."""
        anomalies: List[DocumentAnomaly] = []
        doc = docx.Document(io.BytesIO(contents))

        # 1. Core properties
        core_props = doc.core_properties
        author = core_props.author or "Unknown"
        last_modified_by = core_props.last_modified_by or "Unknown"
        created = str(core_props.created) if core_props.created else "Unknown"
        modified = str(core_props.modified) if core_props.modified else "Unknown"
        revision = getattr(core_props, "revision", 1)

        metadata: Dict[str, Any] = {
            "author": author,
            "last_modified_by": last_modified_by,
            "created": created,
            "modified": modified,
            "revision": revision,
            "file_size_bytes": len(contents)
        }

        if author == "Unknown" or not author.strip():
            anomalies.append(DocumentAnomaly(
                page=1,
                type="metadata",
                description="Missing author in Word document core properties",
                severity="LOW"
            ))

        if revision == 1:
            anomalies.append(DocumentAnomaly(
                page=1,
                type="metadata",
                description="Document revision is 1 (never edited or revised after creation)",
                severity="LOW"
            ))

        # 2. Text & Typography / Font-switching analysis
        paragraphs_text = []
        font_families = set()
        multi_font_paragraphs = 0

        for p_idx, p in enumerate(doc.paragraphs):
            p_text = p.text.strip()
            if not p_text:
                continue
            paragraphs_text.append(p_text)

            # Check fonts within runs of the same paragraph
            p_fonts = set()
            for run in p.runs:
                if run.font.name:
                    font_families.add(run.font.name)
                    p_fonts.add(run.font.name)

            if len(p_fonts) > 1:
                multi_font_paragraphs += 1

        full_text = "\n".join(paragraphs_text)
        metadata["detected_font_families"] = list(font_families)

        if multi_font_paragraphs > 0:
            anomalies.append(DocumentAnomaly(
                page=1,
                type="font",
                description=f"In-paragraph font family shifts detected in {multi_font_paragraphs} paragraph(s) (common symptom of copy-pasting from external LLM chat windows)",
                severity="HIGH"
            ))

        # Zero-width character scan
        anomalies.extend(cls.find_invisible_characters(full_text))

        # Rough page estimate based on word count
        word_count = len(full_text.split())
        estimated_pages = max(1, (word_count // 350) + 1)

        return full_text, metadata, estimated_pages, anomalies

    @classmethod
    def inspect_txt(cls, contents: bytes) -> Tuple[str, Dict[str, Any], int, List[DocumentAnomaly]]:
        """Inspects plain text for encoding, zero-width characters, and line integrity."""
        anomalies: List[DocumentAnomaly] = []
        text = contents.decode("utf-8", errors="ignore")
        metadata = {
            "file_size_bytes": len(contents),
            "encoding": "utf-8",
            "char_count": len(text)
        }

        # Zero-width character scan
        anomalies.extend(cls.find_invisible_characters(text))

        word_count = len(text.split())
        estimated_pages = max(1, (word_count // 350) + 1)
        return text, metadata, estimated_pages, anomalies

    @classmethod
    def analyze_document_file(
        cls,
        filename: str,
        contents: bytes,
        user_id: Optional[str] = None,
        db: Optional[Session] = None
    ) -> DocumentAnalyzeResponse:
        """
        Main pipeline: parses file, audits structure/metadata/citations,
        runs AI text authenticity, computes calibrated risk score, and saves to DB.
        """
        ext = filename.lower().split(".")[-1]
        ext = f".{ext}"

        if ext == ".pdf":
            extracted_text, metadata, pages, anomalies = cls.inspect_pdf(contents)
        elif ext in [".docx", ".doc"]:
            extracted_text, metadata, pages, anomalies = cls.inspect_docx(contents)
        elif ext == ".txt":
            extracted_text, metadata, pages, anomalies = cls.inspect_txt(contents)
        else:
            raise ValueError(f"Unsupported document format '{ext}'")

        if not extracted_text.strip():
            extracted_text = "No readable text content could be extracted from this document."

        # Audit citations
        citation_count, citation_issues, citation_anomalies = cls.audit_citations(extracted_text)
        anomalies.extend(citation_anomalies)

        # Run System 1 (AI Text Detection) on document text
        text_eval_sample = extracted_text[:4000]
        text_res = text_service.analyze_text(
            text=text_eval_sample,
            model_selection="all",
            return_sentences=True,
            return_shap=True,
            user_id=user_id,
            db=db
        )

        # Structural manipulation score
        high_sev = sum(1 for a in anomalies if a.severity == "HIGH")
        med_sev = sum(1 for a in anomalies if a.severity == "MEDIUM")
        structural_penalty = min(0.35, (high_sev * 0.20) + (med_sev * 0.10))

        # Blended document authenticity score
        doc_prob = (text_res.probability * 0.70) + (structural_penalty)
        doc_prob = float(round(min(0.99, max(0.01, doc_prob)), 4))

        # Overall classification
        if doc_prob >= 0.75 or high_sev >= 1:
            classification = "POTENTIALLY_MANIPULATED" if high_sev >= 1 else "AI_GENERATED"
            confidence = "HIGH"
        elif doc_prob >= 0.50:
            classification = "AI_ASSISTED"
            confidence = "MEDIUM"
        elif doc_prob <= 0.25 and not anomalies:
            classification = "AUTHENTIC"
            confidence = "HIGH"
        elif doc_prob <= 0.40:
            classification = "AUTHENTIC"
            confidence = "MEDIUM"
        else:
            classification = "UNCERTAIN"
            confidence = "LOW"

        # Assemble signals
        signals = list(text_res.signals)
        if anomalies:
            signals.append(f"{len(anomalies)} structural/metadata anomal{'ies' if len(anomalies) > 1 else 'y'} detected")
        if citation_issues:
            signals.extend(citation_issues)

        analysis_id = str(uuid.uuid4())

        # Database persistence
        if db is not None:
            try:
                db_analysis = Analysis(
                    id=analysis_id,
                    user_id=user_id,
                    content_type="document",
                    file_name=filename,
                    classification=classification,
                    probability=doc_prob,
                    confidence=confidence,
                    signals=signals,
                    model_version="v3.0.0"
                )
                db.add(db_analysis)

                anomalies_serialized = [
                    {"page": a.page, "type": a.type, "description": a.description, "severity": a.severity}
                    for a in anomalies
                ]
                db_doc = DocumentRecord(
                    analysis_id=analysis_id,
                    author=metadata.get("author", "Unknown"),
                    creator=metadata.get("creator", "Unknown"),
                    producer=metadata.get("producer", "Unknown"),
                    pages=pages,
                    doc_created_at=str(metadata.get("creationDate") or metadata.get("created") or ""),
                    doc_modified_at=str(metadata.get("modDate") or metadata.get("modified") or ""),
                    anomalies=anomalies_serialized,
                    metadata_raw=metadata
                )
                db.add(db_doc)
                db.commit()
            except Exception as e:
                db.rollback()

        return DocumentAnalyzeResponse(
            classification=classification,
            probability=doc_prob,
            confidence=confidence,
            signals=signals,
            analysis_id=analysis_id,
            model_version="v3.0.0",
            file_name=filename,
            pages=pages,
            metadata=metadata,
            formatting_anomalies=anomalies,
            citations_detected=citation_count,
            citation_issues=citation_issues,
            text_analysis=text_res
        )

document_forensics = DocumentForensicsEngine()
