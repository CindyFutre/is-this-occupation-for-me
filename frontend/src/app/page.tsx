'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { apiClient, type JobAnalysisResponse, type JobSuggestion } from '@/lib/api-client';

export default function Home() {
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<JobSuggestion[]>([]);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSearch = async (searchQuery: string = query) => {
    if (!searchQuery.trim()) return;

    setIsLoading(true);
    setError('');
    setSuggestions([]);

    try {
      const response: JobAnalysisResponse = await apiClient.analyzeJob({
        query: searchQuery.trim(),
        location: location.trim() || 'United States',
      });

      if (response.success && response.data) {
        // Store the results in sessionStorage and navigate to results page
        sessionStorage.setItem('jobAnalysisResults', JSON.stringify(response.data));
        router.push(`/results/${encodeURIComponent(response.data.soc_code)}`);
      } else if (response.suggestions && response.suggestions.length > 0) {
        setSuggestions(response.suggestions);
      } else if (response.error) {
        setError(response.error.message);
      } else {
        setError('No results found. Please try a different job title.');
      }
    } catch (err) {
      setError('Failed to analyze job. Please try again.');
      console.error('Search error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: JobSuggestion) => {
    setQuery(suggestion.title);
    setSuggestions([]);
    handleSearch(suggestion.title);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSearch();
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            Is this occupation for me?
          </h1>
          <p className="text-xl text-slate-300 max-w-2xl mx-auto">
            Analyze real-time job market data to get clear insights into any profession.
            Discover what employers really want in terms of responsibilities, skills, and qualifications.
          </p>
          
          {/* SOC Analysis Link */}
          <div className="mt-6">
            <Button
              onClick={() => router.push('/soc-analysis')}
              variant="outline"
              className="bg-slate-800 border-slate-600 text-slate-300 hover:bg-slate-700"
            >
              🔍 View SOC Code Analysis Results
            </Button>
          </div>
        </div>

        {/* Search Form */}
        <div className="max-w-2xl mx-auto mb-8">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="text-slate-100">Search Job Market</CardTitle>
              <CardDescription className="text-slate-400">
                Enter a job title to analyze current market demands
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="job-title" className="block text-sm font-medium text-slate-300 mb-2">
                    Job Title *
                  </label>
                  <Input
                    id="job-title"
                    type="text"
                    placeholder="e.g., Software Developer, Financial Manager, Registered Nurse"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="bg-slate-700 border-slate-600 text-slate-100 placeholder:text-slate-400"
                    disabled={isLoading}
                  />
                </div>
                <div>
                  <label htmlFor="location" className="block text-sm font-medium text-slate-300 mb-2">
                    Location (Optional)
                  </label>
                  <Input
                    id="location"
                    type="text"
                    placeholder="e.g., Seattle,WA or leave blank for nationwide"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    className="bg-slate-700 border-slate-600 text-slate-100 placeholder:text-slate-400"
                    disabled={isLoading}
                  />
                </div>
                <Button 
                  type="submit" 
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                  disabled={isLoading || !query.trim()}
                >
                  {isLoading ? 'Analyzing Job Market...' : 'Analyze Job Market'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Error Message */}
        {error && (
          <div className="max-w-2xl mx-auto mb-8">
            <Card className="bg-red-900/20 border-red-700">
              <CardContent className="pt-6">
                <p className="text-red-300">{error}</p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Suggestions */}
        {suggestions.length > 0 && (
          <div className="max-w-2xl mx-auto mb-8">
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-slate-100">Did you mean one of these?</CardTitle>
                <CardDescription className="text-slate-400">
                  We found similar job titles that we can analyze
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-2">
                  {suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="flex items-center justify-between p-3 rounded-lg bg-slate-700 hover:bg-slate-600 transition-colors text-left"
                      disabled={isLoading}
                    >
                      <div>
                        <div className="font-medium text-slate-100">{suggestion.title}</div>
                        <div className="text-sm text-slate-400">SOC Code: {suggestion.soc_code}</div>
                      </div>
                      <Badge variant="secondary" className="bg-blue-600 text-white">
                        {Math.round(suggestion.similarity_score * 100)}% match
                      </Badge>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Features */}
        <div className="max-w-4xl mx-auto mt-16">
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="bg-slate-800 border-slate-700">
              <CardContent className="pt-6">
                <div className="text-blue-400 text-2xl mb-2">📋</div>
                <h3 className="font-semibold text-slate-100 mb-2">Responsibilities</h3>
                <p className="text-sm text-slate-400">
                  Key duties and tasks employers expect
                </p>
              </CardContent>
            </Card>
            <Card className="bg-slate-800 border-slate-700">
              <CardContent className="pt-6">
                <div className="text-green-400 text-2xl mb-2">🛠️</div>
                <h3 className="font-semibold text-slate-100 mb-2">Skills</h3>
                <p className="text-sm text-slate-400">
                  Technical and soft skills in demand
                </p>
              </CardContent>
            </Card>
            <Card className="bg-slate-800 border-slate-700">
              <CardContent className="pt-6">
                <div className="text-purple-400 text-2xl mb-2">🎓</div>
                <h3 className="font-semibold text-slate-100 mb-2">Qualifications</h3>
                <p className="text-sm text-slate-400">
                  Education and experience requirements
                </p>
              </CardContent>
            </Card>
            <Card className="bg-slate-800 border-slate-700">
              <CardContent className="pt-6">
                <div className="text-orange-400 text-2xl mb-2">✨</div>
                <h3 className="font-semibold text-slate-100 mb-2">Unique Aspects</h3>
                <p className="text-sm text-slate-400">
                  Benefits, perks, and special features
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}