import json
import os
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.models.pydantic_models import JobInsightsReport

class AnalysisCacheService:
    """
    Service for caching job analysis results to avoid repeated Claude API calls.
    """
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.ensure_cache_directory()
    
    def ensure_cache_directory(self):
        """Ensure the cache directory exists."""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _generate_cache_key(self, soc_code: str, job_title: str) -> str:
        """Generate a unique cache key for the analysis."""
        # Create a hash based on SOC code and job title
        key_string = f"{soc_code}_{job_title.lower().replace(' ', '_')}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> str:
        """Get the full path to the cache file."""
        return os.path.join(self.cache_dir, f"analysis_{cache_key}.json")
    
    def get_cached_analysis(self, soc_code: str, job_title: str, max_age_hours: int = 24) -> Optional[JobInsightsReport]:
        """
        Retrieve cached analysis if it exists and is not expired.
        
        Args:
            soc_code: The SOC code for the job
            job_title: The job title
            max_age_hours: Maximum age of cache in hours (default 24 hours)
            
        Returns:
            JobInsightsReport if cached and valid, None otherwise
        """
        try:
            cache_key = self._generate_cache_key(soc_code, job_title)
            cache_file = self._get_cache_file_path(cache_key)
            
            if not os.path.exists(cache_file):
                return None
            
            # Check if cache is expired
            file_modified_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
            expiry_time = file_modified_time + timedelta(hours=max_age_hours)
            
            if datetime.now() > expiry_time:
                print(f"🕒 Cache expired for {job_title} (SOC: {soc_code})")
                # Optionally remove expired cache file
                os.remove(cache_file)
                return None
            
            # Load cached data
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # Convert back to JobInsightsReport
            report = JobInsightsReport(**cached_data)
            print(f"✅ Using cached analysis for {job_title} (SOC: {soc_code})")
            return report
            
        except Exception as e:
            print(f"⚠️ Error loading cached analysis: {e}")
            return None
    
    def cache_analysis(self, soc_code: str, job_title: str, report: JobInsightsReport) -> bool:
        """
        Cache the analysis results.
        
        Args:
            soc_code: The SOC code for the job
            job_title: The job title
            report: The JobInsightsReport to cache
            
        Returns:
            True if successfully cached, False otherwise
        """
        try:
            cache_key = self._generate_cache_key(soc_code, job_title)
            cache_file = self._get_cache_file_path(cache_key)
            
            # Convert report to dict for JSON serialization
            report_dict = report.dict()
            
            # Add metadata
            cache_data = {
                **report_dict,
                "_cache_metadata": {
                    "cached_at": datetime.now().isoformat(),
                    "soc_code": soc_code,
                    "job_title": job_title,
                    "cache_key": cache_key
                }
            }
            
            # Write to cache file
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Cached analysis for {job_title} (SOC: {soc_code})")
            return True
            
        except Exception as e:
            print(f"⚠️ Error caching analysis: {e}")
            return False
    
    def clear_cache(self, soc_code: str = None, job_title: str = None) -> int:
        """
        Clear cached analyses.
        
        Args:
            soc_code: If provided, only clear cache for this SOC code
            job_title: If provided, only clear cache for this job title
            
        Returns:
            Number of cache files removed
        """
        try:
            removed_count = 0
            
            if soc_code and job_title:
                # Clear specific cache
                cache_key = self._generate_cache_key(soc_code, job_title)
                cache_file = self._get_cache_file_path(cache_key)
                if os.path.exists(cache_file):
                    os.remove(cache_file)
                    removed_count = 1
            else:
                # Clear all cache files
                for filename in os.listdir(self.cache_dir):
                    if filename.startswith("analysis_") and filename.endswith(".json"):
                        file_path = os.path.join(self.cache_dir, filename)
                        os.remove(file_path)
                        removed_count += 1
            
            print(f"🗑️ Cleared {removed_count} cached analysis files")
            return removed_count
            
        except Exception as e:
            print(f"⚠️ Error clearing cache: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            cache_files = [f for f in os.listdir(self.cache_dir) 
                          if f.startswith("analysis_") and f.endswith(".json")]
            
            total_size = 0
            oldest_file = None
            newest_file = None
            
            for filename in cache_files:
                file_path = os.path.join(self.cache_dir, filename)
                file_size = os.path.getsize(file_path)
                file_time = os.path.getmtime(file_path)
                
                total_size += file_size
                
                if oldest_file is None or file_time < oldest_file[1]:
                    oldest_file = (filename, file_time)
                
                if newest_file is None or file_time > newest_file[1]:
                    newest_file = (filename, file_time)
            
            return {
                "total_cached_analyses": len(cache_files),
                "total_cache_size_bytes": total_size,
                "total_cache_size_mb": round(total_size / (1024 * 1024), 2),
                "oldest_cache": {
                    "file": oldest_file[0] if oldest_file else None,
                    "created_at": datetime.fromtimestamp(oldest_file[1]).isoformat() if oldest_file else None
                } if oldest_file else None,
                "newest_cache": {
                    "file": newest_file[0] if newest_file else None,
                    "created_at": datetime.fromtimestamp(newest_file[1]).isoformat() if newest_file else None
                } if newest_file else None
            }
            
        except Exception as e:
            print(f"⚠️ Error getting cache stats: {e}")
            return {"error": str(e)}


# Global cache service instance
cache_service = AnalysisCacheService()