"""
Universal Schemas for the AI Resume Screening & Ranking System.
Supports Pydantic when installed, with seamless Pure-Python standard library dataclass fallback.
"""
from typing import List, Optional, Dict, Any

try:
    from pydantic import BaseModel, Field
    
    class ScoreBreakdown(BaseModel):
        ai_project_depth: float = Field(default=0.0, ge=0.0, le=40.0)
        python_backend: float = Field(default=0.0, ge=0.0, le=30.0)
        cloud_fullstack: float = Field(default=0.0, ge=0.0, le=15.0)
        github: float = Field(default=0.0, ge=0.0, le=10.0)
        engineering_depth: float = Field(default=0.0, ge=0.0, le=5.0)

    class PenaltyDetails(BaseModel):
        thin_wrapper_deduction: float = Field(default=0.0)
        tutorial_deduction: float = Field(default=0.0)
        keyword_stuffing_deduction: float = Field(default=0.0)
        penalty_reasons: List[str] = Field(default_factory=list)

    class CandidateResult(BaseModel):
        rank: Optional[int] = Field(default=None)
        candidate_name: str
        email: Optional[str] = None
        github_url: Optional[str] = None
        eligible: bool
        rejection_reasons: List[str] = Field(default_factory=list)
        total_score: float = Field(default=0.0, ge=0.0, le=100.0)
        score_breakdown: ScoreBreakdown = Field(default_factory=ScoreBreakdown)
        penalties: Optional[PenaltyDetails] = None
        matched_skills: List[str] = Field(default_factory=list)
        project_summary: str = ""
        github_summary: Optional[str] = None
        strengths: List[str] = Field(default_factory=list)
        concerns: List[str] = Field(default_factory=list)
        source_file: str = ""

    class BatchSummary(BaseModel):
        total_resumes: int = 0
        successfully_parsed: int = 0
        eligible: int = 0
        rejected: int = 0
        failed_unreadable: int = 0
        failed_files: List[Dict[str, str]] = Field(default_factory=list)
        execution_time_seconds: float = 0.0

    class ScreeningOutput(BaseModel):
        summary: BatchSummary
        ranked_candidates: List[CandidateResult] = Field(default_factory=list)
        rejected_candidates: List[CandidateResult] = Field(default_factory=list)

    class ParsedResume(BaseModel):
        file_path: str
        raw_text: str
        candidate_name: str
        email: Optional[str] = None
        github_url: Optional[str] = None
        detected_skills: List[str] = Field(default_factory=list)
        projects_text: str = ""
        experience_text: str = ""
        is_malformed: bool = False
        error_message: Optional[str] = None

    class LLMAnalysisResult(BaseModel):
        candidate_name: Optional[str] = None
        ai_project_depth_score: float = Field(default=0.0)
        python_backend_score: float = Field(default=0.0)
        cloud_fullstack_score: float = Field(default=0.0)
        engineering_depth_score: float = Field(default=0.0)
        is_thin_wrapper: bool = False
        is_tutorial_clone: bool = False
        thin_wrapper_penalty: float = 0.0
        tutorial_penalty: float = 0.0
        matched_skills: List[str] = Field(default_factory=list)
        project_summary: str = ""
        strengths: List[str] = Field(default_factory=list)
        concerns: List[str] = Field(default_factory=list)
        evidence: Dict[str, str] = Field(default_factory=dict)

except ImportError:
    # Pure-Python Standard Library Fallback (Zero Dependencies)
    import dataclasses

    class _BaseModelHelper:
        def model_dump(self, exclude_none: bool = False) -> Dict[str, Any]:
            def _convert(v):
                if hasattr(v, 'model_dump'):
                    return v.model_dump(exclude_none=exclude_none)
                elif isinstance(v, list):
                    return [_convert(i) for i in v]
                elif isinstance(v, dict):
                    return {k: _convert(val) for k, val in v.items()}
                return v

            res = {}
            for f in dataclasses.fields(self):
                val = getattr(self, f.name)
                if exclude_none and val is None:
                    continue
                res[f.name] = _convert(val)
            return res

    @dataclasses.dataclass
    class ScoreBreakdown(_BaseModelHelper):
        ai_project_depth: float = 0.0
        python_backend: float = 0.0
        cloud_fullstack: float = 0.0
        github: float = 0.0
        engineering_depth: float = 0.0

    @dataclasses.dataclass
    class PenaltyDetails(_BaseModelHelper):
        thin_wrapper_deduction: float = 0.0
        tutorial_deduction: float = 0.0
        keyword_stuffing_deduction: float = 0.0
        penalty_reasons: List[str] = dataclasses.field(default_factory=list)

    @dataclasses.dataclass
    class CandidateResult(_BaseModelHelper):
        candidate_name: str
        eligible: bool
        rank: Optional[int] = None
        email: Optional[str] = None
        github_url: Optional[str] = None
        rejection_reasons: List[str] = dataclasses.field(default_factory=list)
        total_score: float = 0.0
        score_breakdown: ScoreBreakdown = dataclasses.field(default_factory=ScoreBreakdown)
        penalties: Optional[PenaltyDetails] = None
        matched_skills: List[str] = dataclasses.field(default_factory=list)
        project_summary: str = ""
        github_summary: Optional[str] = None
        strengths: List[str] = dataclasses.field(default_factory=list)
        concerns: List[str] = dataclasses.field(default_factory=list)
        source_file: str = ""

    @dataclasses.dataclass
    class BatchSummary(_BaseModelHelper):
        total_resumes: int = 0
        successfully_parsed: int = 0
        eligible: int = 0
        rejected: int = 0
        failed_unreadable: int = 0
        failed_files: List[Dict[str, str]] = dataclasses.field(default_factory=list)
        execution_time_seconds: float = 0.0

    @dataclasses.dataclass
    class ScreeningOutput(_BaseModelHelper):
        summary: BatchSummary
        ranked_candidates: List[CandidateResult] = dataclasses.field(default_factory=list)
        rejected_candidates: List[CandidateResult] = dataclasses.field(default_factory=list)

    @dataclasses.dataclass
    class ParsedResume(_BaseModelHelper):
        file_path: str
        raw_text: str
        candidate_name: str
        email: Optional[str] = None
        github_url: Optional[str] = None
        detected_skills: List[str] = dataclasses.field(default_factory=list)
        projects_text: str = ""
        experience_text: str = ""
        is_malformed: bool = False
        error_message: Optional[str] = None

    @dataclasses.dataclass
    class LLMAnalysisResult(_BaseModelHelper):
        candidate_name: Optional[str] = None
        ai_project_depth_score: float = 0.0
        python_backend_score: float = 0.0
        cloud_fullstack_score: float = 0.0
        engineering_depth_score: float = 0.0
        is_thin_wrapper: bool = False
        is_tutorial_clone: bool = False
        thin_wrapper_penalty: float = 0.0
        tutorial_penalty: float = 0.0
        matched_skills: List[str] = dataclasses.field(default_factory=list)
        project_summary: str = ""
        strengths: List[str] = dataclasses.field(default_factory=list)
        concerns: List[str] = dataclasses.field(default_factory=list)
        evidence: Dict[str, str] = dataclasses.field(default_factory=dict)
