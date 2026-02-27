"""
News Service Module for Secure Intelligent Desktop Assistant
Fetches top headlines using News API
"""

import requests
import logging
from pathlib import Path
import sys

# Import config
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


class NewsService:
    """
    News Service
    Fetches news headlines from News API
    """
    
    def __init__(self, api_key=None):
        """
        Initialize news service
        
        Args:
            api_key: News API key
        """
        self.logger = logging.getLogger('DesktopAssistant.News')
        self.api_key = api_key or config.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"
        
        if self.api_key == "YOUR_API_KEY_HERE":
            self.logger.warning("News API key not configured")
        
        self.logger.info("News Service initialized")
    
    def get_top_headlines(self, country='us', category=None, max_results=10):
        """
        Get top headlines
        
        Args:
            country: Country code (us, gb, etc.)
            category: News category (technology, business, sports, etc.)
            max_results: Maximum number of results
            
        Returns:
            List of news articles
        """
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            self.logger.error("API key not configured")
            return self._get_demo_headlines()
        
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                'country': country,
                'apiKey': self.api_key,
                'pageSize': max_results
            }
            
            if category:
                params['category'] = category
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_articles(data.get('articles', []))
            elif response.status_code == 401:
                self.logger.error("Invalid API key")
                return self._get_demo_headlines()
            else:
                self.logger.error(f"News API error: {response.status_code}")
                return self._get_demo_headlines()
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            return self._get_demo_headlines()
    
    def search_news(self, query, max_results=10):
        """
        Search for news
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of news articles
        """
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            self.logger.error("API key not configured")
            return self._get_demo_headlines()
        
        try:
            url = f"{self.base_url}/everything"
            params = {
                'q': query,
                'apiKey': self.api_key,
                'pageSize': max_results,
                'sortBy': 'publishedAt'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_articles(data.get('articles', []))
            else:
                self.logger.error(f"News API error: {response.status_code}")
                return self._get_demo_headlines()
        
        except Exception as e:
            self.logger.error(f"Error searching news: {e}")
            return self._get_demo_headlines()
    
    def _parse_articles(self, articles):
        """
        Parse news articles
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            List of parsed articles
        """
        parsed = []
        
        for article in articles:
            parsed.append({
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'source': article.get('source', {}).get('name', ''),
                'author': article.get('author', ''),
                'url': article.get('url', ''),
                'image': article.get('urlToImage', ''),
                'published': article.get('publishedAt', '')
            })
        
        return parsed
    
    def _get_demo_headlines(self):
        """Get demo headlines when API is not available"""
        return [
            {
                'title': 'Demo Headline 1: Your AI Assistant is Ready',
                'description': 'Configure your News API key to get real headlines.',
                'source': 'Demo News',
                'author': 'System',
                'url': '',
                'image': '',
                'published': ''
            },
            {
                'title': 'Demo Headline 2: Weather Service Active',
                'description': 'Configure OpenWeather API for real weather data.',
                'source': 'Demo News',
                'author': 'System',
                'url': '',
                'image': '',
                'published': ''
            },
            {
                'title': 'Demo Headline 3: Face Recognition Enabled',
                'description': 'Enroll your face for secure authentication.',
                'source': 'Demo News',
                'author': 'System',
                'url': '',
                'image': '',
                'published': ''
            }
        ]
    
    def get_headlines_report(self, country='us', category=None, max_headlines=3):
        """
        Get headlines report
        
        Args:
            country: Country code
            category: News category
            max_headlines: Number of headlines to include
            
        Returns:
            Report string
        """
        articles = self.get_top_headlines(country, category, max_headlines)
        
        if not articles:
            return "Sorry, I couldn't get the latest news."
        
        report = "Here are the top headlines. "
        
        for i, article in enumerate(articles, 1):
            title = article['title']
            # Clean title
            title = title.replace('...', '').strip()
            
            report += f"{i}. {title}. "
        
        return report
    
    def speak_headlines(self, country='us', category=None, voice_engine=None, max_headlines=3):
        """
        Speak headlines
        
        Args:
            country: Country code
            category: News category
            voice_engine: Voice engine for TTS
            max_headlines: Number of headlines to speak
            
        Returns:
            Headlines report string
        """
        report = self.get_headlines_report(country, category, max_headlines)
        
        if voice_engine:
            voice_engine.speak(report)
        
        return report
    
    def get_news_by_category(self, category, max_results=5):
        """
        Get news by category
        
        Args:
            category: Category name (business, entertainment, general, health, science, sports, technology)
            max_results: Maximum results
            
        Returns:
            List of articles
        """
        return self.get_top_headlines(category=category, max_results=max_results)
    
    def get_technology_news(self, max_results=5):
        """Get technology news"""
        return self.get_news_by_category('technology', max_results)
    
    def get_business_news(self, max_results=5):
        """Get business news"""
        return self.get_news_by_category('business', max_results)
    
    def get_sports_news(self, max_results=5):
        """Get sports news"""
        return self.get_news_by_category('sports', max_results)


# ============================================
# Main function for testing
# ============================================

def test_news_service():
    """Test news service"""
    print("Testing News Service...")
    
    service = NewsService()
    
    # Get top headlines
    print("\nGetting top headlines...")
    headlines = service.get_top_headlines(max_results=5)
    
    print("\n" + "="*60)
    print("Top Headlines:")
    print("="*60)
    
    for i, article in enumerate(headlines, 1):
        print(f"\n{i}. {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   Description: {article['description'][:100]}...")
    
    # Get report
    print("\n" + "="*60)
    print("Headlines Report:")
    print("="*60)
    report = service.get_headlines_report(max_headlines=3)
    print(report)
    
    return service


if __name__ == "__main__":
    test_news_service()
