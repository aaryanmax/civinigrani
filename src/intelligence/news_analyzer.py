"""
═══════════════════════════════════════════════════════════════════════════════
NEWS INTELLIGENCE MODULE
═══════════════════════════════════════════════════════════════════════════════

This module scrapes and analyzes news articles to identify root causes of
delivery gaps in high-risk districts.

Root Causes Detected:
    - 💰 Corruption (bribery, scams, ghotal)
    - 📚 Awareness Issues (literacy, information gaps)
    - ⚙️ Infrastructure Problems (ePoS, tech failures)
    - 🚚 Supply Chain Delays (transport, stock issues)

Author: CiviNigrani Team
Created: January 2026
═══════════════════════════════════════════════════════════════════════════════
"""

import os
from dotenv import load_dotenv
import requests
import re
from typing import Dict, List
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# News API key (free tier: 100 requests/day)
# Get your key at: https://newsapi.org/register
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Keywords for each root cause category
ROOT_CAUSE_KEYWORDS = {
    'corruption': ['corrupt', 'brib', 'ghotal', 'scam', 'fraud', 'illegal', 'मिलीभगत'],
    'awareness': ['aware', 'literacy', 'educat', 'inform', 'knowledge', 'जागरूकता',  'शिक्षा'],
    'infrastructure': ['infrastruct', 'epos', 'tech', 'system', 'machine', 'breakdown', 'तकनीकी'],
    'supply_chain': ['supply', 'transport', 'delay', 'stock', 'shortage', 'आपूर्ति', 'कमी']
}


# ═══════════════════════════════════════════════════════════════════════════════
# NEWS SCRAPING (Live or Demo Mode)
# ═══════════════════════════════════════════════════════════════════════════════

def search_district_news(
    district: str,
    lookback_days: int = 30,
    use_demo_mode: bool = False
) -> List[Dict]:
    """
    Search for PDS-related news articles about a specific district.
    
    Args:
        district (str): Name of the district
        lookback_days (int): How many days back to search (default: 30)
        use_demo_mode (bool): If True, return mock data. Defaults to False if API key present.
        
    Returns:
        List[Dict]: List of articles with 'title', 'description', 'url'
    """
    # Auto-detect mode if key is missing
    if not NEWS_API_KEY and not use_demo_mode:
        print("⚠️  No NEWS_API_KEY found. Falling back to DEMO MODE.")
        use_demo_mode = True
    
    if use_demo_mode:
        # Return simulated news articles for demonstration
        return generate_mock_news(district)
    
    # REAL API MODE
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        # Build search queries
        queries = [
            f"{district} PDS corruption",
            f"{district} ration card",
            f"{district} fair price shop"
        ]
        
        all_articles = []
        
        for query in queries:
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'from': start_date.strftime('%Y-%m-%d'),
                'sortBy': 'relevancy',
                'language': 'en',
                'apiKey': NEWS_API_KEY
            }
            
            # Try fetching with requested date range
            response = requests.get(url, params=params)
            
            # Handle Free Tier constraint (older than 30 days)
            if response.status_code == 426 or response.status_code == 429:
                print(f"⚠️ API Limit/Plan restriction for {district}. Retrying with 30-day window...")
                # Fallback to last 30 days
                fallback_start = datetime.now() - timedelta(days=30)
                params['from'] = fallback_start.strftime('%Y-%m-%d')
                response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                all_articles.extend(articles)
            else:
                print(f"Error fetching news for {district}: {response.status_code} - {response.text}")
                
        # Deduplicate by title
        seen_titles = set()
        unique_articles = []
        for art in all_articles:
            title = art.get('title', '')
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_articles.append({
                    'title': title,
                    'description': art.get('description', ''),
                    'url': art.get('url', ''),
                    'publishedAt': art.get('publishedAt', ''),
                    'source': art.get('source', {}).get('name', 'Unknown')
                })
        
        return unique_articles[:10]  # Return top 10 unique articles
        
    except Exception as e:
        print(f"Exception in news scraper: {str(e)}")
        return generate_mock_news(district)  # Fallback to demo on error


def generate_mock_news(district: str) -> List[Dict]:
    """
    Generate realistic mock news articles for demo purposes.
    
    Args:
        district (str): District name
        
    Returns:
        List[Dict]: Simulated news articles
    """
    
    # Templates for different root causes
    templates = {
        'corruption': [
            f"{district} PDS Officials Accused of Bribery in Ration Distribution",
            f"Scam Exposed: {district} Fair Price Shops Selling Government Grains to Black Market",
            f"{district} Ration Card Fraud: Officials Demand Illegal Fees from Poor Families"
        ],
        'awareness': [
            f"{district} Villagers Unaware of New Digital Ration Card System",
            f"Low Literacy Hampers PDS Access in Rural {district}",
            f"Lack of Information: {district} Residents Miss Out on Food Entitlements"
        ],
        'infrastructure': [
            f"ePoS Machines Down: {district} Fair Price Shops Unable to Distribute Rations",
            f"Technical Glitches Plague {district} PDS Distribution Centers",
            f"{district} Ration Shops Struggle with Outdated Technology"
        ],
        'supply_chain': [
            f"Transport Strike Delays Food Grain Delivery to {district} PDS Shops",
            f"{district} Faces Acute Shortage of Rice and Wheat Stocks",
            f"Supply Chain Breakdown: {district} Ration Shops Run Out of Grains"
        ]
    }
    
    # Randomly select 2-3 articles from different categories
    import random
    
    articles = []
    selected_causes = random.sample(list(templates.keys()), k=min(3, len(templates)))
    
    for cause in selected_causes:
        title = random.choice(templates[cause])
        articles.append({
            'title': title,
            'description': f"Recent reports from {district} highlight issues related to {cause.replace('_', ' ')}.",
            'url': f"https://example.com/news/{district.lower()}-{cause}",
            'publishedAt': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
        })
    
    return articles


