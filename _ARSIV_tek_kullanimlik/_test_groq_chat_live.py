#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
D-195 Live chat test: Groq model zinciri validation.
Tests MIMIR sohbet widget with new Groq configuration.
"""

import subprocess
import time
import json
import sys

def run_browser_test():
    """Test chat widget via agent-browser automation."""
    
    # Wait for Streamlit server
    # TEK-ADRES-01: tek panel adresi 8501; 8502 ikizi kaldirildi.
    print("⏳ Waiting for Streamlit server (port 8501)...")
    time.sleep(2)
    
    # Create automation script
    automation = """
const { run } = require('agent-browser');

async function test() {
  // Open app
  await run('open http://localhost:8501');
  
  // Wait for login form
  await run('wait --selector "[data-testid=\\"stAppViewContainer\\"]" --timeout 10');
  
  // Screenshot: login page
  console.log('📸 Screenshot: Login page');
  await run('screenshot --path /tmp/01-login.png');
  
  // Fill admin email
  await run('type "@1" "admin@huginn.local"');
  
  // Fill password
  await run('type "@2" "test-password-123"');
  
  // Click login button
  await run('click "@3"');
  
  // Wait for dashboard
  console.log('⏳ Waiting for dashboard...');
  await run('wait --selector "[data-testid=\\"stAppViewContainer\\"]" --timeout 10');
  await run('wait 2');
  
  // Navigate to Abrakadabra tab (chat)
  console.log('🔄 Navigating to Abrakadabra tab...');
  await run('screenshot --path /tmp/02-dashboard.png');
  await run('click "a:has-text(\\"Abrakadabra\\")"');
  await run('wait 2');
  
  // Find chat input
  console.log('💬 Finding chat input...');
  await run('screenshot --path /tmp/03-chat-page.png');
  
  // Send test message
  const msg = "Merhaba, bunu Groq modeli ile mi işliyorsun?";
  await run(`type "[data-testid=\\"stChatInput\\"]" "${msg}"`);
  await run('press Enter');
  
  // Wait for response
  console.log('⏳ Waiting for AI response...');
  await run('wait 10');
  
  // Screenshot: response with model info
  console.log('📸 Screenshot: Response');
  await run('screenshot --path /tmp/04-response.png');
  
  // Extract model name from response
  const html = await run('get-html');
  console.log('✅ Chat response received');
  
  // Check for Groq model mention
  if (html.includes('groq/llama-3.3-70b-versatile') || 
      html.includes('groq/mixtral-8x7b-32768') ||
      html.includes('groq/gemma-7b-it')) {
    console.log('✅ PASS: Groq model detected in response');
    process.exit(0);
  } else {
    console.log('❌ FAIL: No Groq model detected');
    console.log('Response HTML snippet:', html.substring(0, 500));
    process.exit(1);
  }
}

test().catch(err => {
  console.error('❌ Test failed:', err);
  process.exit(2);
});
"""
    
    with open('/tmp/test-chat.js', 'w') as f:
        f.write(automation)
    
    print("🚀 Running browser automation...")
    result = subprocess.run(
        ['node', '/tmp/test-chat.js'],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    print("STDOUT:")
    print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    return result.returncode == 0

if __name__ == '__main__':
    try:
        success = run_browser_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(2)
