#!/usr/bin/env python3
"""
Initialize Nigerian States and LGA data
"""
from app import create_app, db
from models.location import NigerianState, LocalGovernment
from data.nigeria_data import NIGERIAN_STATES, LOCAL_GOVERNMENTS

def init_nigeria_data():
    """Initialize Nigerian states and local government data"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create states
            print("Creating Nigerian states...")
            states_added = 0
            for state_data in NIGERIAN_STATES:
                existing_state = NigerianState.query.filter_by(name=state_data['name']).first()
                if not existing_state:
                    state = NigerianState(
                        name=state_data['name'],
                        code=state_data['code'],
                        capital=state_data['capital'],
                        zone=state_data['zone']
                    )
                    db.session.add(state)
                    states_added += 1
                    print(f"Added state: {state_data['name']}")
            
            db.session.commit()
            print(f"✅ {states_added} new states added")
            
            # Create local governments
            print("\nCreating Local Government Areas...")
            lgas_added = 0
            for state_name, lgas in LOCAL_GOVERNMENTS.items():
                state = NigerianState.query.filter_by(name=state_name).first()
                if state:
                    for lga_data in lgas:
                        existing_lga = LocalGovernment.query.filter_by(
                            name=lga_data['name'], 
                            state_id=state.id
                        ).first()
                        if not existing_lga:
                            lga = LocalGovernment(
                                name=lga_data['name'],
                                state_id=state.id,
                                headquarters=lga_data.get('headquarters', lga_data['name'])
                            )
                            db.session.add(lga)
                            lgas_added += 1
                            print(f"Added LGA: {lga_data['name']} ({state_name})")
            
            db.session.commit()
            print(f"✅ {lgas_added} new LGAs added")
            
            # Print summary
            states_count = NigerianState.query.count()
            lgas_count = LocalGovernment.query.count()
            
            print(f"\n✅ Nigeria data initialization completed!")
            print(f"📍 Total States: {states_count}")
            print(f"🏛️ Total Local Governments: {lgas_count}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error initializing Nigeria data: {str(e)}")
            raise e

if __name__ == "__main__":
    init_nigeria_data()