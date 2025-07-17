#!/usr/bin/env python3
"""
Google Drive Manager for Pathways for Care Viewer
Uses Google Drive API to read/write CSV files
Supports both OAuth (local) and Service Account (web deployment)
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any, List
import io
import requests

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Google Drive API imports
try:
    from google.oauth2.credentials import Credentials
    from google.oauth2 import service_account
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
    import pickle
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False
    print("⚠️  Google Drive API not available. Install with: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")

# HARDCODE your file ID here if needed
HARDCODED_FILE_ID = "1IDixZ49uXsCQsAdjZkVAm_6vcSNU0uehiUm7Wc2JRWQ"
# API Key for simple access - load from environment variable
API_KEY = os.getenv('GOOGLE_API_KEY', '')

class GoogleDriveManager:
    def __init__(self, use_service_account: bool = True):
        """Initialize Google Drive manager"""
        self.service = None
        self.file_id = None
        self.credentials = None
        self.use_service_account = use_service_account
        
    def authenticate(self) -> bool:
        """Authenticate with Google Drive API"""
        if not GOOGLE_DRIVE_AVAILABLE:
            print("❌ Google Drive API not available")
            return False
            
        try:
            if self.use_service_account:
                return self._authenticate_service_account()
            else:
                return self._authenticate_oauth()
                
        except Exception as e:
            print(f"❌ Google Drive authentication failed: {e}")
            return False
    
    def _authenticate_service_account(self) -> bool:
        """Authenticate using service account"""
        try:
            # Check for service account key file
            key_file = 'service_account_key.json'
            if not os.path.exists(key_file):
                print(f"❌ {key_file} not found")
                print("📋 To set up service account:")
                print("1. Go to Google Cloud Console > APIs & Services > Credentials")
                print("2. Create a Service Account")
                print("3. Create and download a JSON key")
                print("4. Rename to 'service_account_key.json' and place in this directory")
                return False
            
            # Load service account credentials
            SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/spreadsheets.readonly']
            credentials = service_account.Credentials.from_service_account_file(
                key_file, scopes=SCOPES)
            
            self.credentials = credentials
            self.service = build('drive', 'v3', credentials=credentials)
            print("✅ Service account authentication successful")
            return True
        except Exception as e:
            print(f"❌ Service account authentication failed: {e}")
            return False
    
    def _authenticate_oauth(self) -> bool:
        """Authenticate using OAuth (for local development)"""
        try:
            # If modifying these scopes, delete the file token.pickle.
            SCOPES = ['https://www.googleapis.com/auth/drive.file']
            
            creds = None
            # The file token.pickle stores the user's access and refresh tokens
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    # Check if credentials.json exists
                    if not os.path.exists('credentials.json'):
                        print("❌ credentials.json not found")
                        print("📋 To set up Google Drive access:")
                        print("1. Go to https://console.developers.google.com/")
                        print("2. Create a new project or select existing")
                        print("3. Enable Google Drive API")
                        print("4. Create credentials (OAuth 2.0 Client ID)")
                        print("5. Download credentials.json to this directory")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            
            self.credentials = creds
            self.service = build('drive', 'v3', credentials=creds)
            print("✅ OAuth authentication successful")
            return True
        except Exception as e:
            print(f"❌ OAuth authentication failed: {e}")
            return False
    
    def find_or_create_csv_file(self, filename: str = "pathways_data.csv") -> Optional[str]:
        """Find existing CSV file or create new one"""
        if HARDCODED_FILE_ID:
            print(f"🔗 Using hardcoded file ID: {HARDCODED_FILE_ID}")
            return HARDCODED_FILE_ID
        try:
            if not self.service:
                return None
            
            # Search for existing file
            query = f"name='{filename}' and mimeType='text/csv' and trashed=false"
            results = self.service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
            files = results.get('files', [])
            
            if files:
                # Use existing file
                file_id = files[0]['id']
                print(f"✅ Found existing file: {filename} (ID: {file_id})")
                return file_id
            else:
                # Create new file
                file_metadata = {
                    'name': filename,
                    'mimeType': 'text/csv'
                }
                
                # Create empty CSV with headers
                csv_content = "AID,Animal Name,Location,SubLocation,Age,Stage,Foster_Attempted,Transfer_Attempted,Communications_Team_Attempted,Welfare_Notes,Image_URLs\n"
                
                media = MediaIoBaseUpload(
                    io.BytesIO(csv_content.encode('utf-8')),
                    mimetype='text/csv',
                    resumable=True
                )
                
                file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                
                file_id = file.get('id')
                print(f"✅ Created new file: {filename} (ID: {file_id})")
                
                # Make file accessible to anyone with the link
                self.service.permissions().create(
                    fileId=file_id,
                    body={'type': 'anyone', 'role': 'writer'},
                    fields='id'
                ).execute()
                
                return file_id
                
        except Exception as e:
            print(f"❌ Error finding/creating CSV file: {e}")
            return None
    
    def read_from_sheets_with_api_key(self, file_id: str = None) -> Optional[pd.DataFrame]:
        """Read Google Sheet using simple API key (no authentication needed)"""
        try:
            if not file_id:
                file_id = HARDCODED_FILE_ID
            
            # Read from Google Sheets using API key
            url = f"https://sheets.googleapis.com/v4/spreadsheets/{file_id}/values/A:Z?key={API_KEY}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                values = data.get('values', [])
                
                if not values:
                    print('✅ Google Sheet is empty')
                    return pd.DataFrame()
                
                # Convert to DataFrame
                df = pd.DataFrame(values[1:], columns=values[0])  # First row as headers
                print(f"✅ Loaded {len(df)} records from Google Sheets using API key")
                return df.reset_index(drop=True)
            else:
                print(f"❌ Failed to load data from Google Sheets: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error reading from Google Sheets with API key: {e}")
            return None

    def read_csv_from_drive(self, file_id: str = None, sheet_name: str = None) -> Optional[pd.DataFrame]:
        """Read Google Sheet from Google Drive"""
        try:
            if not self.service:
                return None
            if not file_id:
                file_id = self.find_or_create_csv_file()
                if not file_id:
                    return None
            self.file_id = file_id

            sheets_service = build('sheets', 'v4', credentials=self.credentials)
            # If no sheet_name provided, get the first sheet
            sheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=file_id).execute()
            if not sheet_name:
                sheet_name = sheet_metadata['sheets'][0]['properties']['title']
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=file_id,
                range=sheet_name
            ).execute()
            values = result.get('values', [])
            if not values:
                print('✅ Google Sheet is empty')
                return pd.DataFrame()
            df = pd.DataFrame(values)
            df.columns = df.iloc[0]
            df = df[1:]
            print(f"✅ Loaded {len(df)} records from Google Sheet")
            return df.reset_index(drop=True)
        except Exception as e:
            print(f"❌ Error reading Google Sheet from Drive: {e}")
            return None
    
    def write_csv_to_drive(self, df: pd.DataFrame, file_id: str = None) -> bool:
        """Write DataFrame to CSV file in Google Drive"""
        try:
            if not self.service:
                return False
            
            if not file_id:
                file_id = self.file_id or self.find_or_create_csv_file()
                if not file_id:
                    return False
            
            # Convert DataFrame to CSV string
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_content = csv_buffer.getvalue()
            
            # Upload to Drive
            media = MediaIoBaseUpload(
                io.BytesIO(csv_content.encode('utf-8')),
                mimetype='text/csv',
                resumable=True
            )
            
            self.service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
            
            print(f"✅ Updated CSV file in Google Drive ({len(df)} records)")
            return True
            
        except Exception as e:
            print(f"❌ Error writing CSV to Drive: {e}")
            return False
    
    def update_animal_record(self, aid: str, foster_value: str, transfer_value: str, 
                           communications_value: str, new_note: str) -> bool:
        """Update animal record in CSV file"""
        try:
            # Read current data
            df = self.read_csv_from_drive()
            if df is None:
                return False
            
            # Find the animal record
            animal_mask = df['AID'] == aid
            if not animal_mask.any():
                print(f"❌ Animal {aid} not found in data")
                return False
            
            # Get current welfare notes
            current_notes = df.loc[animal_mask, 'Welfare_Notes'].iloc[0]
            if pd.isna(current_notes):
                current_notes = ""
            
            # Add new note if provided
            if new_note and new_note.strip():
                if current_notes:
                    new_welfare_notes = f"{current_notes}\n\n{new_note.strip()}"
                else:
                    new_welfare_notes = new_note.strip()
            else:
                new_welfare_notes = current_notes
            
            # Update the record
            df.loc[animal_mask, 'Foster_Attempted'] = foster_value
            df.loc[animal_mask, 'Transfer_Attempted'] = transfer_value
            df.loc[animal_mask, 'Communications_Team_Attempted'] = communications_value
            df.loc[animal_mask, 'Welfare_Notes'] = new_welfare_notes
            
            # Write back to Drive
            success = self.write_csv_to_drive(df)
            return success
            
        except Exception as e:
            print(f"❌ Error updating animal record: {e}")
            return False

    def update_animal_record_with_api_key(self, aid: str, foster_value: str, transfer_value: str, 
                                        communications_value: str, new_note: str) -> bool:
        """Update animal record in Google Sheet using API key"""
        try:
            # Read current data using API key
            df = self.read_from_sheets_with_api_key()
            if df is None:
                print("❌ Failed to read data from Google Sheets")
                return False
            
            # Find the animal record
            animal_mask = df['AID'] == aid
            if not animal_mask.any():
                print(f"❌ Animal {aid} not found in data")
                return False
            
            # Get current welfare notes
            welfare_col = None
            for col in ['Welfare_Notes', 'Welfare Notes', 'welfare_notes']:
                if col in df.columns:
                    welfare_col = col
                    break
            
            if welfare_col:
                current_notes = df.loc[animal_mask, welfare_col].iloc[0]
                if pd.isna(current_notes):
                    current_notes = ""
                
                # Add new note if provided
                if new_note and new_note.strip():
                    if current_notes:
                        new_welfare_notes = f"{current_notes}\n\n{new_note.strip()}"
                    else:
                        new_welfare_notes = new_note.strip()
                else:
                    new_welfare_notes = current_notes
            else:
                new_welfare_notes = new_note.strip() if new_note and new_note.strip() else ""
            
            # Find column names for the dropdown fields
            foster_col = None
            transfer_col = None
            communications_col = None
            
            for col in df.columns:
                col_lower = col.lower()
                if 'foster' in col_lower:
                    foster_col = col
                elif 'transfer' in col_lower:
                    transfer_col = col
                elif 'communications' in col_lower:
                    communications_col = col
            
            # Update the record
            if foster_col:
                df.loc[animal_mask, foster_col] = foster_value
            if transfer_col:
                df.loc[animal_mask, transfer_col] = transfer_value
            if communications_col:
                df.loc[animal_mask, communications_col] = communications_value
            if welfare_col:
                df.loc[animal_mask, welfare_col] = new_welfare_notes
            
            # Convert DataFrame to values for Google Sheets API
            values = [df.columns.tolist()] + df.values.tolist()
            
            # Update Google Sheet using API key
            url = f"https://sheets.googleapis.com/v4/spreadsheets/{HARDCODED_FILE_ID}/values/A:Z?valueInputOption=RAW&key={API_KEY}"
            
            # Prepare the update request
            update_data = {
                "values": values
            }
            
            response = requests.put(url, json=update_data)
            
            if response.status_code == 200:
                print(f"✅ Successfully updated animal {aid} in Google Sheets")
                return True
            else:
                print(f"❌ Failed to update Google Sheet: {response.status_code} - {response.text}")
                return False
            
        except Exception as e:
            print(f"❌ Error updating animal record with API key: {e}")
            return False
    
    def get_pathways_data(self) -> Optional[pd.DataFrame]:
        """Get all pathways data from CSV"""
        return self.read_csv_from_drive()
    
    def get_animal_by_id(self, aid: str) -> Optional[pd.DataFrame]:
        """Get animal by AID"""
        try:
            df = self.read_csv_from_drive()
            if df is None:
                return None
            
            animal_data = df[df['AID'] == aid]
            if len(animal_data) == 0:
                return None
            
            return animal_data
            
        except Exception as e:
            print(f"❌ Error getting animal by ID: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test Google Drive connection"""
        try:
            if not self.authenticate():
                return False
            
            file_id = self.find_or_create_csv_file()
            return file_id is not None
            
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False

# Global Google Drive manager instance
_gdrive_manager = None

def get_gdrive_manager(use_service_account: bool = True) -> GoogleDriveManager:
    """Get global Google Drive manager instance"""
    global _gdrive_manager
    if _gdrive_manager is None:
        _gdrive_manager = GoogleDriveManager(use_service_account=use_service_account)
    return _gdrive_manager

def connect_to_gdrive(use_service_account: bool = True) -> bool:
    """Connect to Google Drive"""
    manager = get_gdrive_manager(use_service_account=use_service_account)
    return manager.authenticate()

def test_gdrive_connection(use_service_account: bool = True) -> bool:
    """Test Google Drive connection"""
    manager = get_gdrive_manager(use_service_account=use_service_account)
    return manager.test_connection() 