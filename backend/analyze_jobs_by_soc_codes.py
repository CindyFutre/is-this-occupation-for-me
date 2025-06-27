#!/usr/bin/env python3
"""
Script to analyze jobs by specific SOC codes using Claude/Sonnet 4.0
"""

import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient
from app.services.analysis_service import HybridTermAnalyzer
from app.core.config import settings

async def find_available_soc_codes():
    """Find all available SOC codes in the database"""
    client = AsyncIOMotorClient(settings.database_url)
    db = client.occupation100
    collection = db.jobs
    
    print("🔍 Searching for available SOC codes in the database...")
    
    # Find all unique SOC codes
    pipeline = [
        {"$match": {"soc_code": {"$exists": True, "$ne": None}}},
        {"$group": {"_id": "$soc_code", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    soc_codes = await collection.aggregate(pipeline).to_list(length=None)
    
    print(f"📊 Found {len(soc_codes)} unique SOC codes:")
    for soc in soc_codes:
        print(f"  - {soc['_id']}: {soc['count']} jobs")
    
    # Also check onet_codes and soc_codes arrays
    print("\n🔍 Checking for SOC codes in arrays...")
    
    # Check onet_codes
    pipeline_onet = [
        {"$match": {"onet_codes": {"$exists": True, "$ne": None, "$ne": []}}},
        {"$unwind": "$onet_codes"},
        {"$group": {"_id": "$onet_codes", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    onet_codes = await collection.aggregate(pipeline_onet).to_list(length=None)
    print(f"📊 Found {len(onet_codes)} unique O*NET codes:")
    for code in onet_codes[:10]:  # Show top 10
        print(f"  - {code['_id']}: {code['count']} jobs")
    
    # Check soc_codes arrays
    pipeline_soc_array = [
        {"$match": {"soc_codes": {"$exists": True, "$ne": None, "$ne": []}}},
        {"$unwind": "$soc_codes"},
        {"$group": {"_id": "$soc_codes", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    soc_codes_array = await collection.aggregate(pipeline_soc_array).to_list(length=None)
    print(f"📊 Found {len(soc_codes_array)} unique SOC codes in arrays:")
    for code in soc_codes_array[:10]:  # Show top 10
        print(f"  - {code['_id']}: {code['count']} jobs")
    
    client.close()
    return soc_codes, onet_codes, soc_codes_array

async def analyze_jobs_by_soc_code(soc_code: str, limit: int = 100):
    """Analyze jobs for a specific SOC code using Claude/Sonnet 4.0"""
    client = AsyncIOMotorClient(settings.database_url)
    db = client.occupation100
    collection = db.jobs
    
    print(f"\n🎯 Analyzing jobs for SOC code: {soc_code}")
    
    # Try multiple query patterns to find jobs with this SOC code
    queries = [
        {"soc_code": soc_code},
        {"onet_codes": soc_code},
        {"soc_codes": soc_code},
        {"onet_codes": {"$in": [soc_code]}},
        {"soc_codes": {"$in": [soc_code]}}
    ]
    
    jobs = []
    for query in queries:
        cursor = collection.find(query).limit(limit)
        batch = await cursor.to_list(length=limit)
        if batch:
            jobs.extend(batch)
            print(f"  ✅ Found {len(batch)} jobs with query: {query}")
            break
    else:
        print(f"  ❌ No jobs found for SOC code: {soc_code}")
        await client.close()
        return None
    
    # Remove duplicates based on JvId
    unique_jobs = {}
    for job in jobs:
        unique_jobs[job.get('JvId', job.get('_id'))] = job
    jobs = list(unique_jobs.values())
    
    print(f"  📊 Analyzing {len(jobs)} unique jobs...")
    
    # Initialize the analyzer
    analyzer = HybridTermAnalyzer()
    
    # Extract job descriptions
    job_descriptions = []
    for job in jobs:
        description = job.get('Description', '') or job.get('description', '')
        if description:
            job_descriptions.append(description)
    
    if not job_descriptions:
        print(f"  ⚠️ No job descriptions found for SOC code: {soc_code}")
        client.close()
        return None
    
    print(f"  🤖 Using Claude/Sonnet 4.0 to analyze {len(job_descriptions)} job descriptions...")
    
    # Analyze with Claude
    # Get a representative job title for this SOC code
    job_title = jobs[0].get('JobTitle', f'SOC {soc_code}')
    
    # Combine job descriptions into one text
    combined_text = "\n\n--- JOB POSTING ---\n".join(job_descriptions)
    
    results = analyzer.extract_and_categorize_with_claude(combined_text, job_title)
    
    # Create analysis report
    report = {
        "soc_code": soc_code,
        "total_jobs_found": len(jobs),
        "total_descriptions_analyzed": len(job_descriptions),
        "analysis_results": results,
        "sample_job_titles": [job.get('JobTitle', 'N/A') for job in jobs[:5]]
    }
    
    client.close()
    return report

async def main():
    """Main function to analyze the specific SOC codes"""
    
    # First, find all available SOC codes
    await find_available_soc_codes()
    
    # The SOC codes mentioned by the user
    target_soc_codes = [
        "47-2111.00",  # Electricians
        "29-1141.00",  # Registered Nurses
        "11-3031.00"   # Financial Managers
    ]
    
    print(f"\n🎯 Analyzing the 3 SOC codes you mentioned:")
    
    results = {}
    for soc_code in target_soc_codes:
        result = await analyze_jobs_by_soc_code(soc_code)
        if result:
            results[soc_code] = result
            
            # Save individual results
            filename = f"analysis_results_soc_{soc_code.replace('-', '_').replace('.', '_')}.json"
            with open(filename, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"  💾 Results saved to: {filename}")
    
    # Save combined results
    if results:
        with open("analysis_results_all_soc_codes.json", 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Combined results saved to: analysis_results_all_soc_codes.json")
        
        # Print summary
        print(f"\n📋 ANALYSIS SUMMARY:")
        for soc_code, result in results.items():
            print(f"  🏷️ SOC {soc_code}: {result['total_jobs_found']} jobs, {result['total_descriptions_analyzed']} descriptions analyzed")
            print(f"     Sample titles: {', '.join(result['sample_job_titles'])}")
    else:
        print("\n❌ No results found for any of the specified SOC codes")

if __name__ == "__main__":
    asyncio.run(main())