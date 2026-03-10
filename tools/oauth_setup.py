import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Restrict scope to only drive.file to keep permissions minimal
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def main():
    creds = None
    
    # Calculate paths relative to the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    token_path = os.path.join(project_root, "Req_File", "token.json")
    credentials_path = os.path.join(project_root, "Req_File", "credentials.json")

    # If the token already exists, try to load it
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    # If there are no (valid) credentials available, force a login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing existing token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                print(f"[!] ERROR: {credentials_path} not found.")
                print("[!] Please go to Google Cloud Console > APIs & Services > Credentials.")
                print("[!] Create an 'OAuth client ID' (Desktop App), download the JSON, rename it to 'credentials.json', and place it in your Req_File folder.")
                return
                
            print("Starting local server for authentication. Please check your browser...")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credential for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        print(f"\n[OK] Success! OAuth token saved to: {token_path}")
        print("[OK] You can now safely run the pipeline. Your .tex files will be uploaded to Drive.")
    else:
        print(f"[OK] Token exists and is valid at: {token_path}")

if __name__ == '__main__':
    main()
