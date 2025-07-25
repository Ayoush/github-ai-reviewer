#!/usr/bin/env python3
"""
Dummy Python file with intentional issues for testing AI code review
"""

import os
import sys

# Issue 1: Unused import
import json
import requests

# Issue 2: Global variable (bad practice)
GLOBAL_DATA = []

# Issue 3: Function with too many parameters and no type hints
def process_user_data(name, email, age, address, phone, city, state, zip_code, country):
    # Issue 4: No input validation
    user_data = {
        'name': name,
        'email': email,
        'age': age,
        'address': address,
        'phone': phone,
        'city': city,
        'state': state,
        'zip': zip_code,
        'country': country
    }
    
    # Issue 5: Direct database query without parameterization (SQL injection risk)
    query = f"INSERT INTO users (name, email) VALUES ('{name}', '{email}')"
    
    # Issue 6: Hardcoded credentials
    api_key = "sk-1234567890abcdef"
    
    # Issue 7: No error handling
    response = requests.get(f"https://api.example.com/users?key={api_key}")
    data = response.json()
    
    # Issue 8: Modifying global state
    GLOBAL_DATA.append(user_data)
    
    return user_data

# Issue 9: Function with no docstring and poor naming
def calc(x, y):
    # Issue 10: Division by zero not handled
    result = x / y
    return result

# Issue 11: Class with no proper initialization
class UserManager:
    def add_user(self, user):
        # Issue 12: No validation of input
        self.users.append(user)
    
    def get_user(self, user_id):
        # Issue 13: Inefficient search
        for user in self.users:
            if user['id'] == user_id:
                return user
        return None

# Issue 14: Main execution without proper guard
if __name__ == "__main__":
    # Issue 15: No command line argument validation
    username = sys.argv[1]
    email = sys.argv[2]
    
    # Issue 16: Magic numbers
    user_data = process_user_data(username, email, 25, "123 Main St", "555-1234", 
                                "Anytown", "CA", "12345", "USA")
    
    # Issue 17: Print instead of proper logging
    print(f"User created: {user_data}")
    
    # Issue 18: Potential memory leak with large data
    for i in range(10000):
        GLOBAL_DATA.append(f"dummy_data_{i}")
