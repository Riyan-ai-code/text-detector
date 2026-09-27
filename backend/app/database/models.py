import uuid
import datetime
from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    DateTime,
    ForeignKey,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship
from backend.app.database.connection import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="analyst")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    content_type = Column(String(50), nullable=False)  # 'text', 'document', 'audio', 'multimodal'
    file_name = Column(String(255), nullable=True)
    classification = Column(String(50), nullable=False)  # 'AUTHENTIC', 'AI_GENERATED', 'AI_ASSISTED', 'POTENTIALLY_MANIPULATED', 'UNCERTAIN'
    probability = Column(Float, nullable=False)
    confidence = Column(String(50), nullable=False)  # 'HIGH', 'MEDIUM', 'LOW'
    status = Column(String(50), default="COMPLETED")
    signals = Column(JSON, nullable=True)
    warnings = Column(JSON, nullable=True)
    model_version = Column(String(50), default="v2.1.0")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="analyses")
    text_analysis = relationship("TextAnalysis", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    sentences = relationship("SentenceResult", back_populates="analysis", cascade="all, delete-orphan")
    similarity_matches = relationship("SimilarityMatch", back_populates="analysis", cascade="all, delete-orphan")
    document = relationship("DocumentRecord", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    audio_analysis = relationship("AudioAnalysis", back_populates="analysis", uselist=False, cascade="all, delete-orphan")

class TextAnalysis(Base):
    __tablename__ = "text_analyses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_id = Column(String(36), ForeignKey("analyses.id"), nullable=False)
    text_length = Column(Integer, nullable=False)
    perplexity = Column(Float, nullable=True)
    burstiness = Column(Float, nullable=True)
    vocabulary_diversity = Column(Float, nullable=True)
    style_score = Column(Float, nullable=True)
    model_version = Column(String(50), default="v2.1.0")

    analysis = relationship("Analysis", back_populates="text_analysis")

class SentenceResult(Base):
    __tablename__ = "sentence_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_id = Column(String(36), ForeignKey("analyses.id"), nullable=False)
    sentence_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    probability = Column(Float, nullable=False)
    classification = Column(String(50), nullable=False)
    signals = Column(JSON, nullable=True)

    analysis = relationship("Analysis", back_populates="sentences")

class SimilarityMatch(Base):
    __tablename__ = "similarity_matches"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_id = Column(String(36), ForeignKey("analyses.id"), nullable=False)
    source_id = Column(String(255), nullable=True)
    source_title = Column(String(255), nullable=True)
    similarity_score = Column(Float, nullable=False)
    match_type = Column(String(50), nullable=False)  # 'exact', 'near_duplicate', 'paraphrase', 'semantic'
    matched_text = Column(Text, nullable=False)
    user_passage = Column(Text, nullable=True)

    analysis = relationship("Analysis", back_populates="similarity_matches")

class DocumentRecord(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_id = Column(String(36), ForeignKey("analyses.id"), nullable=False)
    author = Column(String(255), nullable=True)
    creator = Column(String(255), nullable=True)
    producer = Column(String(255), nullable=True)
    pages = Column(Integer, nullable=True)
    doc_created_at = Column(String(100), nullable=True)
    doc_modified_at = Column(String(100), nullable=True)
    anomalies = Column(JSON, nullable=True)
    metadata_raw = Column(JSON, nullable=True)

    analysis = relationship("Analysis", back_populates="document")

class AudioAnalysis(Base):
    __tablename__ = "audio_analyses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_id = Column(String(36), ForeignKey("analyses.id"), nullable=False)
    duration = Column(Float, nullable=False)
    sample_rate = Column(Integer, nullable=False)
    synthetic_probability = Column(Float, nullable=False)
    model_version = Column(String(50), default="v2.1.0")
    acoustic_metrics = Column(JSON, nullable=True)
    suspicious_intervals = Column(JSON, nullable=True)

    analysis = relationship("Analysis", back_populates="audio_analysis")
