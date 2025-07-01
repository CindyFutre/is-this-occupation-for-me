'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Search, 
  MapPin, 
  TrendingUp, 
  BarChart3, 
  ClipboardList, 
  Wrench, 
  GraduationCap, 
  Sparkles,
  Users,
  Target,
  DollarSign,
  ArrowRight,
  Star,
  CheckCircle,
  Zap,
  Brain,
  Rocket,
  Globe,
  Award,
  Lightbulb,
  Shield,
  Clock,
  Briefcase
} from 'lucide-react';
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

  const popularSearches = [
    'Software Developer',
    'Marketing Manager', 
    'UX Designer',
    'Data Scientist',
    'Product Manager',
    'Financial Analyst'
  ];

  const valuePropositions = [
    {
      icon: BarChart3,
      title: 'Skills Analysis',
      description: 'Discover what skills employers actually want',
      features: ['Technical skills breakdown', 'Soft skills requirements', 'Emerging skill trends'],
      color: 'from-emerald-500 to-teal-600',
      bgColor: 'from-emerald-50 to-teal-50',
      darkBgColor: 'from-emerald-900/20 to-teal-900/20'
    },
    {
      icon: Target,
      title: 'Market Demand',
      description: 'Know where opportunities are growing',
      features: ['Geographic demand', 'Industry growth', 'Job availability'],
      color: 'from-blue-500 to-cyan-600',
      bgColor: 'from-blue-50 to-cyan-50',
      darkBgColor: 'from-blue-900/20 to-cyan-900/20'
    },
    {
      icon: DollarSign,
      title: 'Salary Insights',
      description: 'Understand compensation expectations',
      features: ['Salary ranges', 'Benefits packages', 'Compensation trends'],
      color: 'from-violet-500 to-purple-600',
      bgColor: 'from-violet-50 to-purple-50',
      darkBgColor: 'from-violet-900/20 to-purple-900/20'
    },
    {
      icon: Rocket,
      title: 'Career Path',
      description: 'Plan your professional journey',
      features: ['Career progression', 'Skill development', 'Growth opportunities'],
      color: 'from-orange-500 to-red-600',
      bgColor: 'from-orange-50 to-red-50',
      darkBgColor: 'from-orange-900/20 to-red-900/20'
    }
  ];

  const processSteps = [
    {
      number: 1,
      title: 'Search & Discover',
      description: 'Enter any job title and let our AI analyze thousands of real job postings',
      icon: Search,
      color: 'from-pink-500 to-rose-600'
    },
    {
      number: 2,
      title: 'Analyze & Understand',
      description: 'Get comprehensive insights about skills, requirements, and market trends',
      icon: Brain,
      color: 'from-indigo-500 to-blue-600'
    },
    {
      number: 3,
      title: 'Plan & Execute',
      description: 'Create your personalized career roadmap with actionable next steps',
      icon: Rocket,
      color: 'from-emerald-500 to-green-600'
    }
  ];

  const trendingInsights = [
    {
      title: '🔥 Hot Skills 2024',
      items: ['Python', 'Data Analysis', 'Cloud Computing', 'Machine Learning', 'React'],
      ctaText: 'Explore Skills',
      gradient: 'from-red-500 to-orange-500'
    },
    {
      title: '📈 Growing Roles',
      items: ['UX Designer', 'Product Manager', 'Data Scientist', 'DevOps Engineer'],
      ctaText: 'See Trends',
      gradient: 'from-blue-500 to-purple-500'
    },
    {
      title: '🎯 Entry Level',
      items: ['Marketing Coordinator', 'Jr Developer', 'Business Analyst', 'Content Creator'],
      ctaText: 'View Roles',
      gradient: 'from-green-500 to-teal-500'
    }
  ];

  const stats = [
    { number: '100K+', label: 'Jobs Analyzed', icon: Briefcase },
    { number: '25K+', label: 'Students Helped', icon: Users },
    { number: '98%', label: 'Success Rate', icon: Award },
    { number: '500+', label: 'Career Paths', icon: Globe }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-slate-900 dark:via-blue-900/20 dark:to-indigo-900/20">
      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-purple-400/20 to-pink-400/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-blue-400/20 to-cyan-400/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-br from-emerald-400/10 to-teal-400/10 rounded-full blur-3xl animate-pulse delay-500"></div>
      </div>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="container mx-auto px-4 py-16 lg:py-24">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="text-center lg:text-left space-y-8">
              <div className="space-y-6">
                <Badge className="bg-gradient-to-r from-purple-600 to-pink-600 text-white border-0 px-4 py-2 text-sm font-medium">
                  <Sparkles className="w-4 h-4 mr-2" />
                  AI-Powered Career Intelligence
                </Badge>
                <h1 className="text-4xl md:text-5xl lg:text-7xl font-black leading-tight">
                  <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                    Decode Your
                  </span>
                  <br />
                  <span className="bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 bg-clip-text text-transparent">
                    Dream Career
                  </span>
                </h1>
                <p className="text-xl md:text-2xl text-slate-600 dark:text-slate-300 leading-relaxed max-w-2xl">
                  Transform job market data into your competitive advantage. 
                  <span className="font-semibold text-slate-800 dark:text-slate-200"> Discover skills, salaries, and opportunities</span> 
                  that matter most.
                </p>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                <Button 
                  size="lg" 
                  className="text-lg px-8 py-6 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-2xl hover:shadow-blue-500/25 transform hover:scale-105 transition-all duration-300"
                  onClick={() => document.getElementById('search-section')?.scrollIntoView({ behavior: 'smooth' })}
                >
                  <Rocket className="mr-2 h-5 w-5" />
                  Start Career Analysis
                </Button>
                <Button 
                  size="lg" 
                  variant="outline"
                  className="text-lg px-8 py-6 border-2 border-slate-300 hover:border-purple-500 hover:text-purple-600 transition-all duration-300"
                >
                  <Globe className="mr-2 h-5 w-5" />
                  Explore Trends
                </Button>
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-8">
                {stats.map((stat, index) => {
                  const IconComponent = stat.icon;
                  return (
                    <div key={index} className="text-center p-4 rounded-2xl bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm border border-white/20">
                      <IconComponent className="h-6 w-6 mx-auto mb-2 text-purple-600" />
                      <div className="text-2xl font-bold text-slate-800 dark:text-slate-200">{stat.number}</div>
                      <div className="text-sm text-slate-600 dark:text-slate-400">{stat.label}</div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Hero Visual */}
            <div className="relative">
              <div className="relative w-full h-96 lg:h-[500px]">
                {/* Main Card */}
                <div className="absolute inset-0 bg-gradient-to-br from-white to-blue-50 dark:from-slate-800 dark:to-blue-900/30 rounded-3xl shadow-2xl border border-white/20 backdrop-blur-sm p-8 transform rotate-2 hover:rotate-0 transition-transform duration-500">
                  <div className="space-y-6">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl flex items-center justify-center">
                        <TrendingUp className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <h3 className="font-bold text-lg">Career Dashboard</h3>
                        <p className="text-sm text-slate-600 dark:text-slate-400">Real-time insights</p>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Market Demand</span>
                        <span className="text-sm text-green-600 font-semibold">+23%</span>
                      </div>
                      <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                        <div className="bg-gradient-to-r from-green-500 to-emerald-500 h-2 rounded-full w-3/4"></div>
                      </div>
                      
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Skill Match</span>
                        <span className="text-sm text-blue-600 font-semibold">87%</span>
                      </div>
                      <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                        <div className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full w-5/6"></div>
                      </div>
                      
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Salary Range</span>
                        <span className="text-sm text-purple-600 font-semibold">$85K-$120K</span>
                      </div>
                      <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                        <div className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full w-4/5"></div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Floating Elements */}
                <div className="absolute -top-4 -right-4 w-20 h-20 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-2xl flex items-center justify-center shadow-xl animate-bounce">
                  <Zap className="h-8 w-8 text-white" />
                </div>
                <div className="absolute -bottom-4 -left-4 w-16 h-16 bg-gradient-to-br from-orange-400 to-red-500 rounded-xl flex items-center justify-center shadow-xl animate-pulse">
                  <Star className="h-6 w-6 text-white" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Smart Search Section */}
      <section id="search-section" className="py-20 relative">
        <div className="container mx-auto px-4">
          <div className="max-w-5xl mx-auto">
            <Card className="shadow-2xl border-0 bg-gradient-to-br from-white/90 to-slate-50/90 dark:from-slate-800/90 dark:to-slate-900/90 backdrop-blur-xl">
              <CardHeader className="text-center pb-8 bg-gradient-to-r from-blue-600/10 to-purple-600/10 rounded-t-xl">
                <div className="flex justify-center mb-4">
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl flex items-center justify-center shadow-lg">
                    <Search className="h-8 w-8 text-white" />
                  </div>
                </div>
                <CardTitle className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Smart Career Explorer
                </CardTitle>
                <CardDescription className="text-lg md:text-xl text-slate-600 dark:text-slate-300 mt-4">
                  Enter any job title and unlock comprehensive career insights powered by AI
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-8 p-8">
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-3">
                      <Label htmlFor="job-title" className="text-base font-semibold text-slate-700 dark:text-slate-300">
                        Job Title *
                      </Label>
                      <div className="relative">
                        <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
                        <Input 
                          id="job-title"
                          className="pl-12 h-14 text-base border-2 border-slate-200 dark:border-slate-700 focus:border-purple-500 rounded-xl bg-white/50 dark:bg-slate-800/50 backdrop-blur-sm" 
                          placeholder="e.g., Software Developer, Marketing Manager"
                          value={query}
                          onChange={(e) => setQuery(e.target.value)}
                          disabled={isLoading}
                        />
                      </div>
                    </div>
                    <div className="space-y-3">
                      <Label htmlFor="location" className="text-base font-semibold text-slate-700 dark:text-slate-300">
                        Location (Optional)
                      </Label>
                      <div className="relative">
                        <MapPin className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
                        <Input 
                          id="location"
                          className="pl-12 h-14 text-base border-2 border-slate-200 dark:border-slate-700 focus:border-purple-500 rounded-xl bg-white/50 dark:bg-slate-800/50 backdrop-blur-sm" 
                          placeholder="e.g., Seattle, WA"
                          value={location}
                          onChange={(e) => setLocation(e.target.value)}
                          disabled={isLoading}
                        />
                      </div>
                    </div>
                  </div>
                  
                  <Button 
                    type="submit"
                    className="w-full h-14 text-lg font-semibold bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-xl hover:shadow-purple-500/25 transform hover:scale-[1.02] transition-all duration-300 rounded-xl"
                    disabled={isLoading || !query.trim()}
                  >
                    <TrendingUp className="mr-3 h-6 w-6" />
                    {isLoading ? 'Analyzing Market Data...' : 'Analyze Career Opportunities'}
                  </Button>
                </form>

                {/* Popular Searches */}
                <div className="pt-6 border-t border-slate-200 dark:border-slate-700">
                  <p className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-4">🔥 Trending Searches:</p>
                  <div className="flex flex-wrap gap-3">
                    {popularSearches.map((search, index) => (
                      <Badge 
                        key={index}
                        variant="secondary" 
                        className="cursor-pointer hover:bg-gradient-to-r hover:from-blue-500 hover:to-purple-500 hover:text-white transition-all duration-300 px-4 py-2 text-sm font-medium rounded-full border-2 border-slate-200 dark:border-slate-700"
                        onClick={() => {
                          setQuery(search);
                          handleSearch(search);
                        }}
                      >
                        {search}
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Error Message */}
      {error && (
        <div className="container mx-auto px-4 mb-8">
          <div className="max-w-2xl mx-auto">
            <Card className="border-red-200 bg-red-50 dark:bg-red-900/20 dark:border-red-800">
              <CardContent className="pt-6">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
                    <Shield className="h-4 w-4 text-white" />
                  </div>
                  <p className="text-red-700 dark:text-red-300 font-medium">{error}</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <div className="container mx-auto px-4 mb-8">
          <div className="max-w-4xl mx-auto">
            <Card className="shadow-2xl border-0 bg-gradient-to-br from-white/90 to-slate-50/90 dark:from-slate-800/90 dark:to-slate-900/90 backdrop-blur-xl">
              <CardHeader className="pb-4">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500 to-purple-500">
                    <Search className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-2xl font-bold">Similar Career Matches</CardTitle>
                    <CardDescription className="text-lg">
                      We found {suggestions.length} related positions that match your search
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4">
                  {suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="group flex items-center justify-between p-6 rounded-2xl bg-gradient-to-r from-slate-50 to-blue-50 dark:from-slate-800 dark:to-blue-900/30 hover:from-blue-50 hover:to-purple-50 dark:hover:from-blue-900/30 dark:hover:to-purple-900/30 transition-all duration-300 text-left border-2 border-slate-200 dark:border-slate-700 hover:border-purple-300 dark:hover:border-purple-600 hover:shadow-xl transform hover:scale-[1.02]"
                      disabled={isLoading}
                    >
                      <div className="flex-1">
                        <div className="font-bold text-xl group-hover:text-purple-600 transition-colors mb-2">
                          {suggestion.title}
                        </div>
                        <div className="text-sm text-slate-600 dark:text-slate-400 font-mono bg-slate-100 dark:bg-slate-700 px-3 py-1 rounded-full inline-block">
                          SOC: {suggestion.soc_code}
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <Badge className="bg-gradient-to-r from-green-500 to-emerald-500 text-white border-0 px-3 py-1">
                          {Math.round(suggestion.similarity_score * 100)}% match
                        </Badge>
                        <ArrowRight className="h-6 w-6 text-slate-400 group-hover:text-purple-600 transition-colors" />
                      </div>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Value Proposition Section */}
      <section className="py-24 relative">
        <div className="container mx-auto px-4">
          <div className="text-center mb-20">
            <Badge className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white border-0 px-4 py-2 text-sm font-medium mb-6">
              <Lightbulb className="w-4 h-4 mr-2" />
              Comprehensive Career Intelligence
            </Badge>
            <h2 className="text-4xl md:text-5xl font-black mb-6">
              <span className="bg-gradient-to-r from-slate-800 to-slate-600 dark:from-slate-200 dark:to-slate-400 bg-clip-text text-transparent">
                Transform Data Into
              </span>
              <br />
              <span className="bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
                Career Success
              </span>
            </h2>
            <p className="text-xl text-slate-600 dark:text-slate-300 max-w-4xl mx-auto leading-relaxed">
              Our AI-powered platform analyzes thousands of job postings to give you the insights you need to make informed career decisions
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {valuePropositions.map((prop, index) => {
              const IconComponent = prop.icon;
              return (
                <Card
                  key={index}
                  className={`group hover:shadow-2xl transition-all duration-500 border-0 bg-gradient-to-br ${prop.bgColor} dark:${prop.darkBgColor} backdrop-blur-sm hover:scale-105 transform cursor-pointer overflow-hidden relative`}
                >
                  {/* Animated background */}
                  <div className={`absolute inset-0 bg-gradient-to-br ${prop.color} opacity-0 group-hover:opacity-10 transition-opacity duration-500`}></div>
                  
                  <CardContent className="pt-8 pb-8 text-center relative z-10">
                    <div className={`mx-auto w-20 h-20 rounded-2xl bg-gradient-to-br ${prop.color} flex items-center justify-center shadow-xl mb-6 group-hover:scale-110 group-hover:rotate-6 transition-all duration-500`}>
                      <IconComponent className="h-10 w-10 text-white" />
                    </div>
                    <h3 className="font-bold mb-4 text-2xl group-hover:text-slate-800 dark:group-hover:text-slate-200 transition-colors">
                      {prop.title}
                    </h3>
                    <p className="text-slate-600 dark:text-slate-400 mb-6 leading-relaxed text-lg">
                      {prop.description}
                    </p>
                    <ul className="space-y-3">
                      {prop.features.map((feature, idx) => (
                        <li key={idx} className="flex items-center gap-3 text-sm">
                          <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                          <span className="text-slate-700 dark:text-slate-300">{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-24 bg-gradient-to-br from-slate-100 to-blue-100 dark:from-slate-800 dark:to-blue-900/30 relative overflow-hidden">
        <div className="container mx-auto px-4">
          <div className="text-center mb-20">
            <Badge className="bg-gradient-to-r from-blue-600 to-purple-600 text-white border-0 px-4 py-2 text-sm font-medium mb-6">
              <Clock className="w-4 h-4 mr-2" />
              Simple 3-Step Process
            </Badge>
            <h2 className="text-4xl md:text-5xl font-black mb-6">
              <span className="bg-gradient-to-r from-slate-800 to-slate-600 dark:from-slate-200 dark:to-slate-400 bg-clip-text text-transparent">
                How It Works
              </span>
            </h2>
            <p className="text-xl text-slate-600 dark:text-slate-300 max-w-3xl mx-auto">
              Get comprehensive career insights in minutes, not months
            </p>
          </div>
          
          <div className="max-w-6xl mx-auto">
            <div className="grid md:grid-cols-3 gap-12 relative">
              {/* Connection Lines */}
              <div className="hidden md:block absolute top-24 left-1/3 right-1/3 h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-emerald-500 rounded-full"></div>
              
              {processSteps.map((step, index) => {
                const IconComponent = step.icon;
                return (
                  <div key={index} className="text-center relative group">
                    <Card className="hover:shadow-2xl transition-all duration-500 border-0 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm hover:scale-105 transform relative z-10 overflow-hidden">
                      {/* Animated background */}
                      <div className={`absolute inset-0 bg-gradient-to-br ${step.color} opacity-0 group-hover:opacity-10 transition-opacity duration-500`}></div>
                      
                      <CardContent className="pt-8 pb-8 text-center relative z-10">
                        <div className={`mx-auto w-24 h-24 rounded-2xl bg-gradient-to-br ${step.color} flex items-center justify-center shadow-xl mb-6 group-hover:scale-110 transition-all duration-500`}>
                          <div className="text-2xl font-bold text-white">{step.number}</div>
                        </div>
                        <div className="mb-4">
                          <IconComponent className="h-8 w-8 text-slate-600 dark:text-slate-400 mx-auto" />
                        </div>
                        <h3 className="font-bold mb-4 text-2xl">{step.title}</h3>
                        <p className="text-slate-600 dark:text-slate-400 leading-relaxed text-lg">
                          {step.description}
                        </p>
                      </CardContent>
                    </Card>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* Social Proof Section */}
      <section className="py-24 relative">
        <div className="container mx-auto px-4">
          <div className="text-center mb-20">
            <Badge className="bg-gradient-to-r from-purple-600 to-pink-600 text-white border-0 px-4 py-2 text-sm font-medium mb-6">
              <Users className="w-4 h-4 mr-2" />
              Trusted by Students Worldwide
            </Badge>
            <h2 className="text-4xl md:text-5xl font-black mb-6">
              <span className="bg-gradient-to-r from-slate-800 to-slate-600 dark:from-slate-200 dark:to-slate-400 bg-clip-text text-transparent">
                Join Thousands of
              </span>
              <br />
              <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                Success Stories
              </span>
            </h2>
          </div>
          
          <div className="max-w-4xl mx-auto">
            <Card className="shadow-2xl border-0 bg-gradient-to-br from-white/90 to-purple-50/90 dark:from-slate-800/90 dark:to-purple-900/20 backdrop-blur-xl overflow-hidden">
              <CardContent className="pt-12 pb-12 text-center relative">
                {/* Background decoration */}
                <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-pink-500/5"></div>
                
                <div className="relative z-10">
                  <div className="flex justify-center mb-6">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="h-8 w-8 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  <blockquote className="text-2xl md:text-3xl font-bold mb-8 italic text-slate-800 dark:text-slate-200 leading-relaxed">
                    "This platform helped me understand exactly what skills I needed for product management roles.
                    I got my first job offer within 2 months!"
                  </blockquote>
                  <div className="flex items-center justify-center gap-6">
                    <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center shadow-xl">
                      <Users className="h-8 w-8 text-white" />
                    </div>
                    <div className="text-left">
                      <div className="font-bold text-xl text-slate-800 dark:text-slate-200">Sarah Chen</div>
                      <div className="text-slate-600 dark:text-slate-400">UCLA Graduate, Product Manager at Google</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Trending Insights Section */}
      <section className="py-24 bg-gradient-to-br from-slate-100 to-purple-100 dark:from-slate-800 dark:to-purple-900/30">
        <div className="container mx-auto px-4">
          <div className="text-center mb-20">
            <Badge className="bg-gradient-to-r from-orange-600 to-red-600 text-white border-0 px-4 py-2 text-sm font-medium mb-6">
              <Zap className="w-4 h-4 mr-2" />
              Market Intelligence
            </Badge>
            <h2 className="text-4xl md:text-5xl font-black mb-6">
              <span className="bg-gradient-to-r from-slate-800 to-slate-600 dark:from-slate-200 dark:to-slate-400 bg-clip-text text-transparent">
                Trending Career
              </span>
              <br />
              <span className="bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
                Insights
              </span>
            </h2>
            <p className="text-xl text-slate-600 dark:text-slate-300 max-w-3xl mx-auto">
              Stay ahead with the latest market trends and opportunities
            </p>
          </div>
          
          <div className="max-w-6xl mx-auto grid md:grid-cols-3 gap-8">
            {trendingInsights.map((insight, index) => (
              <Card key={index} className="group hover:shadow-2xl transition-all duration-500 border-0 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm hover:scale-105 transform overflow-hidden">
                <div className={`h-2 bg-gradient-to-r ${insight.gradient}`}></div>
                <CardHeader className="pb-4">
                  <CardTitle className="text-2xl font-bold">{insight.title}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-3">
                    {insight.items.map((item, idx) => (
                      <div key={idx} className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-700/50 group-hover:bg-slate-100 dark:group-hover:bg-slate-700 transition-colors">
                        <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${insight.gradient}`}></div>
                        <span className="font-medium text-slate-700 dark:text-slate-300">{item}</span>
                      </div>
                    ))}
                  </div>
                  <Button className={`w-full bg-gradient-to-r ${insight.gradient} hover:opacity-90 text-white border-0 shadow-lg`}>
                    {insight.ctaText}
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-24 bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 text-white relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0">
          <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-blue-600/90 to-purple-600/90"></div>
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-white/10 rounded-full blur-3xl"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-white/10 rounded-full blur-3xl"></div>
        </div>
        
        <div className="container mx-auto px-4 text-center relative z-10">
          <div className="max-w-4xl mx-auto space-y-8">
            <Badge className="bg-white/20 text-white border-0 px-4 py-2 text-sm font-medium">
              <Rocket className="w-4 h-4 mr-2" />
              Ready to Launch Your Career?
            </Badge>
            <h2 className="text-4xl md:text-6xl font-black leading-tight">
              Your Dream Career
              <br />
              <span className="bg-gradient-to-r from-yellow-300 to-orange-300 bg-clip-text text-transparent">
                Starts Today
              </span>
            </h2>
            <p className="text-xl md:text-2xl opacity-90 leading-relaxed max-w-3xl mx-auto">
              Join thousands of students who've used our insights to land their dream jobs and build in-demand skills
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8">
              <Button
                size="lg"
                className="text-lg px-8 py-6 bg-white text-blue-600 hover:bg-gray-100 shadow-2xl hover:shadow-white/25 transform hover:scale-105 transition-all duration-300 font-semibold"
                onClick={() => document.getElementById('search-section')?.scrollIntoView({ behavior: 'smooth' })}
              >
                <Rocket className="mr-2 h-5 w-5" />
                Start Your Career Analysis
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="text-lg px-8 py-6 border-2 border-white/30 text-white hover:bg-white/10 transition-all duration-300"
              >
                <Globe className="mr-2 h-5 w-5" />
                Explore All Features
              </Button>
            </div>
            <div className="flex items-center justify-center gap-6 pt-8 text-sm opacity-75">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4" />
                <span>Free to Use</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4" />
                <span>No Sign-up Required</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4" />
                <span>Instant Results</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}