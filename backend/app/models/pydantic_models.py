from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

class JobSearchRequest(BaseModel):
    """
    Represents the request body for a job search.
    """
    query: str = Field(..., description="The O*Net SOC code for the job (e.g., '29-1141.00').")
    location: Optional[str] = Field("Washington,DC", description="The user's target location, e.g., 'San Francisco,CA'. Defaults to 'Washington,DC'.")

class JobSuggestion(BaseModel):
    """
    Represents a single job title suggestion.
    """
    title: str = Field(..., description="The suggested job title.")
    soc_code: str = Field(..., description="The Standard Occupational Classification (SOC) code for the job.")

class AnalyzedTerm(BaseModel):
    """
    Represents a single analyzed term from job descriptions.
    """
    term: str = Field(..., description="The normalized term.")
    count: int = Field(..., description="The frequency of the term across all job postings.")
    context_sentences: List[str] = Field(default_factory=list, description="Example sentences where the term appeared.")

class JobInsightsReport(BaseModel):
    """
    The main report containing the analysis of job postings.
    """
    searched_title: str = Field(..., description="The job title that was searched for.")
    soc_code: str = Field(..., description="The SOC code corresponding to the searched title.")
    total_postings_analyzed: int = Field(..., description="The total number of job postings analyzed.")
    responsibilities: List[AnalyzedTerm] = Field(default_factory=list)
    skills: List[AnalyzedTerm] = Field(default_factory=list)
    qualifications: List[AnalyzedTerm] = Field(default_factory=list)
    unique_aspects: List[AnalyzedTerm] = Field(default_factory=list)

class JobAnalysisResponse(BaseModel):
    """
    The unified response model for the analyze endpoint.
    """
    success: bool = True
    suggestions: Optional[List[JobSuggestion]] = None
    data: Optional[JobInsightsReport] = None

class DataSource(BaseModel):
    """
    Represents a data source in job metadata.
    """
    data_name: Optional[str] = Field(None, alias="DataName")
    data_source_name: Optional[str] = Field(None, alias="DataSourceName")
    data_source_url: Optional[str] = Field(None, alias="DataSourceUrl")
    data_last_update: Optional[str] = Field(None, alias="DataLastUpdate")
    data_vintage_or_version: Optional[str] = Field(None, alias="DataVintageOrVersion")
    data_description: Optional[str] = Field(None, alias="DataDescription")
    data_source_citation: Optional[str] = Field(None, alias="DataSourceCitation")
    
    class Config:
        populate_by_name = True

class JobMetaData(BaseModel):
    """
    Represents metadata for a job posting.
    """
    publisher: Optional[str] = Field(None, alias="Publisher")
    sponsor: Optional[str] = Field(None, alias="Sponsor")
    last_access_date: Optional[int] = Field(None, alias="LastAccessDate")
    citation_suggested: Optional[str] = Field(None, alias="CitationSuggested")
    data_source: Optional[List[DataSource]] = Field(None, alias="DataSource")
    
    class Config:
        populate_by_name = True

class Job(BaseModel):
    """
    Represents a job posting from the CareerOneStop API.
    """
    jv_id: str = Field(..., alias="JvId", description="Unique job identifier")
    job_title: str = Field(..., alias="JobTitle", description="Job title")
    company: str = Field(..., alias="Company", description="Company name")
    acquisition_date: str = Field(..., alias="AccquisitionDate", description="Date when job was acquired")
    url: str = Field(..., alias="URL", description="Job posting URL")
    location: str = Field(..., alias="Location", description="Job location")
    fc: str = Field(..., alias="Fc", description="FC field")
    
    # Enhanced fields from detailed job API
    date_posted: Optional[str] = Field(None, alias="DatePosted", description="Date when job was posted")
    description: Optional[str] = Field(None, alias="Description", description="Full job description")
    onet_codes: Optional[List[str]] = Field(None, alias="OnetCodes", description="O*NET SOC codes")
    meta_data: Optional[JobMetaData] = Field(None, alias="MetaData", description="Job metadata")
    soc_codes: Optional[List[str]] = Field(None, description="SOC codes extracted from OnetCodes")
    soc_code: Optional[str] = Field(None, description="Primary SOC code used for search/categorization")
    
    class Config:
        populate_by_name = True

class JobInsertResponse(BaseModel):
    """
    Response model for job insertion operations.
    """
    success: bool = True
    inserted_count: int = Field(..., description="Number of jobs inserted")
    updated_count: int = Field(..., description="Number of jobs updated")
    total_processed: int = Field(..., description="Total number of jobs processed")
    message: str = Field(..., description="Operation result message")