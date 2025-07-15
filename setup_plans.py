#!/usr/bin/env python3
"""
Script to add the 4 new subscription plans to Phoenix platform
Run this script to initialize the plans in Firestore database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from datetime import datetime

def add_plans():
    """Add the 4 subscription plans to Firestore"""
    app = create_app()
    
    with app.app_context():
        db = app.db
        plans_collection = db.collection('plans')
        
        # Define the 4 plans
        plans = [
            {
                'id': 'free',
                'name': 'Free',
                'description': 'Perfekt für Einsteiger und kleine Projekte',
                'price_monthly': 0.00,
                'price_yearly': 0.00,
                'currency': 'EUR',
                'order': 1,
                'is_active': True,
                'features': {
                    'active_projects': 1,
                    'milestones_per_project': 3,
                    'tasks_per_project': 30,
                    'additional_team_members': 1,
                    'storage_per_project_mb': 5,
                    'priority_support': False,
                    'api_access': False
                },
                'feature_list': [
                    '1 aktives Projekt',
                    '3 Meilensteine pro Projekt',
                    '30 Aufgaben pro Projekt',
                    '1 zusätzliches Teammitglied',
                    '5MB Speicher pro Projekt'
                ],
                'color': '#6b7280',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            },
            {
                'id': 'premium',
                'name': 'Premium',
                'description': 'Ideal für kleine Teams und wachsende Projekte',
                'price_monthly': 4.99,
                'price_yearly': 49.99,
                'currency': 'EUR',
                'order': 2,
                'is_active': True,
                'features': {
                    'active_projects': 5,
                    'milestones_per_project': 10,
                    'tasks_per_project': 100,
                    'additional_team_members': 5,
                    'storage_per_project_mb': 15,
                    'priority_support': True,
                    'api_access': False
                },
                'feature_list': [
                    '5 aktive Projekte',
                    '10 Meilensteine pro Projekt',
                    '100 Aufgaben pro Projekt',
                    '5 zusätzliche Teammitglieder',
                    '15MB Speicher pro Projekt',
                    'Priority Support'
                ],
                'color': '#3b82f6',
                'badge': 'Beliebt',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            },
            {
                'id': 'pro',
                'name': 'Pro',
                'description': 'Perfekt für professionelle Teams und große Projekte',
                'price_monthly': 9.99,
                'price_yearly': 99.99,
                'currency': 'EUR',
                'order': 3,
                'is_active': True,
                'features': {
                    'active_projects': 15,
                    'milestones_per_project': 30,
                    'tasks_per_project': 300,
                    'additional_team_members': 15,
                    'storage_per_project_mb': 50,
                    'priority_support': True,
                    'api_access': True
                },
                'feature_list': [
                    '15 aktive Projekte',
                    '30 Meilensteine pro Projekt',
                    '300 Aufgaben pro Projekt',
                    '15 zusätzliche Teammitglieder',
                    '50MB Speicher pro Projekt',
                    'Priority Support',
                    'API Zugang'
                ],
                'color': '#10b981',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            },
            {
                'id': 'unlimited',
                'name': 'Unlimited',
                'description': 'Für Unternehmen ohne Grenzen',
                'price_monthly': 34.99,
                'price_yearly': 349.99,
                'currency': 'EUR',
                'order': 4,
                'is_active': True,
                'features': {
                    'active_projects': -1,  # -1 means unlimited
                    'milestones_per_project': -1,
                    'tasks_per_project': -1,
                    'additional_team_members': -1,
                    'storage_per_project_mb': 100,
                    'priority_support': True,
                    'api_access': True,
                    'full_api_access': True
                },
                'feature_list': [
                    'Unbegrenzte Projekte',
                    'Unbegrenzte Meilensteine',
                    'Unbegrenzte Aufgaben',
                    'Unbegrenzte Teammitglieder',
                    '100MB Speicher pro Projekt',
                    'Priority Support',
                    'Voller API Zugang'
                ],
                'color': '#f59e0b',
                'badge': 'Enterprise',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
        ]
        
        # Add each plan to Firestore
        for plan in plans:
            plan_id = plan.pop('id')  # Remove id from data
            
            # Check if plan already exists
            existing_plan = plans_collection.document(plan_id).get()
            
            if existing_plan.exists:
                print(f"⚠️  Plan '{plan_id}' already exists, updating...")
                plans_collection.document(plan_id).update(plan)
                print(f"✅ Updated plan: {plan['name']}")
            else:
                plans_collection.document(plan_id).set(plan)
                print(f"✅ Added new plan: {plan['name']}")
        
        print("\n🎉 All plans have been successfully added/updated!")
        print("\nPlan Summary:")
        print("- Free: €0 (1 project, 3 milestones, 30 tasks)")
        print("- Premium: €4.99/month or €49.99/year (5 projects, 10 milestones, 100 tasks)")
        print("- Pro: €9.99/month or €99.99/year (15 projects, 30 milestones, 300 tasks)")
        print("- Unlimited: €34.99/month or €349.99/year (unlimited everything)")

if __name__ == '__main__':
    print("🔥 Phoenix Plan Setup")
    print("==================")
    print("Adding subscription plans to Firestore database...")
    print()
    
    try:
        add_plans()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
