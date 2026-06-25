from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field

class Option(BaseModel):
    id: str
    label: Optional[str] = None
    label_child: Optional[str] = None
    label_teen: Optional[str] = None
    weights: Dict[str, float] = {}

class Question(BaseModel):
    id: str
    format: Literal["single","rank_best_worst"] = "single"
    # Заголовок + подзаголовки по аудитории
    text: Optional[str] = None
    text_child: Optional[str] = None
    text_teen: Optional[str] = None
    # Новый общий intro (для взрослых) + дет/подростк.
    intro: Optional[str] = None
    intro_child: Optional[str] = None
    intro_teen: Optional[str] = None
    options: List[Option]
    note: Optional[str] = None
    tags: List[str] = []

class QuestionBank(BaseModel):
    meta: dict
    features: dict
    questions: List[Question]

class SessionState(BaseModel):
    chat_id: int
    mode: Literal["child","teen","adult"] = "teen"
    gender: Optional[Literal["male","female","skip"]] = None
    style: Literal["story"] = "story"                    # оставляем только истории
    length: Literal["express","standard","deep"] = "standard"
    vectors: dict = Field(default_factory=dict)
    top_vector: Optional[str] = None
    asked: List[str] = []
    answers: Dict[str, dict] = {}
    scores: Dict[str, float] = {}
    route_core: List[str] = []
    route_branch: List[str] = []
    bws_done: bool = False
    started_at: Optional[str] = None
    finished: bool = False
    result_code: Optional[str] = None
    daily_mode: bool = False
    total_questions: int = 0
    daily_asked: List[str] = Field(default_factory=list)
    daily_answers: Dict[str, dict] = Field(default_factory=dict)
    report_ready: bool = False
    deep_block: List[str] = Field(default_factory=list)
    deep_index: Optional[int] = None
