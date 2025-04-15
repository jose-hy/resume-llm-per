from typing import List, Optional, Union
from pydantic import BaseModel, Field
from fastapi import Form, Query
from enum import Enum

class DegreeEnum(str, Enum):
    no_degree_required = "no_degree"
    degree_required = "required"

class EmploymentTypeEnum(str, Enum):
    ft = 'Full-time'
    pt = 'Part-time'
    ct = 'Contract'
    it = 'Internship'

class LocationEnum(str, Enum):
    alabama = "Alabama"
    alaska = "Alaska"
    arizona = "Arizona"
    arkansas = "Arkansas"
    california = "California"
    colorado = "Colorado"
    connecticut = "Connecticut"
    delaware = "Delaware"
    florida = "Florida"
    georgia = "Georgia"
    hawaii = "Hawaii"
    idaho = "Idaho"
    illinois = "Illinois"
    indiana = "Indiana"
    iowa = "Iowa"
    kansas = "Kansas"
    kentucky = "Kentucky"
    louisiana = "Louisiana"
    maine = "Maine"
    maryland = "Maryland"
    massachusetts = "Massachusetts"
    michigan = "Michigan"
    minnesota = "Minnesota"
    mississippi = "Mississippi"
    missouri = "Missouri"
    montana = "Montana"
    nebraska = "Nebraska"
    nevada = "Nevada"
    new_hampshire = "New Hampshire"
    new_jersey = "New Jersey"
    new_mexico = "New Mexico"
    new_york = "New York"
    north_carolina = "North Carolina"
    north_dakota = "North Dakota"
    ohio = "Ohio"
    oklahoma = "Oklahoma"
    oregon = "Oregon"
    pennsylvania = "Pennsylvania"
    rhode_island = "Rhode Island"
    south_carolina = "South Carolina"
    south_dakota = "South Dakota"
    tennessee = "Tennessee"
    texas = "Texas"
    utah = "Utah"
    vermont = "Vermont"
    virginia = "Virginia"
    washington = "Washington"
    west_virginia = "West Virginia"
    wisconsin = "Wisconsin"
    wyoming = "Wyoming"
    district_of_columbia = "District of Columbia"
    all = "All"

class JobSearchVars(BaseModel):
    limit: int = Field(..., description="Number of results to return")
    offset: int = Field(..., description="Number of results to skip")
    exclude_citizen_only: Optional[bool] = Field(None, description="Exclude jobs that require citizenship")
    degree: Optional[List[DegreeEnum]] = Field(None, description="Filter by degree requirement")
    remote: Optional[bool] = Field(None, description="Filter by remote work option")
    location_state: Optional[List[LocationEnum]] = Field(None, description="Filter by state location")
    employment_type: Optional[List[EmploymentTypeEnum]] = Field(None, description="Filter by employment type")
    rerank: Optional[bool] = Field(None, description="Whether to rerank results")

    @classmethod
    def as_form(
        cls,
        limit: int = Form(..., description="Number of results to return"),
        offset: int = Form(..., description="Number of results to skip"),
        exclude_citizen_only: Optional[bool] = Form(None, description="Exclude jobs that require citizenship"),
        degree: Optional[List[DegreeEnum]] = Query(None, description="Filter by degree requirement"),
        remote: Optional[bool] = Form(None, description="Filter by remote work option"),
        location_state: Optional[List[LocationEnum]] = Query(None, description="Filter by state location"),
        employment_type: Optional[List[EmploymentTypeEnum]] = Query(None, description="Filter by employment type"),
        rerank: Optional[bool] = Form(None, description="Whether to rerank results")
    ):
        return cls(
            limit=limit,
            offset=offset,
            exclude_citizen_only=exclude_citizen_only,
            degree=degree,
            remote=remote,
            location_state=location_state,
            employment_type=employment_type,
            rerank=rerank
        )

class JobSearchResponse(BaseModel):
    job_id: str
    job_title: str
    job_location: str
    company: str
    description: str
    score: float
    degree: Optional[str] = None
    remote: Optional[bool] = None
    location_state: Optional[str] = None
    employment_type: Optional[str] = None
    citizen: Optional[bool] = None
    link: Optional[str] = None
    job_post_date: Optional[str] = None
    job_posted_at: Optional[int] = None

class ErrorResponse(BaseModel):
    message: str
    status: str = "error"

class AnalysisResponse(BaseModel):
    analysis: str
    status: str = "success"

JobSearchResults = Union[List[JobSearchResponse], ErrorResponse]
AnalysisResults = Union[AnalysisResponse, ErrorResponse] 