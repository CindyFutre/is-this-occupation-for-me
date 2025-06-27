import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    // Path to the combined SOC analysis results
    const resultsPath = path.join(process.cwd(), '..', 'backend', 'analysis_results_all_soc_codes.json');
    
    console.log('Looking for SOC results at:', resultsPath);
    
    // Check if file exists
    if (!fs.existsSync(resultsPath)) {
      return NextResponse.json(
        { error: 'SOC analysis results not found. Please run the analysis first.' },
        { status: 404 }
      );
    }

    // Read and parse the results
    const resultsData = fs.readFileSync(resultsPath, 'utf8');
    const socResults = JSON.parse(resultsData);

    return NextResponse.json(socResults);
  } catch (error) {
    console.error('Error reading SOC analysis results:', error);
    return NextResponse.json(
      { error: 'Failed to load SOC analysis results' },
      { status: 500 }
    );
  }
}