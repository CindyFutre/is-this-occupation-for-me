'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface AnalyzedTerm {
  term: string;
  count: number;
  context_sentences: string[];
}

interface SOCAnalysisResult {
  soc_code: string;
  total_jobs_found: number;
  total_descriptions_analyzed: number;
  analysis_results: {
    responsibilities: AnalyzedTerm[];
    skills: AnalyzedTerm[];
    qualifications: AnalyzedTerm[];
    unique_aspects: AnalyzedTerm[];
  };
  sample_job_titles: string[];
}

interface AllSOCResults {
  [socCode: string]: SOCAnalysisResult;
}

const SOC_CODE_NAMES: { [key: string]: string } = {
  '47-2111.00': 'Electricians',
  '29-1141.00': 'Registered Nurses',
  '11-3031.00': 'Financial Managers',
  '15-1252.00': 'Software Developers'
};

export default function SOCAnalysisPage() {
  const [socResults, setSOCResults] = useState<AllSOCResults>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedSOC, setSelectedSOC] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('responsibilities');

  useEffect(() => {
    const fetchSOCResults = async () => {
      try {
        // Fetch the combined results from the backend
        const response = await fetch('/api/soc-analysis');
        if (!response.ok) {
          throw new Error('Failed to fetch SOC analysis results');
        }
        const data = await response.json();
        setSOCResults(data);
        setSelectedSOC(Object.keys(data)[0] || '');
      } catch (err) {
        console.error('Error fetching SOC results:', err);
        setError('Failed to load SOC analysis results');
      } finally {
        setLoading(false);
      }
    };

    fetchSOCResults();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 text-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto mb-4"></div>
          <p className="text-slate-300">Loading SOC analysis results...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 text-slate-100 flex items-center justify-center">
        <Card className="bg-red-900/20 border-red-700 max-w-md">
          <CardContent className="pt-6">
            <p className="text-red-300">{error}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const renderTermsList = (terms: AnalyzedTerm[], category: string) => {
    const getEmoji = (category: string) => {
      switch (category) {
        case 'responsibilities': return '📋';
        case 'skills': return '🛠️';
        case 'qualifications': return '🎓';
        case 'unique_aspects': return '✨';
        default: return '📄';
      }
    };

    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-2xl">{getEmoji(category)}</span>
          <h3 className="text-xl font-semibold text-slate-100 capitalize">
            {category.replace('_', ' ')}
          </h3>
          <Badge variant="secondary" className="bg-slate-700 text-slate-300">
            {terms.length} items
          </Badge>
        </div>
        <div className="grid gap-3">
          {terms.map((term, index) => (
            <Card key={index} className="bg-slate-800 border-slate-700">
              <CardContent className="pt-4">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-medium text-slate-100 flex-1">{term.term}</h4>
                  <Badge variant="outline" className="border-blue-500 text-blue-400 ml-2">
                    {term.count} jobs
                  </Badge>
                </div>
                {term.context_sentences.length > 0 && (
                  <div className="mt-3">
                    <p className="text-xs text-slate-400 mb-2">Context examples:</p>
                    <div className="space-y-1">
                      {term.context_sentences.slice(0, 2).map((sentence, idx) => (
                        <p key={idx} className="text-sm text-slate-300 italic border-l-2 border-slate-600 pl-3">
                          "{sentence.length > 150 ? sentence.substring(0, 150) + '...' : sentence}"
                        </p>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  };

  const currentResult = socResults[selectedSOC];

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            SOC Code Analysis Results
          </h1>
          <p className="text-lg text-slate-300 max-w-3xl mx-auto">
            Claude/Sonnet 4.0 analysis of job postings across 4 major occupations. 
            Each analysis includes normalized terms, frequency counts, and context sentences.
          </p>
        </div>

        {/* Overview Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {Object.entries(socResults).map(([socCode, result]) => (
            <Card 
              key={socCode} 
              className={`bg-slate-800 border-slate-700 cursor-pointer transition-colors ${
                selectedSOC === socCode ? 'ring-2 ring-blue-500' : 'hover:bg-slate-750'
              }`}
              onClick={() => setSelectedSOC(socCode)}
            >
              <CardContent className="pt-6">
                <div className="text-center">
                  <h3 className="font-semibold text-slate-100 mb-1">
                    {SOC_CODE_NAMES[socCode] || socCode}
                  </h3>
                  <p className="text-sm text-slate-400 mb-2">SOC {socCode}</p>
                  <div className="space-y-1">
                    <Badge variant="outline" className="border-green-500 text-green-400">
                      {result.total_jobs_found} jobs
                    </Badge>
                    <p className="text-xs text-slate-500">
                      {result.total_descriptions_analyzed} analyzed
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Selected SOC Details */}
        {currentResult && (
          <>
            <Card className="bg-slate-800 border-slate-700 mb-6">
              <CardHeader>
                <CardTitle className="text-slate-100">
                  {SOC_CODE_NAMES[selectedSOC] || selectedSOC} (SOC {selectedSOC})
                </CardTitle>
                <CardDescription className="text-slate-400">
                  Analysis of {currentResult.total_jobs_found} job postings with {currentResult.total_descriptions_analyzed} descriptions analyzed using Claude/Sonnet 4.0
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="mb-4">
                  <h4 className="font-medium text-slate-200 mb-2">Sample Job Titles:</h4>
                  <div className="flex flex-wrap gap-2">
                    {currentResult.sample_job_titles.slice(0, 5).map((title, idx) => (
                      <Badge key={idx} variant="secondary" className="bg-slate-700 text-slate-300">
                        {title}
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Category Navigation */}
            <div className="flex flex-wrap gap-2 mb-6">
              {[
                { key: 'responsibilities', label: '📋 Responsibilities', emoji: '📋' },
                { key: 'skills', label: '🛠️ Skills', emoji: '🛠️' },
                { key: 'qualifications', label: '🎓 Qualifications', emoji: '🎓' },
                { key: 'unique_aspects', label: '✨ Unique Aspects', emoji: '✨' }
              ].map((category) => (
                <Button
                  key={category.key}
                  variant={selectedCategory === category.key ? "default" : "outline"}
                  onClick={() => setSelectedCategory(category.key)}
                  className={`${
                    selectedCategory === category.key 
                      ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                      : 'bg-slate-800 border-slate-600 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  {category.label}
                </Button>
              ))}
            </div>

            {/* Category Content */}
            <div className="mt-6">
              {renderTermsList(
                currentResult.analysis_results[selectedCategory as keyof typeof currentResult.analysis_results], 
                selectedCategory
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}