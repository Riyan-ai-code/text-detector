from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field

# Authenticity Engine Common Schema
class CommonAuthenticityResult(BaseModel):
    model_config = {"protected_namespaces": ()}
    classification: str = Field(..., description="AUTHENTIC | AI_GENERATED | AI_ASSISTED | POTENTIALLY_MANIPULATED | UNCERTAIN")
    probability: float = Field(..., ge=0.0, le=1.0, description="Likelihood between 0.0 and 1.0")
    confidence: str = Field(..., description="HIGH | MEDIUM | LOW")
    signals: List[str] = Field(default_factory=list, description="List of detected evidence signals")
    warnings: List[str] = Field(
        default_factory=lambda: [
            "AI detection is probabilistic and should not be treated as definitive proof of authorship."
        ],
        description="Disclaimer and uncertainty warnings"
    )
    model_version: str = Field(default="v2.1.0")
    analysis_id: str

# Sentence-level detection schema
class SentenceAnalysisItem(BaseModel):
    sentence_index: int
    text: str
    probability: float
    classification: str
    confidence: str
    signals: List[str] = Field(default_factory=list)

# System 1: Text Detection
class TextAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=5, description="Text passage to inspect")
    model: Optional[str] = Field(default="all", description="'all' | 'deberta' | 'roberta' | 'bert' | 'ensemble'")
    return_sentences: bool = Field(default=True)
    return_shap: bool = Field(default=True)

class TextAnalyzeResponse(CommonAuthenticityResult):
    model_config = {"protected_namespaces": ()}
    text_length: int
    word_count: int
    counts: Optional[Dict[str, int]] = None
    perplexity: Optional[float] = None
    burstiness: Optional[float] = None
    vocabulary_diversity: Optional[float] = None
    statistical_signals: Optional[Dict[str, Any]] = None
    stylometric_signals: Optional[Dict[str, Any]] = None
    fingerprint_signals: Optional[Dict[str, Any]] = None
    calibration: Optional[Dict[str, Any]] = None
    evasion_audit: Optional[Dict[str, Any]] = None
    consensus_matrix: Optional[Dict[str, Any]] = None
    stylometrics: Optional[Dict[str, Any]] = None
    sentence_breakdown: Optional[List[SentenceAnalysisItem]] = None
    shap_contributions: Optional[Dict[str, float]] = None
    model_breakdown: Optional[Dict[str, Any]] = None
    authorship_timeline: Optional[Dict[str, Any]] = None
    watermark_analysis: Optional[Dict[str, Any]] = None
    paraphrase_analysis: Optional[Dict[str, Any]] = None
    readability: Optional[Dict[str, Any]] = None


# System 2: Plagiarism & Paraphrase
class PlagiarismMatch(BaseModel):
    source_id: str
    source_title: str
    similarity_score: float
    match_type: str  # 'exact' | 'near_duplicate' | 'paraphrase' | 'semantic'
    matched_text: str
    user_passage: str

class PlagiarismAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=10)
    threshold: float = Field(default=0.70, ge=0.0, le=1.0)
    top_k: int = Field(default=5, ge=1, le=20)

class PlagiarismAnalyzeResponse(CommonAuthenticityResult):
    overall_similarity: float
    paraphrase_likelihood: str  # 'High' | 'Medium' | 'Low'
    matches: List[PlagiarismMatch] = Field(default_factory=list)

# System 3: Document Authenticity
class DocumentAnomaly(BaseModel):
    page: Optional[int] = None
    type: str  # 'metadata' | 'font' | 'spacing' | 'heading' | 'citation'
    description: str
    severity: str  # 'LOW' | 'MEDIUM' | 'HIGH'

class DocumentAnalyzeResponse(CommonAuthenticityResult):
    file_name: str
    pages: int
    metadata: Dict[str, Any]
    formatting_anomalies: List[DocumentAnomaly] = Field(default_factory=list)
    citations_detected: int = 0
    citation_issues: List[str] = Field(default_factory=list)
    text_analysis: Optional[TextAnalyzeResponse] = None

# System 4: Audio Authenticity
class SuspiciousInterval(BaseModel):
    start_time: float
    end_time: float
    score: float
    reason: str

class AudioAnalyzeResponse(CommonAuthenticityResult):
    file_name: str
    duration_seconds: float
    sample_rate: int
    acoustic_features: Dict[str, Any]
    suspicious_intervals: List[SuspiciousInterval] = Field(default_factory=list)

# Auth Schemas
class UserRegisterRequest(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2)
    password: str = Field(..., min_length=6)

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# History
class AnalysisListItem(BaseModel):
    id: str
    content_type: str
    file_name: Optional[str] = None
    classification: str
    probability: float
    confidence: str
    created_at: str