# ═══════════════════════════════════════════════════════════════════════════════
# TEXT ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_root_causes(articles: List[Dict]) -> Dict:
    """
    Analyze news articles to identify primary root causes.
    
    Algorithm:
        1. Extract text from titles and descriptions
        2. Count keyword matches for each root cause category
        3. Rank causes by frequency
        4. Return top cause + breakdown
        
    Args:
        articles: List of news articles from search_district_news()
        
    Returns:
        Dict with keys:
            - top_root_cause (str): Primary cause identified
            - cause_breakdown (Dict[str, int]): Counts for each category
            - article_count (int): Total articles analyzed
            - sample_headlines (List[str]): Top 3 article titles
    """
    
    # Initialize counters
    cause_scores = {
        'corruption': 0,
        'awareness': 0,
        'infrastructure': 0,
        'supply_chain': 0
    }
    
    # Analyze each article
    for article in articles:
        text = (article.get('title', '') + ' ' + article.get('description', '')).lower()
        
        # Count keyword matches
        for cause, keywords in ROOT_CAUSE_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    cause_scores[cause] += 1
    
    # Determine top cause
    if sum(cause_scores.values()) == 0:
        top_cause = "Insufficient Data"
    else:
        top_cause = max(cause_scores, key=cause_scores.get)
    
    # Format results
    results = {
        'top_root_cause': top_cause.replace('_', ' ').title(),
        'cause_breakdown': cause_scores,
        'article_count': len(articles),
        'sample_headlines': [a['title'] for a in articles[:3]],
        'confidence': 'High' if cause_scores[top_cause] >= 3 else 'Medium' if cause_scores[top_cause] >= 1 else 'Low'
    }
    
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# COMBINED ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def get_district_intelligence(
    district: str,
    lookback_days: int = 30
) -> Dict:
    """
    Get complete root cause intelligence for a district.
    
    This is the main function to call from the dashboard.
    
    Args:
        district (str): District name
        lookback_days (int): Days to look back for news
        
    Returns:
        Dict: Complete intelligence report
    """
    
    print(f"\n{f' ANALYZING {district.upper()} ':═^80}")
    
    # Step 1: Fetch news
    # use_demo_mode defaults to False -> will try API key if present
    articles = search_district_news(district, lookback_days, use_demo_mode=False)
    
    if not articles:
        return {
            'district': district,
            'top_root_cause': 'No Data Available',
            'cause_breakdown': {},
            'article_count': 0,
            'sample_headlines': [],
            'confidence': 'None'
        }
    
    # Step 2: Analyze causes
    analysis = analyze_root_causes(articles)
    analysis['district'] = district
    
    print(f"✅ Found {analysis['article_count']} articles")
    print(f"🎯 Top Cause: {analysis['top_root_cause']} ({analysis['confidence']} confidence)")
    
    return analysis


# ═══════════════════════════════════════════════════════════════════════════════
# BATCH PROCESSING
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_multiple_districts(districts: List[str]) -> List[Dict]:
    """
    Analyze root causes for multiple districts in batch.
    
    Args:
        districts: List of district names
        
    Returns:
        List[Dict]: Intelligence reports for each district
    """
    
    results = []
    
    for district in districts:
        intelligence = get_district_intelligence(district)
        results.append(intelligence)
    
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO / TESTING
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Test with sample districts
    test_districts = ["Agra", "Lucknow", "Gorakhpur"]
    
    print(f"\n{'═' * 80}")
    print(f"{'NEWS INTELLIGENCE DEMO':^80}")
    print(f"{'═' * 80}\n")
    
    for district in test_districts:
        report = get_district_intelligence(district, lookback_days=30)
        
        print(f"\n{'─' * 80}")
        print(f"📍 {report['district']}")
        print(f"{'─' * 80}")
        print(f"🎯 Primary Issue: {report['top_root_cause']}")
        print(f"📊 Cause Breakdown:")
        for cause, count in report['cause_breakdown'].items():
            print(f"   - {cause.replace('_', ' ').title()}: {count} mentions")
        print(f"\n📰 Sample Headlines:")
        for i, headline in enumerate(report['sample_headlines'], 1):
            print(f"   {i}. {headline}")
