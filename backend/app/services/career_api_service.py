import httpx
from fastapi import HTTPException, status
from typing import List, Dict, Any
import asyncio

from app.core.config import Settings
from app.db.mongodb import insert_jobs_from_job_set
from app.models.pydantic_models import JobInsertResponse

async def fetch_postings(soc_code: str, location: str, settings: Settings) -> List[Dict[str, Any]]:
    """
    Fetches job postings from the CareerOneStop API for a given SOC code and location.
    """
    if not settings.onestop_api_key or not settings.onestop_user_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CareerOneStop API credentials are not configured."
        )

    userId = settings.onestop_user_id
    keyword=soc_code
    radius = "50"
    sortColumns = "0"
    sortOrder = "0"
    startRecord = "0"
    pageSize = "200"
    days = "0"
    showFilters = "true"
    enableJobDescriptionSnippet = "true"
    enableMetaData = "true"

    # Build URL exactly like the working example - no URL encoding needed
    api_url = f"https://api.careeronestop.org/v1/jobsearch/{userId}/{keyword}/{location}/{radius}/{sortColumns}/{sortOrder}/{startRecord}/{pageSize}/{days}?showFilters={showFilters}&enableJobDescriptionSnippet={enableJobDescriptionSnippet}&enableMetaData={enableMetaData}"
    
    headers = {
        "Authorization": f"Bearer {settings.onestop_api_key}"
    }
    
    params = {
        "showFilters": "true",
        "enableJobDescriptionSnippet": "true",
        "enableMetaData": "true"
    }

    print(f"Fetching job postings for {location} with SOC code {soc_code}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            
            data = response.json()
            job_set = data.get("Jobs", [])
            print(f"Successfully fetched {len(job_set)} postings for {location}.")
            
            # Insert jobs into MongoDB
            if job_set:
                insert_result = await insert_jobs_from_job_set(job_set)
                print(f"Database insertion result: {insert_result.message}")
            
            return job_set

        except httpx.HTTPStatusError as e:
            print(f"API request failed for {location} with status {e.response.status_code}: {e.response.text}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to fetch data from CareerOneStop API. Status: {e.response.status_code}"
            )
        except httpx.RequestError as e:
            print(f"An error occurred while requesting from CareerOneStop API for {location}: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to connect to CareerOneStop API."
            )