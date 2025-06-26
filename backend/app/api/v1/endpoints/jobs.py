from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Union, Tuple, Optional
from difflib import SequenceMatcher

from app.core.config import Settings, get_settings
from app.models.pydantic_models import (
    JobSearchRequest,
    JobAnalysisResponse,
    JobInsertResponse,
    JobSuggestion,
    Job
)
from app.services import career_api_service
from app.services.analysis_service import generate_report_from_postings
from app.db.mongodb import insert_jobs_from_job_set, get_jobs_by_criteria, get_job_count

router = APIRouter()

def find_job_match(query: str, supported_jobs: List[Dict[str, str]]) -> Tuple[Optional[Dict[str, str]], List[JobSuggestion]]:
    """
    Find exact or similar job matches from supported jobs list.
    Returns (exact_match, suggestions)
    """
    query_lower = query.lower().strip()
    
    # Check for exact match
    for job in supported_jobs:
        if job["title"].lower() == query_lower or job["soc_code"] == query:
            return job, []
    
    # If no exact match, find similar titles using string similarity
    similarities = []
    for job in supported_jobs:
        similarity = SequenceMatcher(None, query_lower, job["title"].lower()).ratio()
        similarities.append((job, similarity))
    
    # Sort by similarity and return top suggestions
    similarities.sort(key=lambda x: x[1], reverse=True)
    suggestions = [
        JobSuggestion(title=job["title"], soc_code=job["soc_code"])
        for job, similarity in similarities[:5]  # Top 5 suggestions
        if similarity > 0.3  # Only suggest if similarity > 30%
    ]
    
    return None, suggestions


@router.post("/analyze", response_model=JobAnalysisResponse)
async def analyze_job(
    search_request: JobSearchRequest,
    settings: Settings = Depends(get_settings)
):
    """
    Accepts a job title or SOC code, fetches job postings, and returns structured insights.
    If no exact match is found, returns suggestions.
    """
    query = search_request.query
    location = search_request.location
    
    # Load supported jobs from config
    supported_jobs = settings.supported_jobs
    
    # Find job match or suggestions
    exact_match, suggestions = find_job_match(query, supported_jobs)
    
    # If no exact match, return suggestions
    if not exact_match:
        return JobAnalysisResponse(
            success=True,
            suggestions=suggestions
        )
    
    # Fetch job postings for the matched job
    try:
        raw_postings = await career_api_service.fetch_postings(
            exact_match["soc_code"],
            location,
            settings
        )
        
        # Generate structured report using analysis service
        report = generate_report_from_postings(
            raw_postings,
            exact_match["title"],
            exact_match["soc_code"]
        )
        
        return JobAnalysisResponse(
            success=True,
            data=report
        )
        
    except Exception as e:
        print(f"Error analyzing job postings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze job postings: {str(e)}"
        )


@router.post("/insert", response_model=JobInsertResponse)
async def insert_jobs(
    job_set: List[Dict[str, Any]],
    settings: Settings = Depends(get_settings)
):
    """
    Insert a list of jobs into MongoDB, overwriting duplicates based on JvId.
    """
    try:
        result = await insert_jobs_from_job_set(job_set)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to insert jobs: {str(e)}"
        )


@router.get("/list")
async def list_jobs(
    limit: int = 100,
    skip: int = 0,
    company: str = None,
    location: str = None,
    job_title: str = None,
    settings: Settings = Depends(get_settings)
):
    """
    Retrieve jobs from MongoDB with optional filtering and pagination.
    """
    try:
        # Build filter criteria
        filters = {}
        if company:
            filters["Company"] = {"$regex": company, "$options": "i"}
        if location:
            filters["Location"] = {"$regex": location, "$options": "i"}
        if job_title:
            filters["JobTitle"] = {"$regex": job_title, "$options": "i"}
        
        # Get jobs and total count
        jobs = await get_jobs_by_criteria(limit=limit, skip=skip, **filters)
        total_count = await get_job_count(**filters)
        
        return {
            "success": True,
            "jobs": jobs,
            "total_count": total_count,
            "returned_count": len(jobs),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve jobs: {str(e)}"
        )