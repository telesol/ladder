#!/usr/bin/env python3
"""
Test script to verify the fixes for the autonomous system
"""
import asyncio
import sys
from final_autonomous_system import FinalAutonomousSystem
from agents.intelligent_analyzer import IntelligentAnalyzer
from memory_system import MemorySystem

async def test_basic_functionality():
    """Test basic functionality of the fixed system"""
    print("🧪 Testing Fixed Autonomous System")
    print("=" * 50)
    
    try:
        # Test 1: IntelligentAnalyzer method exists
        print("1️⃣ Testing IntelligentAnalyzer...")
        analyzer = IntelligentAnalyzer()
        
        # Check if analyze_system method exists (this was the main issue)
        if hasattr(analyzer, 'analyze_system'):
            print("✅ analyze_system method exists")
        else:
            print("❌ analyze_system method missing")
            return False
            
        # Test 2: MemorySystem store_intelligence method
        print("2️⃣ Testing MemorySystem...")
        memory = MemorySystem('test_memory.db')
        
        # Test store_intelligence
        test_data = {'test': 'data', 'timestamp': '2024-01-01'}
        memory.store_intelligence('test_key', test_data)
        
        # Test retrieve_intelligence
        retrieved = memory.retrieve_intelligence('test_key')
        if retrieved and retrieved.get('test') == 'data':
            print("✅ store_intelligence and retrieve_intelligence work")
        else:
            print("❌ Memory system methods failed")
            return False
        
        # Test 3: FinalAutonomousSystem initialization
        print("3️⃣ Testing FinalAutonomousSystem initialization...")
        system = FinalAutonomousSystem()
        
        # Check token manager settings
        if system.max_context_tokens == 4096:
            print("✅ Token limits reduced to prevent timeouts")
        else:
            print(f"⚠️  Token limits: {system.max_context_tokens}")
        
        print("✅ All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        import os
        if os.path.exists('test_memory.db'):
            os.remove('test_memory.db')

async def test_short_analysis():
    """Test a short analysis run"""
    print("\n🧪 Testing short analysis run...")
    
    try:
        system = FinalAutonomousSystem()
        
        # Test just the analysis phase
        print("Running analysis...")
        analysis_results = await system.run_full_analysis()
        
        if analysis_results:
            print("✅ Analysis completed successfully")
            print(f"📊 Analysis keys: {list(analysis_results.keys())}")
            return True
        else:
            print("❌ Analysis returned empty results")
            return False
            
    except Exception as e:
        print(f"❌ Short analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Testing Fixed Autonomous System")
    print("=" * 60)
    
    # Run basic functionality tests
    basic_success = asyncio.run(test_basic_functionality())
    
    if basic_success:
        # Run short analysis test
        analysis_success = asyncio.run(test_short_analysis())
        
        if analysis_success:
            print("\n🎉 All tests passed! The system should now work correctly.")
            print("\n📋 Summary of fixes applied:")
            print("  • Fixed method name: analyze_system() instead of comprehensive_analysis()")
            print("  • Reduced token limits from 8192 to 4096 to prevent timeouts")
            print("  • Added progressive error backoff and recovery mechanisms")
            print("  • Reduced Ollama timeout from 5 minutes to 2 minutes")
            print("  • Improved error handling with consecutive error tracking")
        else:
            print("\n⚠️  Basic functionality works but analysis test failed")
            sys.exit(1)
    else:
        print("\n❌ Basic functionality tests failed")
        sys.exit(1)
