#!/usr/bin/env python3
"""
User Behavior Data Generator

This script generates simulated user behavior data and writes it to a file
that will be picked up by the InLong Agent.
"""
import json
import time
import random
import os
from datetime import datetime
from faker import Faker

# Initialize Faker
fake = Faker()

# Ensure data directory exists
os.makedirs('/data', exist_ok=True)

# Define possible user actions
ACTIONS = ['view', 'click', 'scroll', 'purchase', 'add_to_cart', 'remove_from_cart', 'search']
CATEGORIES = ['electronics', 'clothing', 'food', 'books', 'toys', 'home', 'beauty']
PLATFORMS = ['web', 'mobile_app', 'tablet']

def generate_user_behavior():
    """Generate a single user behavior event"""
    return {
        'user_id': fake.uuid4(),
        'session_id': fake.uuid4(),
        'timestamp': datetime.now().isoformat(),
        'action': random.choice(ACTIONS),
        'category': random.choice(CATEGORIES),
        'product_id': fake.bothify(text='product-#####'),
        'platform': random.choice(PLATFORMS),
        'device_info': {
            'os': random.choice(['iOS', 'Android', 'Windows', 'macOS', 'Linux']),
            'browser': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge', None]),
            'version': fake.numerify(text='##.#.#'),
        },
        'location': {
            'country': fake.country(),
            'city': fake.city(),
            'ip': fake.ipv4()
        },
        'referrer': random.choice([fake.uri(), None]),
        'time_spent': random.randint(5, 300) if random.random() > 0.3 else None,
    }

def main():
    """Main function to continuously generate user behavior data"""
    print("Starting User Behavior Data Generator...")
    
    counter = 0
    batch_size = 100
    
    while True:
        # Generate a batch of user behavior events
        events = [generate_user_behavior() for _ in range(batch_size)]
        
        # Write to file with timestamp in filename to ensure uniqueness
        timestamp = int(time.time())
        filename = f'/data/user_behavior_{timestamp}_{counter}.json'
        
        with open(filename, 'w') as f:
            json.dump(events, f, indent=2)
        
        print(f"Generated {batch_size} events, saved to {filename}")
        
        counter += 1
        # Sleep for a random interval between 1-5 seconds
        time.sleep(random.uniform(1, 5))

if __name__ == '__main__':
    main()
