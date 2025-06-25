from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any

from app.core.config import Settings, get_settings
from app.models.pydantic_models import (
    JobSearchRequest,
    JobAnalysisResponse,
    JobInsertResponse,
    Job
)
from app.services import career_api_service
from app.db.mongodb import insert_jobs_from_job_set, get_jobs_by_criteria, get_job_count

router = APIRouter()

@router.post("/analyze", response_model=JobAnalysisResponse)
async def analyze_job(
    search_request: JobSearchRequest,
    settings: Settings = Depends(get_settings)
):
    """
    Accepts a SOC code and location, fetches job postings, and returns insights.
    """
    soc_code = search_request.query
    location = search_request.location
    
    raw_postings = await career_api_service.fetch_postings(soc_code, location, settings)
    
    # In S1, we return the raw data. In S2, this will be a full report.
    return JobAnalysisResponse(
        success=True,
        data={
            "searched_title": f"Report for SOC Code: {soc_code}", # Placeholder title
            "soc_code": soc_code,
            "total_postings_analyzed": len(raw_postings),
            "raw_postings": raw_postings
        }
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