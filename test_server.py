#!/usr/bin/env python3
"""
Tests for GitHub AI Code Reviewer
"""

import unittest
import json
import hmac
import hashlib
from unittest.mock import patch, MagicMock
import os
import sys

# Add the current directory to the path so we can import our server
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import app, verify_signature, should_review_file

class TestGitHubAIReviewer(unittest.TestCase):
    
    def setUp(self):
        """Set up test client."""
        self.app = app.test_client()
        self.app.testing = True
        
        # Set test environment variables
        os.environ['WEBHOOK_SECRET'] = 'test_secret'
        os.environ['GITHUB_APP_ID'] = '12345'
        os.environ['GEMINI_API_KEY'] = 'test_key'
    
    def test_home_endpoint(self):
        """Test the home endpoint."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AI Code Reviewer is running', response.data)
    
    def test_health_endpoint(self):
        """Test the health endpoint."""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_verify_signature_valid(self):
        """Test signature verification with valid signature."""
        payload = b'{"test": "data"}'
        secret = 'test_secret'
        signature = 'sha256=' + hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        os.environ['WEBHOOK_SECRET'] = secret
        self.assertTrue(verify_signature(payload, signature))
    
    def test_verify_signature_invalid(self):
        """Test signature verification with invalid signature."""
        payload = b'{"test": "data"}'
        invalid_signature = 'sha256=invalid'
        
        os.environ['WEBHOOK_SECRET'] = 'test_secret'
        self.assertFalse(verify_signature(payload, invalid_signature))
    
    def test_should_review_file(self):
        """Test file extension filtering."""
        # Should review these files
        self.assertTrue(should_review_file('test.py'))
        self.assertTrue(should_review_file('app.js'))
        self.assertTrue(should_review_file('component.tsx'))
        self.assertTrue(should_review_file('main.go'))
        
        # Should not review these files
        self.assertFalse(should_review_file('README.md'))
        self.assertFalse(should_review_file('config.json'))
        self.assertFalse(should_review_file('image.png'))
        self.assertFalse(should_review_file('.gitignore'))
    
    def test_webhook_invalid_signature(self):
        """Test webhook with invalid signature."""
        payload = {'action': 'opened'}
        response = self.app.post(
            '/webhook',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'X-Hub-Signature-256': 'invalid'}
        )
        self.assertEqual(response.status_code, 401)
    
    def test_webhook_ignored_event(self):
        """Test webhook with ignored event type."""
        payload = {'action': 'opened'}
        payload_str = json.dumps(payload)
        signature = 'sha256=' + hmac.new(
            'test_secret'.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        response = self.app.post(
            '/webhook',
            data=payload_str,
            content_type='application/json',
            headers={
                'X-Hub-Signature-256': signature,
                'X-GitHub-Event': 'issues'
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Event ignored')
    
    def create_valid_webhook_payload(self, action='opened'):
        """Create a valid webhook payload for testing."""
        payload = {
            'action': action,
            'pull_request': {
                'number': 1,
                'head': {'sha': 'abc123'}
            },
            'repository': {
                'full_name': 'test/repo',
                'owner': {'login': 'test'},
                'name': 'repo'
            },
            'installation': {'id': 12345}
        }
        return payload
    
    @patch('server.get_github_client')
    @patch('server.review_with_gemini')
    def test_webhook_pull_request_opened(self, mock_review, mock_github):
        """Test webhook handling for opened pull request."""
        # Mock GitHub client and responses
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        mock_file = MagicMock()
        mock_file.filename = 'test.py'
        mock_content = MagicMock()
        mock_content.decoded_content = b'print("hello world")'
        
        mock_github.return_value.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pr
        mock_pr.get_files.return_value = [mock_file]
        mock_repo.get_contents.return_value = mock_content
        mock_review.return_value = 'CODE LOOKS GOOD: Nice simple code!'
        
        # Create valid payload
        payload = self.create_valid_webhook_payload()
        payload_str = json.dumps(payload)
        signature = 'sha256=' + hmac.new(
            'test_secret'.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        response = self.app.post(
            '/webhook',
            data=payload_str,
            content_type='application/json',
            headers={
                'X-Hub-Signature-256': signature,
                'X-GitHub-Event': 'pull_request'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Success')

if __name__ == '__main__':
    # Create a simple test runner
    print("🧪 Running GitHub AI Code Reviewer Tests")
    print("=" * 40)
    
    # Run the tests
    unittest.main(verbosity=2)
