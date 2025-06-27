#!/usr/bin/env python3
"""
Script to re-analyze existing job postings in MongoDB using Claude Sonnet 4.0.
This will generate new insights reports for all SOC codes with job data.
"""
import asyncio
import os
import sys
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.analysis_service import generate_report_from_postings
from app.core.config import settings

async def reanalyze_all_jobs():
    """Re-analyze all job postings in the database using Claude Sonnet 4.0."""
    
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB connection string from environment
    mongodb_url = os.getenv('DATABASE_URL')
    if not mongodb_url:
        print("❌ DATABASE_URL not found in environment variables")
        return
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongodb_url)
    db = client.occupation100
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✅ Successfully connected to MongoDB")
        
        # Get total count
        total_count = await db.jobs.count_documents({})
        print(f"📊 Total job postings in database: {total_count}")
        
        # Get unique SOC codes with job counts
        pipeline = [
            {'$group': {'_id': '$soc_code', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        
        soc_counts = await db.jobs.aggregate(pipeline).to_list(None)
        print(f"🎯 Found {len(soc_counts)} SOC codes with job data")
        
        # Process each SOC code
        for soc_info in soc_counts:
            soc_code = soc_info['_id']
            job_count = soc_info['count']
            
            if not soc_code:
                print("⚠️ Skipping jobs with missing SOC code")
                continue
                
            print(f"\n🔍 Processing SOC {soc_code} ({job_count} jobs)...")
            
            # Get all jobs for this SOC code
            jobs_cursor = db.jobs.find({'soc_code': soc_code})
            jobs = await jobs_cursor.to_list(None)
            
            if not jobs:
                print(f"  ⚠️ No jobs found for SOC {soc_code}")
                continue
            
            # Find the job title from the first job
            job_title = "Unknown"
            for job in jobs:
                if job.get('JobTitle'):
                    job_title = job['JobTitle']
                    break
                elif job.get('job_title'):
                    job_title = job['job_title']
                    break
            
            print(f"  📝 Job Title: {job_title}")
            print(f"  🤖 Analyzing with Claude Sonnet 4.0...")
            
            try:
                # Generate new insights report using Claude
                report = generate_report_from_postings(jobs, job_title, soc_code)
                
                # Convert report to dict for storage
                report_dict = {
                    'soc_code': report.soc_code,
                    'searched_title': report.searched_title,
                    'total_postings_analyzed': report.total_postings_analyzed,
                    'responsibilities': [
                        {
                            'term': term.term,
                            'count': term.count,
                            'context_sentences': term.context_sentences
                        } for term in report.responsibilities
                    ],
                    'skills': [
                        {
                            'term': term.term,
                            'count': term.count,
                            'context_sentences': term.context_sentences
                        } for term in report.skills
                    ],
                    'qualifications': [
                        {
                            'term': term.term,
                            'count': term.count,
                            'context_sentences': term.context_sentences
                        } for term in report.qualifications
                    ],
                    'unique_aspects': [
                        {
                            'term': term.term,
                            'count': term.count,
                            'context_sentences': term.context_sentences
                        } for term in report.unique_aspects
                    ],
                    'analysis_timestamp': asyncio.get_event_loop().time(),
                    'analysis_method': 'claude_sonnet_4'
                }
                
                # Store the analysis results
                await db.job_insights.replace_one(
                    {'soc_code': soc_code},
                    report_dict,
                    upsert=True
                )
                
                print(f"  ✅ Analysis complete and stored!")
                print(f"     - Responsibilities: {len(report.responsibilities)}")
                print(f"     - Skills: {len(report.skills)}")
                print(f"     - Qualifications: {len(report.qualifications)}")
                print(f"     - Unique Aspects: {len(report.unique_aspects)}")
                
            except Exception as e:
                print(f"  ❌ Error analyzing SOC {soc_code}: {e}")
                continue
        
        print(f"\n🎉 Re-analysis complete! Processed {len(soc_counts)} SOC codes.")
        
        # Show final statistics
        insights_count = await db.job_insights.count_documents({})
        print(f"📈 Total job insights reports in database: {insights_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    print("🚀 Starting job re-analysis with Claude Sonnet 4.0...")
    print("=" * 60)
    asyncio.run(reanalyze_all_jobs())