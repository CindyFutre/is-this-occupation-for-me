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
        <div className="max-w-xl mx-auto mb-8" style={{ maxWidth: '497px' }}>
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-slate-100 mb-2">Search Job Market</h2>
            <p className="text-slate-400">
              Enter a job title to analyze current market demands
            </p>
          </div>
          <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="job-title" className="block text-sm font-medium text-slate-300 mb-2">
                    Job Title *
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <svg className="h-5 w-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                    </div>
                    <Input
                      id="job-title"
                      type="text"
                      placeholder="e.g., Software Developer, Financial Manager, Registered Nurse"
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      className="pl-10 bg-slate-700 border-slate-600 text-slate-100 placeholder:text-slate-400 rounded-full"
                      style={{ padding: '12px 14px 12px 40px', fontSize: '1.1rem' }}
                      disabled={isLoading}
                    />
                  </div>
                </div>
                <div>
                  <label htmlFor="location" className="block text-sm font-medium text-slate-300 mb-2">
                    Location (Optional)
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <svg className="h-5 w-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                    </div>
                    <Input
                      id="location"
                      type="text"
                      placeholder="e.g., Seattle,WA or leave blank for nationwide"
                      value={location}
                      onChange={(e) => setLocation(e.target.value)}
                      className="pl-10 bg-slate-700 border-slate-600 text-slate-100 placeholder:text-slate-400 rounded-full"
                      style={{ padding: '12px 14px 12px 40px', fontSize: '1.1rem' }}
                      disabled={isLoading}
                    />
                  </div>
                </div>
                <Button 
                  type="submit" 
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                  disabled={isLoading || !query.trim()}
                >
                  {isLoading ? 'Analyzing Job Market...' : 'Analyze Job Market'}
                </Button>
              </form>
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
          <div className="max-w-3xl mx-auto mb-8">
            <Card className="bg-slate-800/70 border-slate-700 shadow-xl">
              <CardHeader className="pb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500">
                    <span className="text-xl">🎯</span>
                  </div>
                  <div>
                    <CardTitle className="text-slate-100 text-xl">Did you mean one of these?</CardTitle>
                    <CardDescription className="text-slate-400">
                      We found {suggestions.length} similar job titles that we can analyze
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid gap-3">
                  {suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="group flex items-center justify-between p-4 rounded-xl bg-slate-700/50 hover:bg-slate-600/70 transition-all duration-300 text-left border border-slate-600 hover:border-slate-500 hover:shadow-lg transform hover:scale-[1.02]"
                      disabled={isLoading}
                    >
                      <div className="flex-1">
                        <div className="font-semibold text-slate-100 text-lg group-hover:text-white transition-colors">
                          {suggestion.title}
                        </div>
                        <div className="text-sm text-slate-400 font-mono mt-1">
                          SOC Code: {suggestion.soc_code}
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Badge
                          variant="outline"
                          className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white border-transparent px-3 py-1 font-semibold"
                        >
                          {Math.round(suggestion.similarity_score * 100)}% match
                        </Badge>
                        <div className="text-slate-400 group-hover:text-slate-300 transition-colors">
                          →
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Features */}
        <div className="max-w-5xl mx-auto mt-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-100 mb-4">
              What You'll Discover
            </h2>
            <p className="text-lg text-slate-400 max-w-2xl mx-auto">
              Our AI-powered analysis provides comprehensive insights across four key areas
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                emoji: '📋',
                title: 'Responsibilities',
                description: 'Key duties and tasks employers expect',
                gradient: 'from-blue-500 to-cyan-500',
                bgColor: 'bg-blue-950/30'
              },
              {
                emoji: '🛠️',
                title: 'Skills',
                description: 'Technical and soft skills in demand',
                gradient: 'from-green-500 to-emerald-500',
                bgColor: 'bg-green-950/30'
              },
              {
                emoji: '🎓',
                title: 'Qualifications',
                description: 'Education and experience requirements',
                gradient: 'from-purple-500 to-violet-500',
                bgColor: 'bg-purple-950/30'
              },
              {
                emoji: '✨',
                title: 'Unique Aspects',
                description: 'Benefits, perks, and special features',
                gradient: 'from-orange-500 to-amber-500',
                bgColor: 'bg-orange-950/30'
              }
            ].map((feature, index) => (
              <Card
                key={index}
                className="bg-slate-800/70 border-slate-700 hover:bg-slate-800 transition-all duration-300 transform hover:scale-105 hover:shadow-xl group"
              >
                <CardContent className="pt-8 pb-6 text-center">
                  <div className={`mx-auto w-16 h-16 rounded-full bg-gradient-to-br ${feature.gradient} flex items-center justify-center shadow-lg mb-4 group-hover:scale-110 transition-transform duration-300`}>
                    <span className="text-2xl">{feature.emoji}</span>
                  </div>
                  <h3 className="font-bold text-slate-100 mb-3 text-lg group-hover:text-white transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-slate-400 leading-relaxed group-hover:text-slate-300 transition-colors">
                    {feature.description}
                  </p>
                  <div className={`mt-4 h-1 w-12 mx-auto rounded-full bg-gradient-to-r ${feature.gradient} opacity-60 group-hover:opacity-100 transition-opacity duration-300`}></div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}