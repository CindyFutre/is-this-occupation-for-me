'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

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

    const getCategoryColor = (category: string) => {
      switch (category) {
        case 'responsibilities': return 'from-blue-500 to-cyan-500';
        case 'skills': return 'from-green-500 to-emerald-500';
        case 'qualifications': return 'from-purple-500 to-violet-500';
        case 'unique_aspects': return 'from-orange-500 to-amber-500';
        default: return 'from-gray-500 to-slate-500';
      }
    };

    const getBadgeColor = (category: string) => {
      switch (category) {
        case 'responsibilities': return 'border-blue-400 text-blue-300 bg-blue-950/30';
        case 'skills': return 'border-green-400 text-green-300 bg-green-950/30';
        case 'qualifications': return 'border-purple-400 text-purple-300 bg-purple-950/30';
        case 'unique_aspects': return 'border-orange-400 text-orange-300 bg-orange-950/30';
        default: return 'border-gray-400 text-gray-300 bg-gray-950/30';
      }
    };

    return (
      <div className="space-y-6">
        {/* Category Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className={`p-3 rounded-xl bg-gradient-to-br ${getCategoryColor(category)} shadow-lg`}>
            <span className="text-2xl">{getEmoji(category)}</span>
          </div>
          <div>
            <h3 className="text-2xl font-bold text-slate-100 capitalize">
              {category.replace('_', ' ')}
            </h3>
            <p className="text-slate-400">
              {terms.length} {terms.length === 1 ? 'item' : 'items'} found in job analysis
            </p>
          </div>
        </div>

        {/* Enhanced Table */}
        <Card className="bg-slate-800/50 border-slate-700 shadow-xl">
          <Table>
            <TableHeader>
              <TableRow className="border-slate-700 hover:bg-slate-800/50">
                <TableHead className="text-slate-300 font-semibold py-4 px-6" style={{ width: '25%' }}>
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{getEmoji(category)}</span>
                    Term
                  </div>
                </TableHead>
                <TableHead className="text-slate-300 font-semibold py-4 px-6 text-center" style={{ width: '50%' }}>
                  Frequency
                </TableHead>
                <TableHead className="text-slate-300 font-semibold py-4 px-6" style={{ width: '25%' }}>
                  Context Examples
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {terms.map((term, index) => (
                <TableRow
                  key={index}
                  className="border-slate-700 hover:bg-slate-800/30 transition-colors duration-200"
                >
                  <TableCell className="py-8 px-6">
                    <div className="font-bold text-slate-100 text-base leading-relaxed">
                      {term.term}
                    </div>
                  </TableCell>
                  <TableCell className="py-8 px-6 text-center">
                    <Badge
                      variant="outline"
                      className={`${getBadgeColor(category)} font-semibold px-3 py-1 text-sm`}
                    >
                      {term.count} {term.count === 1 ? 'job' : 'jobs'}
                    </Badge>
                  </TableCell>
                  <TableCell className="py-8 px-6">
                    {term.context_sentences.length > 0 ? (
                      <div className="space-y-3">
                        {term.context_sentences.slice(0, 2).map((sentence, idx) => (
                          <div
                            key={idx}
                            className="relative pl-4 py-2 rounded-lg bg-slate-900/40 border-l-4 border-slate-600"
                          >
                            <p className="text-sm text-slate-300 italic leading-relaxed">
                              "{sentence.length > 120 ? sentence.substring(0, 120) + '...' : sentence}"
                            </p>
                          </div>
                        ))}
                        {term.context_sentences.length > 2 && (
                          <p className="text-xs text-slate-500 italic">
                            +{term.context_sentences.length - 2} more examples
                          </p>
                        )}
                      </div>
                    ) : (
                      <span className="text-slate-500 italic">No context available</span>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <Card className="bg-slate-800/30 border-slate-700">
            <CardContent className="pt-4 pb-4 px-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-slate-100">{terms.length}</div>
                <div className="text-sm text-slate-400">Total Items</div>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-slate-800/30 border-slate-700">
            <CardContent className="pt-4 pb-4 px-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-slate-100">
                  {terms.reduce((sum, term) => sum + term.count, 0)}
                </div>
                <div className="text-sm text-slate-400">Total Mentions</div>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-slate-800/30 border-slate-700">
            <CardContent className="pt-4 pb-4 px-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-slate-100">
                  {terms.length > 0 ? Math.round(terms.reduce((sum, term) => sum + term.count, 0) / terms.length) : 0}
                </div>
                <div className="text-sm text-slate-400">Avg per Item</div>
              </div>
            </CardContent>
          </Card>
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
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {Object.entries(socResults).map(([socCode, result], index) => {
            const gradients = [
              'from-blue-500 to-cyan-500',
              'from-green-500 to-emerald-500',
              'from-purple-500 to-violet-500',
              'from-orange-500 to-amber-500'
            ];
            const isSelected = selectedSOC === socCode;
            
            return (
              <Card
                key={socCode}
                className={`cursor-pointer transition-all duration-300 transform hover:scale-105 ${
                  isSelected
                    ? 'bg-slate-800 border-slate-600 ring-2 ring-blue-400 shadow-xl shadow-blue-500/20'
                    : 'bg-slate-800/70 border-slate-700 hover:bg-slate-800 hover:border-slate-600 shadow-lg'
                }`}
                onClick={() => setSelectedSOC(socCode)}
              >
                <CardContent className="pt-6 pb-6">
                  <div className="text-center space-y-4">
                    {/* Gradient Icon */}
                    <div className={`mx-auto w-16 h-16 rounded-full bg-gradient-to-br ${gradients[index]} flex items-center justify-center shadow-lg`}>
                      <span className="text-2xl text-white font-bold">
                        {(SOC_CODE_NAMES[socCode] || socCode).charAt(0)}
                      </span>
                    </div>
                    
                    {/* Title */}
                    <div>
                      <h3 className="font-bold text-slate-100 mb-1 text-lg">
                        {SOC_CODE_NAMES[socCode] || socCode}
                      </h3>
                      <p className="text-sm text-slate-400 font-mono">SOC {socCode}</p>
                    </div>
                    
                    {/* Stats */}
                    <div className="space-y-2">
                      <Badge
                        variant="outline"
                        className="border-green-400 text-green-300 bg-green-950/30 px-3 py-1"
                      >
                        {result.total_jobs_found} jobs found
                      </Badge>
                      <div className="text-xs text-slate-500">
                        {result.total_descriptions_analyzed} descriptions analyzed
                      </div>
                    </div>
                    
                    {/* Selection Indicator */}
                    {isSelected && (
                      <div className="flex items-center justify-center gap-1 text-blue-400">
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                        <span className="text-xs font-medium">Selected</span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
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
            <div className="flex flex-wrap gap-3 mb-8">
              {[
                { key: 'responsibilities', label: 'Responsibilities', emoji: '📋', gradient: 'from-blue-500 to-cyan-500', bg: 'bg-blue-600 hover:bg-blue-700' },
                { key: 'skills', label: 'Skills', emoji: '🛠️', gradient: 'from-green-500 to-emerald-500', bg: 'bg-green-600 hover:bg-green-700' },
                { key: 'qualifications', label: 'Qualifications', emoji: '🎓', gradient: 'from-purple-500 to-violet-500', bg: 'bg-purple-600 hover:bg-purple-700' },
                { key: 'unique_aspects', label: 'Unique Aspects', emoji: '✨', gradient: 'from-orange-500 to-amber-500', bg: 'bg-orange-600 hover:bg-orange-700' }
              ].map((category) => {
                const isSelected = selectedCategory === category.key;
                return (
                  <Button
                    key={category.key}
                    variant="outline"
                    onClick={() => setSelectedCategory(category.key)}
                    className={`relative overflow-hidden transition-all duration-300 px-6 py-3 text-base font-semibold ${
                      isSelected
                        ? `${category.bg} text-white border-transparent shadow-lg transform scale-105`
                        : 'bg-slate-800/50 border-slate-600 text-slate-300 hover:bg-slate-700 hover:border-slate-500'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{category.emoji}</span>
                      <span>{category.label}</span>
                    </div>
                    {isSelected && (
                      <div className={`absolute inset-0 bg-gradient-to-r ${category.gradient} opacity-20 pointer-events-none`}></div>
                    )}
                  </Button>
                );
              })}
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