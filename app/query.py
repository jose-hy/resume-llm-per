from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, Depends, Query
from pydantic import BaseModel, Field, validator
from enum import Enum

# Define enums for the selectable options

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
    limit: int = ...
    offset: int = ...
    exclude_citizen_only: Optional[bool] = None
    degree: Optional[List[DegreeEnum]] = Query(None)
    remote: Optional[bool] = None
    location_state: Optional[List[LocationEnum]] = Query(None)
    employment_type: Optional[List[EmploymentTypeEnum]] = Query(None)
    rerank: Optional[bool] = None

    @classmethod
    def as_form(
        cls,
        limit: int = Form(...),
        offset: int = Form(...),
        exclude_citizen_only: Optional[bool] = Form(None),
        degree: Optional[List[DegreeEnum]] = Query(None),
        remote: Optional[bool] = Form(None),
        location_state: Optional[List[LocationEnum]] = Query(None),
        employment_type: Optional[List[EmploymentTypeEnum]] = Query(None),
        rerank: Optional[bool] = Form(None)
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