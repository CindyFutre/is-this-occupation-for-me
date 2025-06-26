import httpx
from fastapi import HTTPException, status
from typing import List, Dict, Any
import asyncio

from app.core.config import Settings
from app.db.mongodb import insert_jobs_from_job_set
from app.models.pydantic_models import JobInsertResponse

async def fetch_job_details(job_id: str, settings: Settings) -> Dict[str, Any]:
    """
    Fetches detailed job information from the CareerOneStop API for a specific job ID.
    """
    if not settings.onestop_api_key or not settings.onestop_user_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CareerOneStop API credentials are not configured."
        )

    user_id = settings.onestop_user_id
    url = f"https://api.careeronestop.org/v1/jobsearch/{user_id}/{job_id}"
    
    headers = {
        "Authorization": f"Bearer {settings.onestop_api_key}"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            
            data = response.json()
            return data

        except httpx.HTTPStatusError as e:
            print(f"Failed to fetch job details for job ID {job_id} with status {e.response.status_code}: {e.response.text}")
            return {}
        except httpx.RequestError as e:
            print(f"An error occurred while requesting job details for job ID {job_id}: {e}")
            return {}

async def enrich_job_with_details(job: Dict[str, Any], settings: Settings) -> Dict[str, Any]:
    """
    Enriches a job posting with detailed information from the job details API.
    """
    job_id = job.get("JvId")
    if not job_id:
        return job
    
    job_details = await fetch_job_details(job_id, settings)
    
    if job_details:
        # Add detailed information to the job
        job["Description"] = job_details.get("Description", "")
        job["DatePosted"] = job_details.get("DatePosted", "")
        job["OnetCodes"] = job_details.get("OnetCodes", [])
        job["MetaData"] = job_details.get("MetaData", {})
        
        # Extract SOC codes from OnetCodes and add to top level
        onet_codes = job_details.get("OnetCodes", [])
        if onet_codes:
            job["soc_codes"] = onet_codes
    
    return job

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
            
            # Enrich each job with detailed information
            if job_set:
                print(f"Enriching {len(job_set)} jobs with detailed information...")
                enriched_jobs = []
                
                # Process jobs in batches to avoid overwhelming the API
                batch_size = 10
                for i in range(0, len(job_set), batch_size):
                    batch = job_set[i:i + batch_size]
                    
                    # Create tasks for concurrent processing of the batch
                    tasks = [enrich_job_with_details(job, settings) for job in batch]
                    enriched_batch = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Filter out any exceptions and add successful enrichments
                    for enriched_job in enriched_batch:
                        if not isinstance(enriched_job, Exception):
                            enriched_jobs.append(enriched_job)
                    
                    print(f"Processed batch {i//batch_size + 1}/{(len(job_set) + batch_size - 1)//batch_size}")
                    
                    # Small delay between batches to be respectful to the API
                    if i + batch_size < len(job_set):
                        await asyncio.sleep(0.5)
                
                print(f"Successfully enriched {len(enriched_jobs)} jobs with detailed information.")
                
                # Insert enriched jobs into MongoDB
                if enriched_jobs:
                    insert_result = await insert_jobs_from_job_set(enriched_jobs)
                    print(f"Database insertion result: {insert_result.message}")
                
                return enriched_jobs
            
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