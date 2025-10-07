#!/usr/bin/env python3
"""
Test script to verify suRxit backend API functionality
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def test_backend():
    """Test basic backend functionality"""
    
    print("🧪 Testing suRxit Backend Components")
    print("=" * 40)
    
    try:
        # Test 1: Import core modules
        print("1. Testing module imports...")
        from auth import AuthManager
        from ai_service import MedLMService
        from models import PrescriptionAnalysis, ChatMessage
        print("   ✅ All modules imported successfully")
        
        # Test 2: Test authentication
        print("\n2. Testing authentication...")
        auth_manager = AuthManager()
        
        # Test user creation
        user = await auth_manager.create_user(
            email="test@example.com",
            password="testpass123",
            name="Test User",
            role="doctor"
        )
        print(f"   ✅ User created: {user['name']}")
        
        # Test login
        auth_result = await auth_manager.authenticate_user("test@example.com", "testpass123")
        token = auth_result["token"]
        print(f"   ✅ Authentication successful")
        
        # Test token verification
        verified_user = await auth_manager.verify_token(token)
        print(f"   ✅ Token verification successful: {verified_user['email']}")
        
        # Test 3: Test AI service
        print("\n3. Testing AI service...")
        ai_service = MedLMService()
        
        # Test prescription analysis
        analysis = await ai_service.analyze_prescription(
            "Lisinopril 10mg daily and Metformin 500mg twice daily",
            patient_data={"allergies": ["Penicillin"], "age": 45}
        )
        print(f"   ✅ Prescription analysis completed")
        print(f"   📊 Found {len(analysis['drug_interactions'])} drug interactions")
        print(f"   ⚠️ Found {len(analysis['alerts'])} safety alerts")
        
        # Test chat response
        chat_response = await ai_service.get_chat_response(
            "What are the side effects of Lisinopril?",
            context=[],
            user_role="doctor"
        )
        print(f"   ✅ Chat response generated")
        print(f"   💬 Response: {chat_response['content'][:100]}...")
        
        # Test 4: Test data models
        print("\n4. Testing data models...")
        
        from models import DrugInteraction, RiskLevel, SeverityLevel
        
        interaction = DrugInteraction(
            drug1="Warfarin",
            drug2="Aspirin", 
            severity=SeverityLevel.HIGH,
            mechanism="Additive anticoagulant effects",
            clinical_effects="Increased bleeding risk",
            management="Monitor INR closely"
        )
        print(f"   ✅ Drug interaction model created: {interaction.drug1} + {interaction.drug2}")
        
        print("\n🎉 All tests passed! Backend is ready to use.")
        print("\nNext steps:")
        print("1. Run: python main.py (or ./start.sh)")
        print("2. Visit: http://localhost:8000/docs")
        print("3. Test login with: doctor@example.com / password")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure you're in the backend directory")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Check that all files are present")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_backend())
    sys.exit(0 if result else 1)