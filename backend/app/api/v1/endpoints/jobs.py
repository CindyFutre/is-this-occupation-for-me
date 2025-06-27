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
from app.services.cache_service import cache_service
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
    
    # Check for cached analysis first
    soc_code = exact_match["soc_code"]
    job_title = exact_match["title"]
    
    cached_report = cache_service.get_cached_analysis(soc_code, job_title)
    if cached_report:
        return JobAnalysisResponse(
            success=True,
            data=cached_report
        )
    
    # Fetch job postings from MongoDB for the matched job
    try:
        # Query MongoDB for jobs with this SOC code
        filters = {}
        
        # Try multiple SOC code field patterns
        filters = {
            "$or": [
                {"soc_code": soc_code},
                {"onet_codes": soc_code},
                {"soc_codes": soc_code},
                {"onet_codes": {"$in": [soc_code]}},
                {"soc_codes": {"$in": [soc_code]}}
            ]
        }
        
        # Get jobs from MongoDB (limit to 100 for analysis)
        raw_postings = await get_jobs_by_criteria(limit=100, **filters)
        
        if not raw_postings:
            # If no jobs found by SOC code, try job title matching
            title_filters = {"JobTitle": {"$regex": job_title, "$options": "i"}}
            raw_postings = await get_jobs_by_criteria(limit=100, **title_filters)
        
        if not raw_postings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No job postings found for {job_title} (SOC {soc_code}) in database"
            )
        
        # Generate structured report using analysis service
        report = generate_report_from_postings(
            raw_postings,
            job_title,
            soc_code
        )
        
        # Cache the analysis results
        cache_service.cache_analysis(soc_code, job_title, report)
        
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


@router.get("/cache/stats")
async def get_cache_stats():
    """
    Get statistics about the analysis cache.
    """
    try:
        stats = cache_service.get_cache_stats()
        return {
            "success": True,
            "cache_stats": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache stats: {str(e)}"
        )


@router.delete("/cache/clear")
async def clear_cache(
    soc_code: str = None,
    job_title: str = None
):
    """
    Clear analysis cache. If soc_code and job_title are provided,
    only clear cache for that specific analysis.
    """
    try:
        removed_count = cache_service.clear_cache(soc_code, job_title)
        return {
            "success": True,
            "message": f"Cleared {removed_count} cached analysis files",
            "removed_count": removed_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )