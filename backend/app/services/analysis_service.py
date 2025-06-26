import nltk
import re
from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict, Counter
from app.models.pydantic_models import JobInsightsReport, AnalyzedTerm
import html

# Download required NLTK data on first import
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

class TermAnalyzer:
    """
    Core analysis engine for processing job postings and extracting meaningful daily work responsibilities.
    """
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        
        # Custom normalization dictionary for synonyms and variations
        self.normalization_dict = {
            # Electrical work activities
            'running wire': 'running and pulling wire',
            'pulling wire': 'running and pulling wire',
            'wire running': 'running and pulling wire',
            'wire pulling': 'running and pulling wire',
            'run wire': 'running and pulling wire',
            'pull wire': 'running and pulling wire',
            'running and pulling wire': 'running and pulling wire',
            
            'bending conduit': 'running and bending conduit',
            'conduit bending': 'running and bending conduit',
            'bend conduit': 'running and bending conduit',
            'running conduit': 'running and bending conduit',
            'conduit running': 'running and bending conduit',
            'running and bending conduit': 'running and bending conduit',
            
            'installing lights': 'installing lights and outlets',
            'installing outlets': 'installing lights and outlets',
            'light installation': 'installing lights and outlets',
            'outlet installation': 'installing lights and outlets',
            'install lights': 'installing lights and outlets',
            'install outlets': 'installing lights and outlets',
            'installing lights and outlets': 'installing lights and outlets',
            
            'low voltage work': 'low voltage work',
            'low voltage': 'low voltage work',
            'low voltage installation': 'low voltage work',
            'low voltage systems': 'low voltage work',
            
            'industrial work': 'industrial electrical work',
            'industrial electrical': 'industrial electrical work',
            'industrial electrical work': 'industrial electrical work',
            
            'electrical terminations': 'terminations',
            'wire terminations': 'terminations',
            'cable terminations': 'terminations',
            'terminating': 'terminations',
            'terminate': 'terminations',
            'terminations': 'terminations',
            
            # Programming languages and frameworks
            'javascript': 'javascript',
            'js': 'javascript',
            'node.js': 'node.js',
            'nodejs': 'node.js',
            'react.js': 'react',
            'reactjs': 'react',
            'vue.js': 'vue',
            'vuejs': 'vue',
            'angular.js': 'angular',
            'angularjs': 'angular',
            
            # Microsoft Office
            'ms excel': 'excel',
            'microsoft excel': 'excel',
            'ms word': 'word',
            'microsoft word': 'word',
            'ms powerpoint': 'powerpoint',
            'microsoft powerpoint': 'powerpoint',
            'ms office': 'microsoft office',
            'microsoft office': 'microsoft office',
            
            # Databases
            'mysql': 'mysql',
            'postgresql': 'postgresql',
            'postgres': 'postgresql',
            'mongodb': 'mongodb',
            'mongo': 'mongodb',
            
            # Cloud platforms
            'amazon web services': 'aws',
            'aws': 'aws',
            'google cloud platform': 'gcp',
            'google cloud': 'gcp',
            'gcp': 'gcp',
            'microsoft azure': 'azure',
            'azure': 'azure',
            
            # Common skills
            'machine learning': 'machine learning',
            'ml': 'machine learning',
            'artificial intelligence': 'artificial intelligence',
            'ai': 'artificial intelligence',
            'data analysis': 'data analysis',
            'data analytics': 'data analysis',
            'project management': 'project management',
            'project manager': 'project management',
            
            # Education levels
            'bachelor\'s degree': 'bachelor\'s degree',
            'bachelors degree': 'bachelor\'s degree',
            'bachelor degree': 'bachelor\'s degree',
            'master\'s degree': 'master\'s degree',
            'masters degree': 'master\'s degree',
            'master degree': 'master\'s degree',
            'phd': 'phd',
            'ph.d': 'phd',
            'doctorate': 'phd',
            
            # Experience levels
            'years of experience': 'years experience',
            'years experience': 'years experience',
            'work experience': 'experience',
            'professional experience': 'experience',
        }
    
    def normalize_term(self, term: str) -> str:
        """
        Normalize a term using custom rules and dictionary.
        """
        # Convert to lowercase
        term = term.lower().strip()
        
        # Remove special characters but keep spaces, hyphens, and periods
        term = re.sub(r'[^\w\s\-\.]', '', term)
        
        # Check normalization dictionary
        if term in self.normalization_dict:
            return self.normalization_dict[term]
        
        return term
    
    def clean_html_and_artifacts(self, text: str) -> str:
        """
        Clean HTML tags, script content, and other artifacts from text.
        """
        if not text:
            return ""
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove script tags and their content
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove style tags and their content
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags but keep the content
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Remove common tracking/analytics patterns
        tracking_patterns = [
            r'https?://[^\s]*\.cloudfront\.net[^\s]*',
            r'https?://[^\s]*analytics[^\s]*',
            r'https?://[^\s]*tracking[^\s]*',
            r'data-[a-zA-Z-]+=[\"\'][^\"\']*[\"\']',
            r'id=["\'][^"\']*detrack[^"\']*["\']',
            r'defer\s+src=',
            r'script\s+id=',
        ]
        
        for pattern in tracking_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+\.\S+', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_work_activities_from_text(self, text: str) -> List[Tuple[str, str]]:
        """
        Extract meaningful work activities and daily responsibilities from text.
        Returns list of (activity_phrase, original_sentence) tuples.
        """
        if not text:
            return []
        
        # Clean HTML and artifacts first
        text = self.clean_html_and_artifacts(text)
        
        activities_with_context = []
        sentences = sent_tokenize(text)
        
        # Action verbs that indicate daily work activities
        action_verbs = {
            'administer', 'analyze', 'assess', 'assist', 'build', 'calculate', 'care', 'clean',
            'collaborate', 'collect', 'communicate', 'compile', 'complete', 'conduct', 'configure',
            'connect', 'coordinate', 'create', 'deliver', 'design', 'develop', 'diagnose',
            'document', 'educate', 'ensure', 'evaluate', 'examine', 'execute', 'facilitate',
            'implement', 'improve', 'install', 'instruct', 'interpret', 'investigate', 'maintain',
            'manage', 'monitor', 'operate', 'organize', 'oversee', 'perform', 'plan', 'prepare',
            'present', 'process', 'provide', 'record', 'repair', 'report', 'research', 'review',
            'schedule', 'supervise', 'support', 'teach', 'test', 'train', 'troubleshoot',
            'update', 'verify', 'write'
        }
        
        # Work-related nouns that indicate daily activities
        work_nouns = {
            'care', 'records', 'reports', 'documentation', 'systems', 'equipment', 'patients',
            'clients', 'customers', 'data', 'information', 'procedures', 'protocols', 'policies',
            'meetings', 'presentations', 'training', 'assessments', 'evaluations', 'inspections',
            'installations', 'repairs', 'maintenance', 'operations', 'processes', 'workflows',
            'schedules', 'appointments', 'communications', 'correspondence', 'analysis', 'research',
            'wiring', 'conduit', 'panels', 'circuits', 'electrical', 'nursing', 'medication',
            'symptoms', 'vital signs', 'treatment', 'therapy', 'diagnosis'
        }
        
        for sentence in sentences:
            # Skip sentences that are too short or contain artifacts
            if len(sentence.strip()) < 15:
                continue
            
            # Skip sentences with HTML/script artifacts
            if any(artifact in sentence.lower() for artifact in ['script', 'detrack', 'defer', 'src=', 'data-g=']):
                continue
            
            sentence_lower = sentence.lower()
            
            # Look for responsibility patterns
            responsibility_patterns = [
                r'responsible for ([^.]{15,100})',
                r'duties include ([^.]{15,100})',
                r'will ([a-z\s]{10,80}(?:patients|clients|customers|records|data|equipment|systems|wiring|electrical|nursing|care)[^.]{0,40})',
                r'([a-z\s]{10,80}(?:and|or)\s+(?:providing|maintaining|managing|coordinating|monitoring|installing|connecting|updating|recording)[^.]{5,60})',
                r'((?:coordinate|provide|maintain|manage|monitor|update|record|document|assist|support|ensure|install|connect|wire|administer)[^.]{15,100})',
                r'((?:performing|conducting|implementing|developing|creating|building|installing|repairing|connecting|wiring)[^.]{15,100})',
                r'((?:observing|monitoring|recording|updating|coordinating|providing|installing|connecting)[^.]{15,100})',
            ]
            
            for pattern in responsibility_patterns:
                matches = re.finditer(pattern, sentence_lower, re.IGNORECASE)
                for match in matches:
                    activity = match.group(1).strip()
                    if len(activity) > 15 and len(activity) < 120:
                        # Clean up the activity phrase
                        activity = re.sub(r'\s+', ' ', activity)
                        activity = activity.strip(' .,;:')
                        if activity and not any(artifact in activity for artifact in ['script', 'http', 'www', '.com']):
                            activities_with_context.append((activity, sentence))
            
            # Look for action verb + object patterns
            tokens = word_tokenize(sentence_lower)
            for i, token in enumerate(tokens):
                if token in action_verbs:
                    # Look for meaningful phrases starting with action verbs
                    # Extract 3-10 word phrases that include the action verb
                    for length in range(3, 11):
                        if i + length <= len(tokens):
                            phrase_tokens = tokens[i:i+length]
                            phrase = ' '.join(phrase_tokens)
                            
                            # Check if phrase contains work-related nouns or meaningful content
                            if (any(noun in phrase for noun in work_nouns) or 
                                any(word in phrase for word in ['with', 'for', 'to', 'and', 'or']) and
                                len(phrase) > 20 and len(phrase) < 100):
                                
                                # Clean up the phrase
                                phrase = re.sub(r'\s+', ' ', phrase)
                                phrase = phrase.strip(' .,;:')
                                
                                if (phrase and 
                                    not any(artifact in phrase for artifact in ['script', 'http', 'www', '.com']) and
                                    not phrase.startswith(('the ', 'a ', 'an '))):
                                    activities_with_context.append((phrase, sentence))
            
            # Look for gerund phrases (activities ending in -ing)
            gerund_pattern = r'([a-z\s]*(?:ing)\s+[a-z\s]{10,70}(?:patients|clients|records|data|equipment|systems|procedures|protocols|wiring|electrical|nursing|care|medication|symptoms)[^.]{0,40})'
            matches = re.finditer(gerund_pattern, sentence_lower)
            for match in matches:
                activity = match.group(1).strip()
                if len(activity) > 20 and len(activity) < 100:
                    activity = re.sub(r'\s+', ' ', activity)
                    activity = activity.strip(' .,;:')
                    if activity and not any(artifact in activity for artifact in ['script', 'http', 'www']):
                        activities_with_context.append((activity, sentence))
        
        return activities_with_context
    
    def categorize_activity(self, activity: str, context_sentences: List[str]) -> str:
        """
        Categorize a work activity based on its content and context.
        Focus on distinguishing daily responsibilities from skills/qualifications.
        """
        activity_lower = activity.lower()
        context_text = ' '.join(context_sentences).lower()
        
        # Strong indicators for responsibilities (daily work activities)
        responsibility_indicators = {
            'action_verbs': ['coordinate', 'provide', 'maintain', 'manage', 'monitor', 'update', 'record', 
                           'document', 'assist', 'support', 'ensure', 'perform', 'conduct', 'implement',
                           'administer', 'deliver', 'operate', 'supervise', 'oversee', 'execute', 'install',
                           'connect', 'wire', 'observe', 'care', 'treat', 'diagnose', 'assess'],
            'work_objects': ['patients', 'clients', 'records', 'data', 'equipment', 'systems', 'care',
                           'procedures', 'protocols', 'meetings', 'reports', 'documentation', 'operations',
                           'wiring', 'electrical', 'conduit', 'panels', 'circuits', 'nursing', 'medication',
                           'symptoms', 'vital signs', 'treatment', 'therapy'],
            'responsibility_phrases': ['responsible for', 'duties include', 'will be', 'day to day', 'daily']
        }
        
        # Strong indicators for skills (tools, technologies, abilities)
        skill_indicators = {
            'technologies': ['python', 'java', 'javascript', 'sql', 'excel', 'powerpoint', 'tableau',
                           'aws', 'azure', 'linux', 'windows', 'docker', 'kubernetes', 'git'],
            'soft_skills': ['communication', 'leadership', 'teamwork', 'problem solving', 'analytical',
                          'organizational', 'interpersonal', 'critical thinking'],
            'technical_skills': ['programming', 'coding', 'software', 'database', 'network', 'security'],
            'skill_phrases': ['proficient in', 'experience with', 'knowledge of', 'skilled in', 'ability to']
        }
        
        # Strong indicators for qualifications (education, experience, certifications)
        qualification_indicators = {
            'education': ['degree', 'bachelor', 'master', 'phd', 'diploma', 'certification', 'certified',
                        'license', 'licensed', 'accredited'],
            'experience': ['years experience', 'years of experience', 'minimum', 'required', 'preferred',
                         'background in', 'knowledge of', 'familiarity with', 'proficiency in'],
            'requirements': ['must have', 'should have', 'required', 'preferred', 'minimum', 'qualifications']
        }
        
        # Score each category
        scores = {'responsibilities': 0, 'skills': 0, 'qualifications': 0, 'unique_aspects': 0}
        
        # Check for responsibility indicators
        for indicator_type, indicators in responsibility_indicators.items():
            for indicator in indicators:
                if indicator in activity_lower:
                    scores['responsibilities'] += 3
                if indicator in context_text:
                    scores['responsibilities'] += 1
        
        # Check for skill indicators
        for indicator_type, indicators in skill_indicators.items():
            for indicator in indicators:
                if indicator in activity_lower:
                    scores['skills'] += 3
                if indicator in context_text:
                    scores['skills'] += 1
        
        # Check for qualification indicators
        for indicator_type, indicators in qualification_indicators.items():
            for indicator in indicators:
                if indicator in activity_lower:
                    scores['qualifications'] += 3
                if indicator in context_text:
                    scores['qualifications'] += 1
        
        # Additional context-based scoring
        if any(phrase in context_text for phrase in ['responsible for', 'duties', 'will', 'day to day']):
            scores['responsibilities'] += 2
        
        if any(phrase in context_text for phrase in ['experience with', 'knowledge of', 'proficient in']):
            scores['skills'] += 2
            
        if any(phrase in context_text for phrase in ['required', 'minimum', 'must have', 'degree']):
            scores['qualifications'] += 2
        
        if any(phrase in context_text for phrase in ['benefits', 'salary', 'remote', 'flexible', 'culture']):
            scores['unique_aspects'] += 2
        
        # Default to responsibilities if it's an action-oriented phrase
        if any(verb in activity_lower for verb in ['coordinate', 'provide', 'maintain', 'manage', 'monitor', 'install', 'connect', 'wire', 'observe', 'care']):
            scores['responsibilities'] += 1
        
        # Return category with highest score
        max_category = max(scores.items(), key=lambda x: x[1])
        return max_category[0] if max_category[1] > 0 else 'responsibilities'
    
    def generate_report_from_postings(self, postings: List[Dict[str, Any]], searched_title: str, soc_code: str) -> JobInsightsReport:
        """
        Generate a complete JobInsightsReport from raw job postings.
        """
        if not postings:
            return JobInsightsReport(
                searched_title=searched_title,
                soc_code=soc_code,
                total_postings_analyzed=0,
                responsibilities=[],
                skills=[],
                qualifications=[],
                unique_aspects=[]
            )
        
        # Track activities and their contexts
        activity_contexts = defaultdict(lambda: {'count': 0, 'sentences': set(), 'postings': set()})
        
        # Process each job posting
        for i, posting in enumerate(postings):
            # Extract text from various fields
            text_fields = []
            
            # Get job description (main content)
            if posting.get('Description'):
                text_fields.append(posting['Description'])
            elif posting.get('description'):
                text_fields.append(posting['description'])
            
            # Get job title and company for additional context
            if posting.get('JobTitle'):
                text_fields.append(posting['JobTitle'])
            elif posting.get('job_title'):
                text_fields.append(posting['job_title'])
            
            # Combine all text and clean it
            combined_text = ' '.join(text_fields)
            combined_text = self.clean_html_and_artifacts(combined_text)
            
            # Extract work activities from this posting
            activities_with_context = self.extract_work_activities_from_text(combined_text)
            
            # Track unique activities per posting (count once per posting)
            posting_activities = set()
            
            for activity, sentence in activities_with_context:
                # Normalize the activity to group similar terms
                normalized_activity = self.normalize_term(activity)
                
                if normalized_activity not in posting_activities:
                    posting_activities.add(normalized_activity)
                    activity_contexts[normalized_activity]['count'] += 1
                    activity_contexts[normalized_activity]['postings'].add(i)
                
                # Always add sentences for context (up to 3 per activity)
                if len(activity_contexts[normalized_activity]['sentences']) < 3:
                    activity_contexts[normalized_activity]['sentences'].add(sentence)
        
        # Categorize and rank activities
        categorized_terms = {
            'responsibilities': [],
            'skills': [],
            'qualifications': [],
            'unique_aspects': []
        }
        
        for activity, data in activity_contexts.items():
            # Filter out technical artifacts and meaningless activities
            if any(artifact in activity.lower() for artifact in [
                'script', 'detrack', 'defer', 'src', 'http', 'www', '.com', '.net',
                'data-g', 'id=', 'class=', 'div', 'span', 'href', 'onclick'
            ]):
                continue
            
            # Filter out very generic or short activities
            if len(activity) < 15 or activity.lower() in ['work', 'job', 'position', 'role', 'duties']:
                continue
            
            # Include activities that appear in multiple postings for better synthesis
            # Lowered threshold to capture more diverse content while filtering noise
            if data['count'] >= 2 or len(data['postings']) >= 2:
                category = self.categorize_activity(activity, list(data['sentences']))
                
                # Clean context sentences
                clean_sentences = []
                for sentence in list(data['sentences'])[:3]:
                    clean_sentence = self.clean_html_and_artifacts(sentence)
                    if len(clean_sentence) > 20:  # Only include substantial sentences
                        clean_sentences.append(clean_sentence)
                
                if clean_sentences:  # Only add if we have clean context
                    analyzed_term = AnalyzedTerm(
                        term=activity,
                        count=data['count'],
                        context_sentences=clean_sentences
                    )
                    
                    categorized_terms[category].append(analyzed_term)
        
        # Sort each category by count (descending) and limit to top 15
        for category in categorized_terms:
            categorized_terms[category].sort(key=lambda x: x.count, reverse=True)
            categorized_terms[category] = categorized_terms[category][:15]
        
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
analyzer = TermAnalyzer()

def generate_report_from_postings(postings: List[Dict[str, Any]], searched_title: str, soc_code: str) -> JobInsightsReport:
    """
    Public interface for generating reports from job postings.
    """
    return analyzer.generate_report_from_postings(postings, searched_title, soc_code)