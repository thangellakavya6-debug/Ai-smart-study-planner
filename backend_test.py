#!/usr/bin/env python3
"""
Backend API Testing for AI-Powered Study Planner
Tests all backend endpoints with proper authentication flow
"""

import requests
import json
import sys
from datetime import datetime

# Base URL from review request
BASE_URL = "https://a941a297-a8fb-408b-ba38-123bd5ecc882.preview.emergentagent.com"
API_BASE = f"{BASE_URL}/api"

class StudyPlannerAPITester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.session_id = "test-session-123"
        self.test_results = []
        
    def log_result(self, test_name, success, message, response_data=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "response_data": response_data
        })
        
    def make_request(self, method, endpoint, data=None, headers=None):
        """Make HTTP request with error handling"""
        url = f"{API_BASE}{endpoint}"
        default_headers = {"Content-Type": "application/json"}
        
        if headers:
            default_headers.update(headers)
            
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=default_headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=default_headers, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=default_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
            
    def get_auth_headers(self):
        """Get authorization headers with token"""
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}
        
    def test_auth_register(self):
        """Test user registration"""
        print("\n=== Testing User Registration ===")
        
        data = {
            "name": "Alex Johnson",
            "email": "alex.johnson@studyai.com", 
            "password": "securepass123"
        }
        
        response = self.make_request("POST", "/auth/register", data)
        
        if not response:
            self.log_result("Auth Register", False, "Request failed - no response")
            return False
            
        if response.status_code == 200:
            try:
                result = response.json()
                if "token" in result and "user" in result:
                    self.token = result["token"]
                    self.user_id = result["user"]["id"]
                    self.log_result("Auth Register", True, f"User registered successfully. ID: {self.user_id}")
                    return True
                else:
                    self.log_result("Auth Register", False, f"Missing token or user in response: {result}")
                    return False
            except json.JSONDecodeError:
                self.log_result("Auth Register", False, f"Invalid JSON response: {response.text}")
                return False
        else:
            self.log_result("Auth Register", False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    def test_auth_login(self):
        """Test user login"""
        print("\n=== Testing User Login ===")
        
        data = {
            "email": "alex.johnson@studyai.com",
            "password": "securepass123"
        }
        
        response = self.make_request("POST", "/auth/login", data)
        
        if not response:
            self.log_result("Auth Login", False, "Request failed - no response")
            return False
            
        if response.status_code == 200:
            try:
                result = response.json()
                if "token" in result and "user" in result:
                    self.token = result["token"]  # Update token
                    self.log_result("Auth Login", True, f"Login successful. User: {result['user']['name']}")
                    return True
                else:
                    self.log_result("Auth Login", False, f"Missing token or user in response: {result}")
                    return False
            except json.JSONDecodeError:
                self.log_result("Auth Login", False, f"Invalid JSON response: {response.text}")
                return False
        else:
            self.log_result("Auth Login", False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    def test_timetable_generate(self):
        """Test timetable generation"""
        print("\n=== Testing Timetable Generation ===")
        
        data = {
            "subjects": ["Mathematics", "Physics", "Chemistry", "Biology"],
            "strongSubjects": ["Mathematics", "Biology"],
            "weakSubjects": ["Physics", "Chemistry"],
            "hoursPerDay": 5,
            "startTime": "05:00"
        }
        
        headers = self.get_auth_headers()
        response = self.make_request("POST", "/timetable/generate", data, headers)
        
        if not response:
            self.log_result("Timetable Generate", False, "Request failed - no response")
            return False
            
        if response.status_code == 200:
            try:
                result = response.json()
                if "schedule" in result and isinstance(result["schedule"], list):
                    schedule = result["schedule"]
                    if len(schedule) > 0:
                        # Verify schedule structure
                        first_slot = schedule[0]
                        required_fields = ["subject", "startTime", "endTime", "duration", "type"]
                        if all(field in first_slot for field in required_fields):
                            self.log_result("Timetable Generate", True, f"Timetable generated with {len(schedule)} slots")
                            return True
                        else:
                            self.log_result("Timetable Generate", False, f"Schedule missing required fields: {first_slot}")
                            return False
                    else:
                        self.log_result("Timetable Generate", False, "Empty schedule generated")
                        return False
                else:
                    self.log_result("Timetable Generate", False, f"Invalid response structure: {result}")
                    return False
            except json.JSONDecodeError:
                self.log_result("Timetable Generate", False, f"Invalid JSON response: {response.text}")
                return False
        else:
            self.log_result("Timetable Generate", False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    def test_timetable_get(self):
        """Test getting saved timetable"""
        print("\n=== Testing Get Timetable ===")
        
        headers = self.get_auth_headers()
        response = self.make_request("GET", "/timetable", headers=headers)
        
        if not response:
            self.log_result("Timetable Get", False, "Request failed - no response")
            return False
            
        if response.status_code == 200:
            try:
                result = response.json()
                if result and "schedule" in result:
                    self.log_result("Timetable Get", True, f"Retrieved timetable with {len(result['schedule'])} slots")
                    return True
                elif result is None:
                    self.log_result("Timetable Get", True, "No timetable found (null response)")
                    return True
                else:
                    self.log_result("Timetable Get", False, f"Invalid timetable structure: {result}")
                    return False
            except json.JSONDecodeError:
                self.log_result("Timetable Get", False, f"Invalid JSON response: {response.text}")
                return False
        else:
            self.log_result("Timetable Get", False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    def test_study_log_create(self):
        """Test creating study log"""
        print("\n=== Testing Study Log Creation ===")
        
        data = {
            "subject": "Mathematics",
            "duration": 45
        }
        
        headers = self.get_auth_headers()
        response = self.make_request("POST", "/study-logs", data, headers)
        
        if not response:
            self.log_result("Study Log Create", False, "Request failed - no response")
            return False
            
        if response.status_code == 200:
            try:
                result = response.json()
                if "id" in result and "subject" in result and "duration" in result:
                    self.log_result("Study Log Create", True, f"Study log created: {result['subject']} - {result['duration']} mins")
                    return True
                else:
                    self.log_result("Study Log Create", False, f"Invalid response structure: {result}")
                    return False
            except json.JSONDecodeError:
                self.log_result("Study Log Create", False, f"Invalid JSON response: {response.text}")
                return False
        else:
            self.log_result("Study Log Create", False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    def test_study_logs_get(self):
        """Test getting study logs"""
        print("\n=== Testing Get Study Logs ===")
        
        headers = self.get_auth_headers()
        response = self.make_request("GET", "/study-logs?period=weekly", headers=headers)
        
        if not response:
            self.log_result("Study Logs Get", False, "Request failed - no response")
            return False
            
        if response.status_code == 200:
            try:
                result = response.json()
                if isinstance(result, list):
                    self.log_result("Study Logs Get", True, f"Retrieved {len(result)} study logs")
                    return True
                else:
                    self.log_result("Study Logs Get", False, f"Expected array, got: {type(result)}")
                    return False
            except json.JSONDecodeError:
                self.log_result("Study Logs Get", False, f"Invalid JSON response: {response.text}")
                return False
        else:
            self.log_result("Study Logs Get", False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    def test_goals_set(self):
        """Test setting daily goal"""
        print("\n=== Testing Set Goals ===")
        
        data = {
            "dailyGoalHours": 5
        }
        
        headers = self.get_auth_headers()
        response = self.make_request("POST", "/goals", data, headers)
        
        if not response:
            self.log_result("Goals Set", False, "Request failed - no response")
            return False
            
        if response.status_code == 200:
            try:
                result = response.json()
                if "dailyGoalHours" in result:
                    self.log_result("Goals Set", True, f"Goal set: {result['dailyGoalHours']} hours/day")
                    return True
                else:
                    self.log_result("Goals Set", False, f"Invalid response structure: {result}")
                    return False
            except json.JSONDecodeError:
                self.log_result("Goals Set", False, f"Invalid JSON response: {response.text}")
                return False
        else:
            self.log_result("Goals Set", False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    def test_goals_get(self):
        """Test getting current goal"""
        print("\n=== Testing Get Goals ===")
        
        headers = self.get_auth_headers()
        response = self.make_request("GET", "/goals", headers=headers)
        
        if not response:
            self.log_result("Goals Get", False, "Request failed - no response")
            return False
            
        if response.status_code == 200:
            try:
                result = response.json()
                if "completedMinutes" in result:
                    completed = result.get("completedMinutes", 0)
                    goal_hours = result.get("dailyGoalHours", "N/A")
                    self.log_result("Goals Get", True, f"Today's progress: {completed} mins completed, goal: {goal_hours} hours")
                    return True
                else:
                    self.log_result("Goals Get", False, f"Invalid response structure: {result}")
                    return False
            except json.JSONDecodeError:
                self.log_result("Goals Get", False, f"Invalid JSON response: {response.text}")
                return False
        else:
            self.log_result("Goals Get", False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    def test_goals_history(self):
        """Test getting goal history"""
        print("\n=== Testing Goals History ===")
        
        headers = self.get_auth_headers()
        response = self.make_request("GET", "/goals/history", headers=headers)
        
        if not response:
            self.log_result("Goals History", False, "Request failed - no response")
            return False
            
        if response.status_code == 200:
            try:
                result = response.json()
                if isinstance(result, list):
                    self.log_result("Goals History", True, f"Retrieved {len(result)} days of goal history")
                    return True
                else:
                    self.log_result("Goals History", False, f"Expected array, got: {type(result)}")
                    return False
            except json.JSONDecodeError:
                self.log_result("Goals History", False, f"Invalid JSON response: {response.text}")
                return False
        else:
            self.log_result("Goals History", False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    def test_ai_chat(self):
        """Test AI chat functionality"""
        print("\n=== Testing AI Chat ===")
        
        data = {
            "message": "What is photosynthesis?",
            "sessionId": self.session_id
        }
        
        headers = self.get_auth_headers()
        response = self.make_request("POST", "/chat", data, headers)
        
        if not response:
            self.log_result("AI Chat", False, "Request failed - no response")
            return False
            
        if response.status_code == 200:
            try:
                result = response.json()
                if "response" in result and "sessionId" in result:
                    ai_response = result["response"]
                    if ai_response and len(ai_response) > 10:  # Basic check for meaningful response
                        self.log_result("AI Chat", True, f"AI responded with {len(ai_response)} characters")
                        return True
                    else:
                        self.log_result("AI Chat", False, f"AI response too short or empty: {ai_response}")
                        return False
                else:
                    self.log_result("AI Chat", False, f"Invalid response structure: {result}")
                    return False
            except json.JSONDecodeError:
                self.log_result("AI Chat", False, f"Invalid JSON response: {response.text}")
                return False
        else:
            self.log_result("AI Chat", False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    def test_chat_history(self):
        """Test getting chat history"""
        print("\n=== Testing Chat History ===")
        
        headers = self.get_auth_headers()
        response = self.make_request("GET", f"/chat/history?sessionId={self.session_id}", headers=headers)
        
        if not response:
            self.log_result("Chat History", False, "Request failed - no response")
            return False
            
        if response.status_code == 200:
            try:
                result = response.json()
                if "messages" in result and isinstance(result["messages"], list):
                    messages = result["messages"]
                    self.log_result("Chat History", True, f"Retrieved {len(messages)} chat messages")
                    return True
                else:
                    self.log_result("Chat History", False, f"Invalid response structure: {result}")
                    return False
            except json.JSONDecodeError:
                self.log_result("Chat History", False, f"Invalid JSON response: {response.text}")
                return False
        else:
            self.log_result("Chat History", False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    def test_calendar_export(self):
        """Test calendar export functionality"""
        print("\n=== Testing Calendar Export ===")
        
        headers = self.get_auth_headers()
        response = self.make_request("GET", "/calendar/export", headers=headers)
        
        if not response:
            self.log_result("Calendar Export", False, "Request failed - no response")
            return False
            
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'text/calendar' in content_type:
                ics_content = response.text
                if 'BEGIN:VCALENDAR' in ics_content and 'END:VCALENDAR' in ics_content:
                    self.log_result("Calendar Export", True, f"ICS file generated ({len(ics_content)} chars)")
                    return True
                else:
                    self.log_result("Calendar Export", False, f"Invalid ICS format: {ics_content[:100]}...")
                    return False
            else:
                self.log_result("Calendar Export", False, f"Wrong content type: {content_type}")
                return False
        elif response.status_code == 404:
            self.log_result("Calendar Export", False, "No timetable found for export")
            return False
        else:
            self.log_result("Calendar Export", False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    def run_all_tests(self):
        """Run all backend API tests in sequence"""
        print(f"🚀 Starting Backend API Tests for: {BASE_URL}")
        print(f"📡 API Base URL: {API_BASE}")
        
        # Test sequence - order matters for authentication flow
        tests = [
            self.test_auth_register,
            self.test_auth_login,
            self.test_timetable_generate,
            self.test_timetable_get,
            self.test_study_log_create,
            self.test_study_logs_get,
            self.test_goals_set,
            self.test_goals_get,
            self.test_goals_history,
            self.test_ai_chat,
            self.test_chat_history,
            self.test_calendar_export
        ]
        
        for test_func in tests:
            try:
                test_func()
            except Exception as e:
                test_name = test_func.__name__.replace('test_', '').replace('_', ' ').title()
                self.log_result(test_name, False, f"Test crashed: {str(e)}")
                
        # Summary
        print("\n" + "="*60)
        print("📊 BACKEND API TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if total - passed > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  ❌ {result['test']}: {result['message']}")
                    
        print(f"\n🎯 Success Rate: {(passed/total)*100:.1f}%")
        
        return passed == total

if __name__ == "__main__":
    tester = StudyPlannerAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)