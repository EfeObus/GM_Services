#!/usr/bin/env python3
"""
Simple Nigerian States and LGA data initialization for PostgreSQL
"""
import psycopg2
import os
from data.nigeria_data import NIGERIAN_STATES, LOCAL_GOVERNMENTS

def init_nigeria_data_simple():
    """Initialize Nigerian states and local government data using PostgreSQL"""
    
    # Get database URL from environment
    db_url = os.environ.get('SQLALCHEMY_DATABASE_URI', 'postgresql://efeobukohwo@localhost:5432/GM_Services')
    print(f"Connecting to PostgreSQL database: {db_url}")
    
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'nigerian_states')")
        if not cursor.fetchone()[0]:
            print("❌ nigerian_states table not found")
            return
            
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'local_governments')")
        if not cursor.fetchone()[0]:
            print("❌ local_governments table not found")
            return
        
        print("✅ Required tables found")
        
        # Create states
        print("Creating Nigerian states...")
        states_added = 0
        for state_data in NIGERIAN_STATES:
            # Check if state already exists
            cursor.execute("SELECT id FROM nigerian_states WHERE name = %s", (state_data['name'],))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO nigerian_states (name, code, capital, zone, created_at) VALUES (%s, %s, %s, %s, NOW())",
                    (state_data['name'], state_data['code'], state_data['capital'], state_data['zone'])
                )
                states_added += 1
                print(f"Added state: {state_data['name']}")
        
        print(f"✅ {states_added} new states added")
        
        # Create local governments
        print("\nCreating Local Government Areas...")
        lgas_added = 0
        for state_name, lgas in LOCAL_GOVERNMENTS.items():
            # Get state ID
            cursor.execute("SELECT id FROM nigerian_states WHERE name = %s", (state_name,))
            state_row = cursor.fetchone()
            
            if state_row:
                state_id = state_row[0]
                for lga_data in lgas:
                    # Check if LGA already exists
                    cursor.execute(
                        "SELECT id FROM local_governments WHERE name = %s AND state_id = %s", 
                        (lga_data['name'], state_id)
                    )
                    if not cursor.fetchone():
                        headquarters = lga_data.get('headquarters', lga_data['name'])
                        cursor.execute(
                            "INSERT INTO local_governments (name, state_id, headquarters, created_at) VALUES (%s, %s, %s, NOW())",
                            (lga_data['name'], state_id, headquarters)
                        )
                        lgas_added += 1
                        print(f"Added LGA: {lga_data['name']} ({state_name})")
        
        # Commit changes
        conn.commit()
        print(f"✅ {lgas_added} new LGAs added")
        
        # Print summary
        cursor.execute("SELECT COUNT(*) FROM nigerian_states")
        states_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM local_governments")
        lgas_count = cursor.fetchone()[0]
        
        print(f"\n✅ Nigeria data initialization completed!")
        print(f"📍 Total States: {states_count}")
        print(f"🏛️ Total Local Governments: {lgas_count}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error initializing Nigeria data: {str(e)}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    init_nigeria_data_simple()