#!/usr/bin/env python3
"""
Extract normalized terms from job postings in MongoDB and categorize them
using Claude/Sonnet 4.0 based on the existing analysis service.
"""

import asyncio
import json
from typing import List, Dict, Any
from app.db.mongodb import connect_to_mongo, close_mongo_connection, get_database
from app.services.analysis_service import generate_report_from_postings

async def analyze_jobs_by_title(job_title_pattern: str, display_title: str, limit: int = 200):
    """
    Analyze job postings for a specific job title pattern using Claude/Sonnet 4.0.
    
    Args:
        job_title_pattern: Pattern to match job titles (e.g., "Software Developer")
        display_title: Display name for the analysis (e.g., "Software Developers")
        limit: Maximum number of job postings to analyze
    """
    print(f"🔍 Analyzing {display_title} - up to {limit} job postings")
    
    # Connect to MongoDB
    await connect_to_mongo()
    db = get_database()
    
    try:
        # Query job postings by job title pattern (case insensitive)
        cursor = db.jobs.find(
            {"JobTitle": {"$regex": job_title_pattern, "$options": "i"}},
            {"Description": 1, "JobTitle": 1, "Company": 1, "Location": 1}
        ).limit(limit)
        
        postings = await cursor.to_list(length=limit)
        
        if not postings:
            print(f"❌ No job postings found for job title pattern '{job_title_pattern}'")
            return None
        
        print(f"📊 Found {len(postings)} job postings for analysis")
        
        # Generate analysis report using Claude/Sonnet 4.0
        print("🤖 Generating analysis with Claude/Sonnet 4.0...")
        report = generate_report_from_postings(postings, display_title, "N/A")
        
        # Display results
        print(f"\n✅ Analysis Complete for {display_title}")
        print(f"📈 Total postings analyzed: {report.total_postings_analyzed}")
        print(f"🎯 Responsibilities extracted: {len(report.responsibilities)}")
        print(f"🛠️  Skills extracted: {len(report.skills)}")
        print(f"🎓 Qualifications extracted: {len(report.qualifications)}")
        print(f"✨ Unique aspects extracted: {len(report.unique_aspects)}")
        
        # Show top items from each category
        print(f"\n📋 TOP RESPONSIBILITIES:")
        for i, resp in enumerate(report.responsibilities[:5], 1):
            print(f"  {i}. {resp.term} (mentioned {resp.count} times)")
        
        print(f"\n🛠️  TOP SKILLS:")
        for i, skill in enumerate(report.skills[:5], 1):
            print(f"  {i}. {skill.term} (mentioned {skill.count} times)")
        
        print(f"\n🎓 TOP QUALIFICATIONS:")
        for i, qual in enumerate(report.qualifications[:5], 1):
            print(f"  {i}. {qual.term} (mentioned {qual.count} times)")
        
        print(f"\n✨ TOP UNIQUE ASPECTS:")
        for i, aspect in enumerate(report.unique_aspects[:5], 1):
            print(f"  {i}. {aspect.term} (mentioned {aspect.count} times)")
        
        # Save detailed results to JSON file
        safe_title = display_title.replace(' ', '_').replace('/', '_').lower()
        output_file = f"analysis_results_{safe_title}.json"
        
        # Convert to serializable format
        result_data = {
            "job_title": report.searched_title,
            "soc_code": report.soc_code,
            "total_postings_analyzed": report.total_postings_analyzed,
            "analysis_timestamp": asyncio.get_event_loop().time(),
            "categories": {
                "responsibilities": [
                    {
                        "term": item.term,
                        "count": item.count,
                        "context_sentences": item.context_sentences
                    } for item in report.responsibilities
                ],
                "skills": [
                    {
                        "term": item.term,
                        "count": item.count,
                        "context_sentences": item.context_sentences
                    } for item in report.skills
                ],
                "qualifications": [
                    {
                        "term": item.term,
                        "count": item.count,
                        "context_sentences": item.context_sentences
                    } for item in report.qualifications
                ],
                "unique_aspects": [
                    {
                        "term": item.term,
                        "count": item.count,
                        "context_sentences": item.context_sentences
                    } for item in report.unique_aspects
                ]
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Detailed results saved to: {output_file}")
        
        return report
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return None
    
    finally:
        await close_mongo_connection()

async def analyze_multiple_jobs():
    """
    Analyze multiple job types based on common job titles in the database.
    """
    # Common job title patterns to search for
    job_patterns = [
        ("Software Developer", "Software Developers"),
        ("Data Scientist", "Data Scientists"),
        ("Project Manager", "Project Managers"),
        ("Marketing", "Marketing Professionals"),
        ("Sales", "Sales Professionals")
    ]
    
    print(f"🎯 Analyzing {len(job_patterns)} job categories")
    
    for pattern, display_title in job_patterns:
        print(f"\n{'='*60}")
        await analyze_jobs_by_title(pattern, display_title, limit=50)
        print(f"{'='*60}")

async def main():
    """
    Main function to run the analysis.
    """
    print("🚀 Starting Job Analysis with Claude/Sonnet 4.0")
    print("📊 Extracting normalized terms and categorizing them")
    
    # Option 1: Analyze a specific job title
    await analyze_jobs_by_title("Software Developer", "Software Developers", limit=100)
    
    # Option 2: Analyze multiple jobs (uncomment to run)
    # await analyze_multiple_jobs()
    
    print("\n🎉 Analysis complete!")

if __name__ == "__main__":
    asyncio.run(main())