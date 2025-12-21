import requests
import sys
import json
from datetime import datetime

class AstroAPITester:
    def __init__(self, base_url="https://starry-path-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)

            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}

            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                if response_data:
                    print(f"Response preview: {str(response_data)[:200]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"Response: {response.text[:500]}...")

            self.test_results.append({
                "name": name,
                "success": success,
                "status_code": response.status_code,
                "expected_status": expected_status,
                "response_preview": str(response_data)[:200] if response_data else ""
            })

            return success, response_data

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                "name": name,
                "success": False,
                "error": str(e)
            })
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )

    def test_city_search_empty(self):
        """Test city search with empty query"""
        return self.run_test(
            "City Search - Empty Query",
            "POST",
            "search-city",
            200,
            data={"query": ""}
        )

    def test_city_search_short(self):
        """Test city search with short query"""
        return self.run_test(
            "City Search - Short Query",
            "POST",
            "search-city",
            200,
            data={"query": "M"}
        )

    def test_city_search_moscow(self):
        """Test city search for Moscow"""
        success, response = self.run_test(
            "City Search - Moscow",
            "POST",
            "search-city",
            200,
            data={"query": "Moscow"}
        )
        
        if success and isinstance(response, list) and len(response) > 0:
            print(f"Found {len(response)} cities")
            for i, city in enumerate(response[:2]):  # Show first 2 results
                print(f"  City {i+1}: {city.get('name', 'Unknown')} - Lat: {city.get('latitude')}, Lon: {city.get('longitude')}")
            return True, response
        return success, response

    def test_city_search_russian(self):
        """Test city search with Russian city name"""
        return self.run_test(
            "City Search - Russian City (Москва)",
            "POST",
            "search-city",
            200,
            data={"query": "Москва"}
        )

    def test_prediction_valid_data(self):
        """Test prediction with valid birth data"""
        success, response = self.run_test(
            "Astro Prediction - Valid Data",
            "POST",
            "get-prediction",
            200,
            data={
                "birthDate": "1990-05-15",
                "birthTime": "14:30",
                "latitude": 55.7558,
                "longitude": 37.6173,
                "timezone": 3
            },
            timeout=60  # Longer timeout for AI processing
        )
        
        if success and isinstance(response, dict):
            print(f"Prediction response structure:")
            print(f"  - Planets: {len(response.get('planets', []))} items")
            print(f"  - Vdasha periods: {len(response.get('vdasha', []))} items")
            print(f"  - Prediction length: {len(response.get('prediction', ''))} characters")
            
            # Check if we have actual data
            if response.get('planets') and len(response['planets']) > 0:
                print(f"  - First planet: {response['planets'][0].get('name', 'Unknown')}")
            if response.get('prediction'):
                print(f"  - Prediction preview: {response['prediction'][:100]}...")
                
        return success, response

    def test_prediction_invalid_date(self):
        """Test prediction with invalid date format"""
        return self.run_test(
            "Astro Prediction - Invalid Date",
            "POST",
            "get-prediction",
            422,  # Validation error expected
            data={
                "birthDate": "invalid-date",
                "birthTime": "14:30",
                "latitude": 55.7558,
                "longitude": 37.6173,
                "timezone": 3
            }
        )

    def test_prediction_missing_fields(self):
        """Test prediction with missing required fields"""
        return self.run_test(
            "Astro Prediction - Missing Fields",
            "POST",
            "get-prediction",
            422,  # Validation error expected
            data={
                "birthDate": "1990-05-15"
                # Missing other required fields
            }
        )

def main():
    print("🌟 Starting Astrology API Tests")
    print("=" * 50)
    
    tester = AstroAPITester()
    
    # Test basic connectivity
    print("\n📡 Testing Basic Connectivity...")
    tester.test_root_endpoint()
    
    # Test city search functionality
    print("\n🏙️ Testing City Search...")
    tester.test_city_search_empty()
    tester.test_city_search_short()
    moscow_success, moscow_data = tester.test_city_search_moscow()
    tester.test_city_search_russian()
    
    # Test prediction functionality
    print("\n🔮 Testing Astrology Predictions...")
    prediction_success, prediction_data = tester.test_prediction_valid_data()
    tester.test_prediction_invalid_date()
    tester.test_prediction_missing_fields()
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} passed")
    
    # Detailed analysis
    print("\n🔍 Detailed Analysis:")
    
    if moscow_success and moscow_data:
        print("✅ City search is working correctly")
    else:
        print("❌ City search has issues")
    
    if prediction_success and prediction_data:
        planets_count = len(prediction_data.get('planets', []))
        vdasha_count = len(prediction_data.get('vdasha', []))
        prediction_text = prediction_data.get('prediction', '')
        
        print(f"✅ Astrology prediction is working:")
        print(f"   - Planets data: {planets_count} planets")
        print(f"   - Vdasha periods: {vdasha_count} periods for 2026")
        print(f"   - GPT prediction: {'✅ Generated' if prediction_text else '❌ Missing'}")
        
        if not prediction_text:
            print("⚠️  Warning: GPT prediction is empty - check Emergent LLM key")
        if planets_count == 0:
            print("⚠️  Warning: No planets data - check Astrology API integration")
    else:
        print("❌ Astrology prediction has critical issues")
    
    # Save test results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"/app/test_reports/backend_test_results_{timestamp}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "total_tests": tester.tests_run,
            "passed_tests": tester.tests_passed,
            "success_rate": f"{(tester.tests_passed/tester.tests_run)*100:.1f}%",
            "test_details": tester.test_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())