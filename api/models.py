from pydantic import BaseModel


class ReportIn(BaseModel):
    label: str
    body: str


class IncidentCreate(BaseModel):
    title: str
    reports: list[ReportIn]


class ReportOut(BaseModel):
    label: str
    body: str


class IncidentSummary(BaseModel):
    incident_id: int
    title: str
    created_at: str


class IncidentResult(BaseModel):
    incident_id: int
    summary: str
    omissions: list
    conflicts: list


class IncidentDetail(BaseModel):
    incident_id: int
    title: str
    reports: list[ReportOut]
    summary: str
    omissions: list
    conflicts: list
