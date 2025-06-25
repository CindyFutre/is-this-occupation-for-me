from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.pydantic_models import Job, JobInsertResponse
from typing import List, Dict, Any
from pymongo import UpdateOne

client: AsyncIOMotorClient = None


async def connect_to_mongo():
    """Create database connection"""
    global client
    client = AsyncIOMotorClient(settings.database_url)


async def close_mongo_connection():
    """Close database connection"""
    global client
    if client:
        client.close()


def get_database():
    """Get the database instance"""
    return client.occupation100


def get_jobs_collection():
    """Get the jobs collection"""
    return get_database().jobs


async def insert_jobs_from_job_set(job_set: List[Dict[str, Any]]) -> JobInsertResponse:
    """
    Insert jobs from job_set into MongoDB, overwriting duplicates based on JvId.
    
    Args:
        job_set: List of job dictionaries from the CareerOneStop API
        
    Returns:
        JobInsertResponse with operation statistics
    """
    if not job_set:
        return JobInsertResponse(
            success=True,
            inserted_count=0,
            updated_count=0,
            total_processed=0,
            message="No jobs to process"
        )
    
    collection = get_jobs_collection()
    
    # Prepare bulk operations for upsert (insert or update)
    operations = []
    
    for job_data in job_set:
        try:
            # Validate and parse job data using Pydantic model
            job = Job(**job_data)
            
            # Convert to dict for MongoDB insertion
            job_dict = job.model_dump(by_alias=True)
            
            # Create upsert operation using JvId as the unique identifier
            operation = UpdateOne(
                {"JvId": job_dict["JvId"]},  # Filter by JvId
                {"$set": job_dict},         # Update/insert the document
                upsert=True                 # Create if doesn't exist
            )
            operations.append(operation)
            
        except Exception as e:
            print(f"Error processing job data: {job_data}. Error: {e}")
            continue
    
    if not operations:
        return JobInsertResponse(
            success=False,
            inserted_count=0,
            updated_count=0,
            total_processed=0,
            message="No valid jobs to process"
        )
    
    try:
        # Execute bulk operations
        result = await collection.bulk_write(operations)
        
        return JobInsertResponse(
            success=True,
            inserted_count=result.upserted_count,
            updated_count=result.modified_count,
            total_processed=len(operations),
            message=f"Successfully processed {len(operations)} jobs: {result.upserted_count} inserted, {result.modified_count} updated"
        )
        
    except Exception as e:
        print(f"Error during bulk write operation: {e}")
        return JobInsertResponse(
            success=False,
            inserted_count=0,
            updated_count=0,
            total_processed=0,
            message=f"Database operation failed: {str(e)}"
        )


async def get_jobs_by_criteria(limit: int = 100, skip: int = 0, **filters) -> List[Dict[str, Any]]:
    """
    Retrieve jobs from MongoDB with optional filtering.
    
    Args:
        limit: Maximum number of jobs to return
        skip: Number of jobs to skip (for pagination)
        **filters: Additional filter criteria
        
    Returns:
        List of job documents
    """
    collection = get_jobs_collection()
    
    try:
        cursor = collection.find(filters).skip(skip).limit(limit)
        jobs = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string for JSON serialization
        for job in jobs:
            if '_id' in job:
                job['_id'] = str(job['_id'])
                
        return jobs
        
    except Exception as e:
        print(f"Error retrieving jobs: {e}")
        return []


async def get_job_count(**filters) -> int:
    """
    Get the total count of jobs matching the given filters.
    
    Args:
        **filters: Filter criteria
        
    Returns:
        Total count of matching jobs
    """
    collection = get_jobs_collection()
    
    try:
        count = await collection.count_documents(filters)
        return count
        
    except Exception as e:
        print(f"Error counting jobs: {e}")
        return 0