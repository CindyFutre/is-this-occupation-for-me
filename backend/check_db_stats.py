#!/usr/bin/env python3
"""
Script to check MongoDB database statistics for job postings.
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def check_db_stats():
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB connection string from environment
    mongodb_url = os.getenv('DATABASE_URL')
    if not mongodb_url:
        print("DATABASE_URL not found in environment variables")
        return
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongodb_url)
    db = client.occupation100
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("Successfully connected to MongoDB")
        
        # Get total count
        total_count = await db.jobs.count_documents({})
        print(f'\nTotal job postings in database: {total_count}')
        
        # Get count by SOC code
        pipeline = [
            {'$group': {'_id': '$soc_code', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        
        soc_counts = await db.jobs.aggregate(pipeline).to_list(None)
        print(f'\nJob postings by SOC code:')
        for item in soc_counts:
            print(f'  {item["_id"]}: {item["count"]} postings')
        
        print(f'\nTotal SOC codes with data: {len(soc_counts)}')
        
        # Get some sample documents to see structure
        sample_docs = await db.jobs.find({}).limit(3).to_list(None)
        if sample_docs:
            print(f'\nSample document fields and values:')
            for i, doc in enumerate(sample_docs):
                print(f'\nDocument {i+1}:')
                for key, value in doc.items():
                    if key == '_id':
                        print(f'  - {key}: {str(value)}')
                    elif isinstance(value, str) and len(value) > 100:
                        print(f'  - {key}: {value[:100]}...')
                    else:
                        print(f'  - {key}: {value}')
                if i >= 1:  # Only show first 2 documents in detail
                    break
        
        # Check specifically for documents with soc_code
        soc_code_docs = await db.jobs.find({"soc_code": {"$exists": True, "$ne": None}}).limit(5).to_list(None)
        print(f'\nDocuments with soc_code field: {len(soc_code_docs)}')
        if soc_code_docs:
            for doc in soc_code_docs:
                print(f'  - JvId: {doc.get("JvId", "N/A")}, soc_code: {doc.get("soc_code", "N/A")}')
        
    except Exception as e:
        print(f"Error connecting to database: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(check_db_stats())