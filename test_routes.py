#!/usr/bin/env python3
"""
Quick test script to check Messages and Tickets functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_routes():
    """Test if routes are properly registered."""
    app = create_app()
    
    with app.app_context():
        print("🔥 Testing Phoenix Routes")
        print("=" * 50)
        
        # Get all registered routes
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append((rule.rule, rule.endpoint, list(rule.methods)))
        
        # Filter for messages and support routes
        print("\n📧 MESSAGE ROUTES:")
        message_routes = [r for r in routes if 'messages' in r[0] or 'messages' in r[1]]
        for route, endpoint, methods in message_routes:
            print(f"  {route:<30} -> {endpoint:<30} {methods}")
        
        print("\n🎫 SUPPORT ROUTES:")
        support_routes = [r for r in routes if 'support' in r[0] or 'support' in r[1]]
        for route, endpoint, methods in support_routes:
            print(f"  {route:<30} -> {endpoint:<30} {methods}")
        
        print(f"\n✅ Total routes: {len(routes)}")
        print(f"📧 Message routes: {len(message_routes)}")
        print(f"🎫 Support routes: {len(support_routes)}")

if __name__ == '__main__':
    test_routes()
