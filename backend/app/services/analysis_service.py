import json
import re
import html
import os
from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict, Counter
from app.models.pydantic_models import JobInsightsReport, AnalyzedTerm
from app.core.config import settings
import anthropic

class HybridTermAnalyzer:
    """
    Hybrid analysis engine that uses Anthropic Claude/Sonnet 4.0 when available,
    with intelligent fallback to enhanced rule-based analysis.
    """
    
    def __init__(self):
        self.claude_available = False
        self.client = None
        
        # Try to get API key from settings or environment
        api_key = None
        if settings.anthropic_api_key and settings.anthropic_api_key != "your-anthropic-api-key-here":
            api_key = settings.anthropic_api_key
        else:
            # Check system environment variable
            api_key = os.environ.get("ANTHROPIC_API_KEY")
        
        # Try to initialize Claude client
        if api_key:
            try:
                # Initialize with the updated anthropic library
                self.client = anthropic.Anthropic(api_key=api_key)
                self.claude_available = True
                print("✅ Claude/Sonnet 4.0 initialized successfully - Using AI-powered analysis")
            except Exception as e:
                print(f"⚠️ Claude initialization failed: {e} - Falling back to enhanced rule-based analysis")
                self.claude_available = False
        else:
            print("ℹ️ No Anthropic API key found in settings or environment - Using enhanced rule-based analysis")
        
        # Enhanced normalization dictionary for fallback mode
        self.normalization_dict = {
            # Electrical work activities
            'running wire': 'running and pulling electrical wire',
            'pulling wire': 'running and pulling electrical wire',
            'wire running': 'running and pulling electrical wire',
            'wire pulling': 'running and pulling electrical wire',
            'run wire': 'running and pulling electrical wire',
            'pull wire': 'running and pulling electrical wire',
            'running and pulling wire': 'running and pulling electrical wire',
            
            'bending conduit': 'installing and bending conduit',
            'conduit bending': 'installing and bending conduit',
            'bend conduit': 'installing and bending conduit',
            'running conduit': 'installing and bending conduit',
            'conduit installation': 'installing and bending conduit',
            
            'installing lights': 'installing lighting and electrical fixtures',
            'installing outlets': 'installing lighting and electrical fixtures',
            'light installation': 'installing lighting and electrical fixtures',
            'outlet installation': 'installing lighting and electrical fixtures',
            'install lights': 'installing lighting and electrical fixtures',
            'install outlets': 'installing lighting and electrical fixtures',
            'fixture installation': 'installing lighting and electrical fixtures',
            
            'low voltage work': 'low voltage systems installation',
            'low voltage': 'low voltage systems installation',
            'low voltage installation': 'low voltage systems installation',
            'low voltage systems': 'low voltage systems installation',
            
            'industrial work': 'industrial electrical maintenance',
            'industrial electrical': 'industrial electrical maintenance',
            'industrial maintenance': 'industrial electrical maintenance',
            
            'electrical terminations': 'electrical connections and terminations',
            'wire terminations': 'electrical connections and terminations',
            'cable terminations': 'electrical connections and terminations',
            'terminating': 'electrical connections and terminations',
            'terminate': 'electrical connections and terminations',
            'connections': 'electrical connections and terminations',
            
            # Healthcare activities
            'patient care': 'providing direct patient care',
            'administering medication': 'medication administration and monitoring',
            'medication administration': 'medication administration and monitoring',
            'vital signs': 'monitoring vital signs and patient status',
            'monitoring patients': 'monitoring vital signs and patient status',
            'patient monitoring': 'monitoring vital signs and patient status',
            
            # Programming and tech
            'javascript': 'javascript programming',
            'js': 'javascript programming',
            'python': 'python programming',
            'java': 'java programming',
            'react': 'react development',
            'node.js': 'node.js development',
            'nodejs': 'node.js development',
            
            # General work activities
            'data analysis': 'analyzing and interpreting data',
            'data analytics': 'analyzing and interpreting data',
            'project management': 'managing projects and timelines',
            'customer service': 'providing customer support and service',
            'troubleshooting': 'diagnosing and troubleshooting issues',
        }
        
    def clean_html_and_artifacts(self, text: str) -> str:
        """Clean HTML tags, script content, and other artifacts from text."""
        if not text:
            return ""
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove script and style tags with content
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags but keep content
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Remove tracking patterns
        tracking_patterns = [
            r'https?://[^\s]*\.cloudfront\.net[^\s]*',
            r'https?://[^\s]*analytics[^\s]*',
            r'data-[a-zA-Z-]+=[\"\'][^\"\']*[\"\']',
            r'defer\s+src=', r'script\s+id=',
        ]
        
        for pattern in tracking_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove URLs and emails
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r'\S+@\S+\.\S+', '', text)
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def extract_and_categorize_with_claude(self, job_postings_text: str, job_title: str) -> Dict[str, List[Dict[str, Any]]]:
        """Use Claude to extract and categorize work activities from job postings."""
        
        system_prompt = """You are an expert job market analyst specializing in extracting meaningful work activities from job postings. Your task is to analyze job posting content and extract the most important daily work responsibilities, required skills, qualifications, and unique aspects.

IMPORTANT GUIDELINES:
1. Focus on DAILY WORK ACTIVITIES and RESPONSIBILITIES that someone actually does on the job
2. Extract CONCRETE, SPECIFIC activities rather than vague descriptions
3. Normalize similar activities (e.g., "running wire", "pulling wire", "wire installation" → "running and pulling electrical wire")
4. Count frequency across multiple job postings to identify the most common activities
5. Provide context sentences that clearly show where each activity was mentioned
6. Categorize each extracted term appropriately

CATEGORIZATION RULES:
- **Responsibilities**: Daily work activities, tasks, duties (e.g., "coordinate patient care", "install electrical systems", "analyze financial data")
- **Skills**: Technical abilities, tools, software, methodologies (e.g., "Python programming", "Microsoft Excel", "project management")
- **Qualifications**: Education, experience, certifications, licenses (e.g., "bachelor's degree", "5 years experience", "RN license")
- **Unique Aspects**: Benefits, work environment, company culture, special perks (e.g., "remote work", "flexible schedule", "health benefits")

OUTPUT FORMAT: Return a JSON object with this exact structure:
{
  "responsibilities": [
    {
      "term": "specific daily work activity",
      "count": number_of_job_postings_mentioning_this,
      "context_sentences": ["sentence 1 showing this activity", "sentence 2", "sentence 3"]
    }
  ],
  "skills": [...],
  "qualifications": [...],
  "unique_aspects": [...]
}

QUALITY REQUIREMENTS:
- Each category should have 10-15 most important items
- Terms should be 15-80 characters long
- Context sentences should be clean and meaningful
- Count should reflect how many different job postings mentioned this activity
- Focus on activities that appear in multiple postings for better synthesis"""

        user_prompt = f"""Analyze these {job_title} job postings and extract the most important work activities, skills, qualifications, and unique aspects. The text contains multiple job postings - please synthesize across all of them to identify the most common and important elements.

JOB POSTINGS TEXT:
{job_postings_text[:15000]}

Please extract and categorize the key elements following the guidelines above. Focus on what people actually DO in this role on a daily basis."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                temperature=0.1,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            response_text = response.content[0].text
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
                return result
            else:
                return json.loads(response_text)
                
        except Exception as e:
            print(f"❌ Claude API error: {e}")
            return {"responsibilities": [], "skills": [], "qualifications": [], "unique_aspects": []}

    def extract_activities_rule_based(self, text: str) -> List[Tuple[str, str]]:
        """Enhanced rule-based activity extraction for fallback mode."""
        if not text:
            return []
        
        text = self.clean_html_and_artifacts(text)
        activities_with_context = []
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Enhanced action verbs for different industries
        action_verbs = {
            'administer', 'analyze', 'assess', 'assist', 'build', 'calculate', 'care', 'clean',
            'collaborate', 'collect', 'communicate', 'compile', 'complete', 'conduct', 'configure',
            'connect', 'coordinate', 'create', 'deliver', 'design', 'develop', 'diagnose',
            'document', 'educate', 'ensure', 'evaluate', 'examine', 'execute', 'facilitate',
            'implement', 'improve', 'install', 'instruct', 'interpret', 'investigate', 'maintain',
            'manage', 'monitor', 'operate', 'organize', 'oversee', 'perform', 'plan', 'prepare',
            'present', 'process', 'provide', 'record', 'repair', 'report', 'research', 'review',
            'schedule', 'supervise', 'support', 'teach', 'test', 'train', 'troubleshoot',
            'update', 'verify', 'write', 'pull', 'run', 'bend', 'terminate', 'wire'
        }
        
        # Enhanced work-related nouns
        work_nouns = {
            'care', 'records', 'reports', 'documentation', 'systems', 'equipment', 'patients',
            'clients', 'customers', 'data', 'procedures', 'protocols', 'meetings', 'training',
            'wiring', 'conduit', 'panels', 'circuits', 'electrical', 'nursing', 'medication',
            'code', 'software', 'database', 'network', 'server', 'application', 'website'
        }
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue
                
            sentence_lower = sentence.lower()
            
            # Look for responsibility patterns
            patterns = [
                r'responsible for ([^,]{20,100})',
                r'duties include ([^,]{20,100})',
                r'will ([a-z\s]{15,80}(?:patients|clients|systems|equipment|data|wiring|electrical)[^,]{0,40})',
                r'((?:coordinate|provide|maintain|manage|monitor|install|connect|analyze|develop)[^,]{20,100})',
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, sentence_lower, re.IGNORECASE)
                for match in matches:
                    activity = match.group(1).strip()
                    if 20 <= len(activity) <= 100:
                        activity = re.sub(r'\s+', ' ', activity)
                        if not any(artifact in activity for artifact in ['script', 'http', 'www']):
                            activities_with_context.append((activity, sentence))
        
        return activities_with_context

    def categorize_activity_rule_based(self, activity: str, context: str) -> str:
        """Enhanced rule-based categorization for fallback mode."""
        activity_lower = activity.lower()
        context_lower = context.lower()
        
        # Enhanced categorization rules
        if any(word in activity_lower for word in ['coordinate', 'provide', 'maintain', 'manage', 'monitor', 'install', 'connect', 'analyze', 'develop', 'perform', 'conduct']):
            return 'responsibilities'
        
        if any(word in activity_lower for word in ['python', 'java', 'javascript', 'sql', 'excel', 'software', 'programming', 'coding']):
            return 'skills'
            
        if any(word in activity_lower for word in ['degree', 'bachelor', 'master', 'experience', 'years', 'certification', 'license']):
            return 'qualifications'
            
        if any(word in activity_lower for word in ['benefits', 'remote', 'flexible', 'culture', 'salary', 'bonus']):
            return 'unique_aspects'
        
        return 'responsibilities'  # Default

    def analyze_with_fallback(self, job_postings_text: str, job_title: str) -> Dict[str, List[Dict[str, Any]]]:
        """Enhanced rule-based analysis for fallback mode."""
        
        # Extract activities using rule-based approach
        activities_with_context = self.extract_activities_rule_based(job_postings_text)
        
        # Track activities and normalize them
        activity_data = defaultdict(lambda: {'count': 0, 'sentences': set()})
        
        for activity, sentence in activities_with_context:
            # Normalize the activity
            normalized = self.normalization_dict.get(activity.lower(), activity)
            activity_data[normalized]['count'] += 1
            activity_data[normalized]['sentences'].add(sentence)
        
        # Categorize activities
        categorized = {'responsibilities': [], 'skills': [], 'qualifications': [], 'unique_aspects': []}
        
        for activity, data in activity_data.items():
            if data['count'] >= 1:  # Include all activities in fallback mode
                category = self.categorize_activity_rule_based(activity, ' '.join(list(data['sentences'])[:3]))
                
                item = {
                    'term': activity,
                    'count': data['count'],
                    'context_sentences': list(data['sentences'])[:3]
                }
                categorized[category].append(item)
        
        # Sort by count and limit results
        for category in categorized:
            categorized[category].sort(key=lambda x: x['count'], reverse=True)
            categorized[category] = categorized[category][:15]
        
        return categorized

    def generate_report_from_postings(self, postings: List[Dict[str, Any]], searched_title: str, soc_code: str) -> JobInsightsReport:
        """Generate a complete JobInsightsReport using Claude or fallback analysis."""
        if not postings:
            return JobInsightsReport(
                searched_title=searched_title,
                soc_code=soc_code,
                total_postings_analyzed=0,
                responsibilities=[], skills=[], qualifications=[], unique_aspects=[]
            )
        
        # Combine all job posting text
        combined_text = ""
        for posting in postings:
            text_fields = []
            
            if posting.get('Description'):
                text_fields.append(posting['Description'])
            elif posting.get('description'):
                text_fields.append(posting['description'])
            
            if posting.get('JobTitle'):
                text_fields.append(posting['JobTitle'])
            elif posting.get('job_title'):
                text_fields.append(posting['job_title'])
            
            posting_text = ' '.join(text_fields)
            posting_text = self.clean_html_and_artifacts(posting_text)
            
            if posting_text:
                combined_text += f"\n\n--- JOB POSTING ---\n{posting_text}"
        
        # Use Claude if available, otherwise use enhanced fallback
        if self.claude_available:
            print("🤖 Using Claude/Sonnet 4.0 for superior analysis...")
            claude_results = self.extract_and_categorize_with_claude(combined_text, searched_title)
        else:
            print("🔧 Using enhanced rule-based analysis...")
            claude_results = self.analyze_with_fallback(combined_text, searched_title)
        
        # Convert results to AnalyzedTerm objects
        categorized_terms = {'responsibilities': [], 'skills': [], 'qualifications': [], 'unique_aspects': []}
        
        for category, items in claude_results.items():
            if category in categorized_terms:
                for item in items[:15]:
                    if isinstance(item, dict) and 'term' in item:
                        analyzed_term = AnalyzedTerm(
                            term=item.get('term', ''),
                            count=item.get('count', 1),
                            context_sentences=item.get('context_sentences', [])[:3]
                        )
                        categorized_terms[category].append(analyzed_term)
        
        return JobInsightsReport(
            searched_title=searched_title,
            soc_code=soc_code,
            total_postings_analyzed=len(postings),
            responsibilities=categorized_terms['responsibilities'],
            skills=categorized_terms['skills'],
            qualifications=categorized_terms['qualifications'],
            unique_aspects=categorized_terms['unique_aspects']
        )


# Global analyzer instance
analyzer = HybridTermAnalyzer()

def generate_report_from_postings(postings: List[Dict[str, Any]], searched_title: str, soc_code: str) -> JobInsightsReport:
    """Public interface for generating reports from job postings."""
    return analyzer.generate_report_from_postings(postings, searched_title, soc_code)