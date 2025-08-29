#!/usr/bin/env python3
"""
Simple Trello Card Creator for SPCA Foster Animals
Just run this script and it will automatically process your AnimalInventory data for Hold - Foster animals
IMAGES ARE PRESERVED - all other info updates with latest data
CARDS ARE ARCHIVED when animals move out of Hold - Foster stage
"""

import os
import json
import time
import logging
from pathlib import Path
import pandas as pd
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleTrelloManager:
    """Simple Trello manager that preserves images but updates all other info and archives old cards"""
    
    def __init__(self):
        self.api_key = os.getenv('TRELLO_API_KEY')
        self.token = os.getenv('TRELLO_TOKEN')
        self.list_id = os.getenv('TRELLO_LIST_ID')
        self.archive_list_id = os.getenv('TRELLO_ARCHIVE_LIST_ID')
        
        if not all([self.api_key, self.token, self.list_id]):
            raise ValueError("Missing Trello credentials in .env file")
        
        if not self.archive_list_id:
            logger.warning("TRELLO_ARCHIVE_LIST_ID not set - archiving disabled")
        
        self.base_url = "https://api.trello.com/1"
        self.card_map_file = "foster_cards.json"
        self.card_map = self._load_card_map()
        
    def _load_card_map(self):
        """Load existing card mappings"""
        if os.path.exists(self.card_map_file):
            try:
                with open(self.card_map_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load card map: {e}")
        return {}
    
    def _save_card_map(self):
        """Save card mappings"""
        try:
            with open(self.card_map_file, 'w') as f:
                json.dump(self.card_map, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save card map: {e}")
    
    def _make_request(self, method: str, endpoint: str, **kwargs):
        """Make HTTP request to Trello API"""
        url = f"{self.base_url}/{endpoint}"
        params = {'key': self.api_key, 'token': self.token}
        
        try:
            response = requests.request(method, url, params=params, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            logger.error(f"Trello API request failed: {e}")
            return None
    
    def find_existing_card(self, animal_number: str):
        """Find existing card by animal number in either list"""
        if animal_number in self.card_map:
            return self.card_map[animal_number]
        
        # Search in both lists
        for list_id in [self.list_id, self.archive_list_id]:
            if not list_id:
                continue
            try:
                response = self._make_request('GET', f'lists/{list_id}/cards')
                if response:
                    for card in response:
                        if card['name'].startswith(f"{animal_number} "):
                            logger.info(f"Found existing card for {animal_number} in list {list_id}")
                            self.card_map[animal_number] = card['id']
                            self._save_card_map()
                            return card['id']
            except Exception as e:
                logger.warning(f"Could not search list {list_id} for card: {e}")
        
        return None
    
    def create_card(self, animal_number: str, animal_name: str, animal_type: str, primary_breed: str, age: str, sex: str, species: str, spayed_neutered: str, intake_date: str):
        """Create a new foster card"""
        name = f"{animal_number} - {animal_name}"
        description = f"""Animal: {animal_name}
Type: {animal_type}
Primary Breed: {primary_breed}
Age: {age}
Sex: {sex}
Species: {species}
Spayed/Neutered: {spayed_neutered}
Intake Date: {intake_date}

This animal is currently on hold for foster care."""
        
        data = {
            'idList': self.list_id,
            'name': name,
            'desc': description
        }
        
        response = self._make_request('POST', 'cards', json=data)
        if not response:
            raise Exception("Failed to create card")
        
        card_id = response['id']
        logger.info(f"Created new foster card: {name}")
        return card_id
    
    def update_card(self, card_id: str, animal_number: str, animal_name: str, animal_type: str, primary_breed: str, age: str, sex: str, species: str, spayed_neutered: str, intake_date: str):
        """Update existing foster card - always updates info, preserves attachments"""
        name = f"{animal_number} - {animal_name}"
        description = f"""Animal: {animal_name}
Type: {animal_type}
Primary Breed: {primary_breed}
Age: {age}
Sex: {sex}
Species: {species}
Spayed/Neutered: {spayed_neutered}
Intake Date: {intake_date}

This animal is currently on hold for foster care."""
        
        data = {
            'name': name,
            'desc': description
        }
        
        response = self._make_request('PUT', f'cards/{card_id}', json=data)
        if not response:
            raise Exception(f"Failed to update card {card_id}")
        
        logger.info(f"Updated foster card: {name}")
    
    def move_card_to_archive(self, card_id: str, animal_number: str, current_stage: str):
        """Move card to archive list when animal is no longer in Hold - Foster"""
        if not self.archive_list_id:
            logger.warning(f"Cannot archive card {card_id} - no archive list configured")
            return
        
        # Update description to show current stage
        description = f"""Animal Number: {animal_number}
Current Stage: {current_stage}

This animal is no longer in Hold - Foster stage.
Card archived for reference."""
        
        data = {
            'idList': self.archive_list_id,
            'desc': description
        }
        
        response = self._make_request('PUT', f'cards/{card_id}', json=data)
        if response:
            logger.info(f"Archived card for {animal_number} (Stage: {current_stage})")
        else:
            logger.error(f"Failed to archive card {card_id}")


def process_foster_data():
    """Process the foster data and create/update Trello cards"""
    try:
        # Load the CSV file, skipping the first 2 metadata rows
        # Row 1-2: Metadata, Row 3: Actual headers, Row 4+: Data
        df = pd.read_csv('../__Load Files Go Here__/AnimalInventory.csv', skiprows=2)
        
        logger.info(f"Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
        logger.info(f"Columns: {list(df.columns)}")
        
        # Filter for animals in "Hold - Foster" stage
        foster_df = df[df['Stage'] == 'Hold - Foster'].copy()
        
        logger.info(f"Found {len(foster_df)} animals in 'Hold - Foster' stage")
        
        if foster_df.empty:
            logger.info("No animals found in 'Hold - Foster' stage")
            return
        
        # Initialize Trello manager
        trello = SimpleTrelloManager()
        
        # Get all existing cards in the foster list
        existing_cards = {}
        try:
            response = requests.get(
                f"https://api.trello.com/1/lists/{trello.list_id}/cards",
                params={'key': trello.api_key, 'token': trello.token}
            )
            response.raise_for_status()
            cards = response.json()
            
            for card in cards:
                # Extract animal number from card name (format: "A0058955507 - GWENETH")
                if ' - ' in card['name']:
                    animal_number = card['name'].split(' - ')[0]
                    existing_cards[animal_number] = card['id']
                    
            logger.info(f"Found {len(existing_cards)} existing cards in foster list")
        except Exception as e:
            logger.error(f"Error getting existing cards: {e}")
            existing_cards = {}
        
        # Process each foster animal
        for index, row in foster_df.iterrows():
            try:
                animal_number = str(row['AnimalNumber'])
                animal_name = str(row['AnimalName']) if pd.notna(row['AnimalName']) else 'Unknown'
                animal_type = str(row['AnimalType']) if pd.notna(row['AnimalType']) else 'Unknown'
                primary_breed = str(row['PrimaryBreed']) if pd.notna(row['PrimaryBreed']) else 'Unknown'
                age = str(row['Age']) if pd.notna(row['Age']) else 'Unknown'
                sex = str(row['Sex']) if pd.notna(row['Sex']) else 'Unknown'
                species = str(row['Species']) if pd.notna(row['Species']) else 'Unknown'
                spayed_neutered = str(row['SpayedNeutered']) if pd.notna(row['SpayedNeutered']) else 'Unknown'
                intake_date = str(row['IntakeDateTime']) if pd.notna(row['IntakeDateTime']) else 'Unknown'
                
                # Find or create card
                card_id = trello.find_existing_card(animal_number)
                
                if card_id:
                    # Update existing card
                    logger.info(f"Updating card for {animal_name} ({animal_number})")
                    trello.update_card(card_id, animal_number, animal_name, animal_type, primary_breed, age, sex, species, spayed_neutered, intake_date)
                    
                    # Remove from existing cards list
                    if animal_number in existing_cards:
                        del existing_cards[animal_number]
                else:
                    # Create new card
                    logger.info(f"Creating new card for {animal_name} ({animal_number})")
                    card_id = trello.create_card(animal_number, animal_name, animal_type, primary_breed, age, sex, species, spayed_neutered, intake_date)
                    trello.card_map[animal_number] = card_id
                    
            except Exception as e:
                logger.error(f"Error processing animal {index}: {e}")
                continue
        
        # Archive cards for animals no longer in Hold - Foster
        if existing_cards and trello.archive_list_id:
            logger.info(f"Archiving {len(existing_cards)} cards no longer in Hold - Foster stage")
            
            for animal_number, card_id in existing_cards.items():
                try:
                    # Try to find current stage from CSV
                    current_stage = "Unknown"
                    animal_row = df[df['AnimalNumber'] == animal_number]
                    if not animal_row.empty:
                        current_stage = str(animal_row.iloc[0]['Stage']) if pd.notna(animal_row.iloc[0]['Stage']) else "Unknown"
                    
                    logger.info(f"Archiving card for {animal_number} (current stage: {current_stage})")
                    trello.move_card_to_archive(card_id, animal_number, current_stage)
                    
                except Exception as e:
                    logger.error(f"Error archiving card {card_id}: {e}")
                    continue
        
        # Save the updated card map
        trello._save_card_map()
        logger.info("Foster data processing completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to process CSV: {e}")
        raise


def main():
    """Main function - just run this!"""
    print("SPCA Foster Trello Card Creator with Archiving")
    print("=" * 50)
    print("Processing AnimalInventory.csv for animals with Stage = 'Hold - Foster'")
    print("IMAGES ARE PRESERVED - all other info updates with latest data")
    print("CARDS ARE ARCHIVED when animals move out of Hold - Foster stage")
    print()
    
    try:
        process_foster_data()
        print("\n✅ Done! Check your Trello board for the updated foster cards.")
        print("Note: Existing photos and attachments were preserved!")
        print("Old cards were moved to the archive list.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. Created a .env file with your Trello credentials")
        print("2. The 'AnimalInventory.csv' file in the '__Load Files Go Here__' folder")
        print("3. Animals with Stage = 'Hold - Foster' in your data")
        print("4. Set TRELLO_ARCHIVE_LIST_ID in your .env file for archiving")
        print("5. Installed requirements: pip install -r requirements.txt")


if __name__ == "__main__":
    main()
