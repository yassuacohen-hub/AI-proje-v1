#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Simple benchmark runner for webhook and MCP load testing using Locust.
Usage:
    python scripts/benchmark_webhook_load.py --webhook-url http://localhost:8000 --mcp-url http://localhost:8000 --duration 2m --users 10 --spawn-rate 2
'''

import argparse
import subprocess
import sys
import os
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Run Locust load test for webhook and MCP endpoints')
    parser.add_argument('--webhook-url', required=True, help='Base URL for webhook endpoint (e.g., http://localhost:8000)')
    parser.add_argument('--mcp-url', required=True, help='Base URL for MCP endpoint (e.g., http://localhost:8000)')
    parser.add_argument('--duration', default='2m', help='Test duration (e.g., 1m, 2m, 30s)')
    parser.add_argument('--users', type=int, default=10, help='Number of concurrent users')
    parser.add_argument('--spawn-rate', type=int, default=2, help='Users spawned per second')
    parser.add_argument('--host', default='http://localhost:8000', help='Host for Locust (if different)')
    parser.add_argument('--output', default='benchmark_results.html', help='Output file for HTML report')
    args = parser.parse_args()

    # Set environment variables for the locustfile
    os.environ['TARGET_HOST'] = args.webhook_url
    os.environ['MCP_HOST'] = args.mcp_url
    os.environ['WEBHOOK_SECRET'] = 'test-secret'  # In real use, should be from secure source

    # Build locust command
    locust_cmd = [
        sys.executable, '-m', 'locust',
        '-f', str(Path(__file__).parent.parent / 'locustfile.py'),
        '--headless',
        '--run-time', args.duration,
        '--users', str(args.users),
        '--spawn-rate', str(args.spawn-rate),
        '--host', args.host,
        '--html', args.output,
        '--csv', 'benchmark_result'
    ]

    print('Running locust command: ' + ' '.join(locust_cmd))
    try:
        subprocess.run(locust_cmd, check=True)
        print('Benchmark completed. Results saved to ' + args.output + ' and benchmark_result.csv')
    except subprocess.CalledProcessError as e:
        print('Locust failed with exit code ' + str(e.returncode))
        sys.exit(e.returncode)

if __name__ == '__main__':
    main
