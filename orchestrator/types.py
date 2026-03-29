from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"

#define task
@dataclass
class TaskSpec:
    user_goal: str
    workspace: str
    max_steps: int


@dataclass
class Action:
    action_type: str
    command: Optional[str] = None
    args: List[str] = field(default_factory=list)
    reason: str = ""
    summary: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

#Observation = execution result
@dataclass
class Observation:
    success: bool
    exit_code: Optional[int]
    stdout: str
    stderr: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

#per-step execution record
@dataclass
class StepTrace:
    step_index: int
    timestamp: str
    action: Dict[str, Any]
    observation: Optional[Dict[str, Any]]
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

#captures environment state, execution progress, and inferred results in a unified schema
@dataclass
class RepoFacts:
    pwd_seen: bool = False
    workspace_path: Optional[str] = None

    files_listed: bool = False
    key_files_scanned: bool = False

    readme_found: bool = False
    requirements_found: bool = False
    pyproject_found: bool = False
    package_json_found: bool = False
    cargo_toml_found: bool = False

    readme_attempted: bool = False
    manifest_attempted: bool = False

    readme_preview: Optional[str] = None
    manifest_preview: Optional[str] = None

    project_type: Optional[str] = None

    readme_path: Optional[str] = None
    requirements_path: Optional[str] = None
    pyproject_path: Optional[str] = None
    package_json_path: Optional[str] = None
    cargo_toml_path: Optional[str] = None


#full runtime state
@dataclass
class ContextState:
    facts: RepoFacts = field(default_factory=RepoFacts)
    notes: List[str] = field(default_factory=list)

#full execution trace
@dataclass
class RunTrace:
    task: str
    workspace: str
    started_at: str
    finished_at: Optional[str] = None
    steps: List[Dict[str, Any]] = field(default_factory=list)
    final_summary: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)