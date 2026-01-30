"""CiviNigrani Intelligence Module - News, Root Cause Analysis & Peer Comparison"""

from .news_analyzer import (
    get_district_intelligence,
    analyze_multiple_districts,
    search_district_news,
    analyze_root_causes
)

from .peerlens import PeerLens

__all__ = [
    'get_district_intelligence',
    'analyze_multiple_districts',
    'search_district_news',
    'analyze_root_causes',
    'PeerLens'
]
