#!/usr/bin/env python3
"""
Script to fetch 100 job postings for each supported SOC code.
This ensures we have adequate data for analysis.
"""

import asyncio
import json
from pathlib import Path
from app.core.config import Settings
from app.services.career_api_service import fetch_postings

async def fetch_jobs_for_all_soc_codes():
    """Fetch 100 job postings for each supported SOC code."""
    
    # Load settings
    settings = Settings()
    
    # Load supported jobs
    config_path = Path(__file__).parent / "config" / "supported_jobs.json"
    with open(config_path, "r") as f:
        supported_jobs = json.load(f)
    
    print(f"Found {len(supported_jobs)} supported job titles:")
    for job in supported_jobs:
        print(f"  - {job['title']} ({job['soc_code']})")
    
    print("\nFetching 100 job postings for each SOC code...")
    
    # Fetch jobs for each SOC code
    total_fetched = 0
    for job in supported_jobs:
        title = job["title"]
        soc_code = job["soc_code"]
        
        print(f"\n🔍 Fetching jobs for {title} (SOC: {soc_code})...")
        
        try:
            # Fetch from multiple locations to get more diverse results
            locations = [
                "San Francisco,CA",
                "New York,NY", 
                "Los Angeles,CA",
                "Chicago,IL",
                "Austin,TX"
            ]
            
            job_count = 0
            for location in locations:
                if job_count >= 100:
                    break
                    
                print(f"  📍 Fetching from {location}...")
                jobs = await fetch_postings(soc_code, location, settings)
                job_count += len(jobs)
                total_fetched += len(jobs)
                print(f"    ✅ Got {len(jobs)} jobs (total for {title}: {job_count})")
                
                # Small delay between requests to be respectful
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"    ❌ Error fetching jobs for {title}: {e}")
    
    print(f"\n🎉 Total jobs fetched: {total_fetched}")
    print("✅ Job fetching complete!")

if __name__ == "__main__":
    asyncio.run(fetch_jobs_for_all_soc_codes())