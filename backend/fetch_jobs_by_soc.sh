#!/bin/bash

# Script to fetch 100 job postings for each SOC code using the API endpoint
# This ensures we have adequate data for analysis

echo "🚀 Starting job fetching for all SOC codes..."

# Array of SOC codes from our supported_jobs.json
SOC_CODES=("15-1252.00" "15-2051.00" "13-1082.00" "27-1024.00" "29-1141.00")
JOB_TITLES=("Software Developers" "Data Scientists" "Project Management Specialists" "Graphic Designers" "Registered Nurses")

# Array of locations to get diverse job postings
LOCATIONS=("San Francisco,CA" "New York,NY" "Los Angeles,CA" "Chicago,IL" "Austin,TX" "Seattle,WA" "Boston,MA" "Denver,CO")

echo "📊 Target: 100 jobs per SOC code (5 SOC codes = 500 total jobs)"
echo ""

# Loop through each SOC code
for i in "${!SOC_CODES[@]}"; do
    SOC_CODE="${SOC_CODES[$i]}"
    JOB_TITLE="${JOB_TITLES[$i]}"
    
    echo "🔍 Fetching jobs for: $JOB_TITLE (SOC: $SOC_CODE)"
    
    # Fetch from multiple locations to get diverse results
    for LOCATION in "${LOCATIONS[@]}"; do
        echo "  📍 Fetching from $LOCATION..."
        
        # Use the analyze endpoint with the exact job title to trigger job fetching
        curl -s -X POST "http://localhost:8001/api/v1/jobs/analyze" \
          -H "Content-Type: application/json" \
          -d "{\"query\": \"$JOB_TITLE\", \"location\": \"$LOCATION\"}" > /dev/null
        
        echo "    ✅ Request sent"
        
        # Small delay between requests to be respectful to the API
        sleep 2
    done
    
    echo "  🎉 Completed fetching for $JOB_TITLE"
    echo ""
done

echo "✅ Job fetching complete!"
echo "📈 Checking final database count..."

# Check final count
curl -s "http://localhost:8001/api/v1/jobs/list?limit=1" | grep -o '"total_count":[0-9]*' | cut -d':' -f2