#!/usr/bin/env python3
"""
Script to fetch 100 job postings for each of the 100 SOC codes.
This will give us 10,000 total job postings for comprehensive analysis.
"""

import asyncio
import csv
import time
from pathlib import Path
from app.core.config import Settings
from app.services.career_api_service import fetch_postings

async def fetch_jobs_for_all_100_soc_codes():
    """Fetch 100 job postings for each of the 100 SOC codes."""
    
    # Load settings
    settings = Settings()
    
    # Load all 100 SOC codes from CSV
    config_path = Path(__file__).parent / "config" / "onet_soc_codes.csv"
    supported_jobs = []
    
    with open(config_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 1:
                data = row[0]
                if ',' in data:
                    title, soc_code = data.rsplit(',', 1)
                    supported_jobs.append({"title": title.strip(), "soc_code": soc_code.strip()})
    
    print(f"🎯 Target: 100 jobs × {len(supported_jobs)} SOC codes = {len(supported_jobs) * 100} total jobs")
    print(f"📋 Found {len(supported_jobs)} SOC codes to process")
    print()
    
    # Locations to fetch from (diverse geographic coverage)
    locations = [
        "San Francisco,CA", "New York,NY", "Los Angeles,CA", "Chicago,IL", 
        "Austin,TX", "Seattle,WA", "Boston,MA", "Denver,CO", "Atlanta,GA", 
        "Miami,FL", "Phoenix,AZ", "Philadelphia,PA", "Dallas,TX", "Houston,TX"
    ]
    
    total_fetched = 0
    successful_soc_codes = 0
    failed_soc_codes = []
    
    # Process each SOC code
    for i, job in enumerate(supported_jobs, 1):
        title = job["title"]
        soc_code = job["soc_code"]
        
        print(f"🔍 [{i}/{len(supported_jobs)}] Processing: {title} (SOC: {soc_code})")
        
        try:
            jobs_for_this_soc = 0
            
            # Try multiple locations until we get enough jobs
            for location in locations:
                if jobs_for_this_soc >= 100:
                    break
                    
                print(f"  📍 Fetching from {location}...")
                jobs = await fetch_postings(soc_code, location, settings)
                jobs_count = len(jobs)
                jobs_for_this_soc += jobs_count
                total_fetched += jobs_count
                
                print(f"    ✅ Got {jobs_count} jobs (total for {title}: {jobs_for_this_soc})")
                
                # Small delay between requests to be respectful
                await asyncio.sleep(1)
            
            if jobs_for_this_soc > 0:
                successful_soc_codes += 1
                print(f"  🎉 Completed {title}: {jobs_for_this_soc} jobs")
            else:
                failed_soc_codes.append(f"{title} ({soc_code})")
                print(f"  ⚠️  No jobs found for {title}")
                
        except Exception as e:
            failed_soc_codes.append(f"{title} ({soc_code}) - Error: {str(e)}")
            print(f"  ❌ Error processing {title}: {e}")
        
        print()
        
        # Progress update every 10 SOC codes
        if i % 10 == 0:
            print(f"📊 Progress: {i}/{len(supported_jobs)} SOC codes processed")
            print(f"📈 Total jobs fetched so far: {total_fetched}")
            print(f"✅ Successful SOC codes: {successful_soc_codes}")
            print(f"❌ Failed SOC codes: {len(failed_soc_codes)}")
            print("-" * 50)
    
    # Final summary
    print("🎉 JOB FETCHING COMPLETE!")
    print("=" * 50)
    print(f"📊 Final Statistics:")
    print(f"  • Total SOC codes processed: {len(supported_jobs)}")
    print(f"  • Successful SOC codes: {successful_soc_codes}")
    print(f"  • Failed SOC codes: {len(failed_soc_codes)}")
    print(f"  • Total jobs fetched: {total_fetched}")
    print(f"  • Average jobs per successful SOC: {total_fetched / successful_soc_codes if successful_soc_codes > 0 else 0:.1f}")
    
    if failed_soc_codes:
        print(f"\n❌ Failed SOC codes ({len(failed_soc_codes)}):")
        for failed in failed_soc_codes[:10]:  # Show first 10
            print(f"  - {failed}")
        if len(failed_soc_codes) > 10:
            print(f"  ... and {len(failed_soc_codes) - 10} more")
    
    print("\n✅ Ready for Sprint 2 verification with comprehensive dataset!")

if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(fetch_jobs_for_all_100_soc_codes())
    end_time = time.time()
    print(f"\n⏱️  Total execution time: {(end_time - start_time) / 60:.1f} minutes")