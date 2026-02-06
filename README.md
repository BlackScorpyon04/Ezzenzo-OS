🧠 Ezzenzo OSThe internal operating system for Ezzenzo Scents & Media.🚀 How to RunInstall Dependencies:pip install -r requirements.txt
Run the App:streamlit run app.py
The app will launch in "Demo Mode" automatically if secrets are not found.🔌 Connecting Real DataTo enable Google Sheets and Gemini AI, you need to set up the .streamlit/secrets.toml file.Create the File:Create a folder named .streamlit in your project root, and a file named secrets.toml inside it.Google Sheets Setup:Go to Google Cloud Console > Create Project.Enable "Google Sheets API" and "Google Drive API".Create a "Service Account", download the JSON key.Crucial: Share your Google Sheet (email address provided in the JSON) with Editor access.Gemini API Setup:Get a key from Google AI Studio.Paste into secrets.toml:GEMINI_API_KEY = "your-api-key-here"

[connections.gsheets]
spreadsheet = "[https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE](https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE)"
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "..."
client_email = "..."
client_id = "..."
auth_uri = "[https://accounts.google.com/o/oauth2/auth](https://accounts.google.com/o/oauth2/auth)"
token_uri = "[https://oauth2.googleapis.com/token](https://oauth2.googleapis.com/token)"
auth_provider_x509_cert_url = "[https://www.googleapis.com/oauth2/v1/certs](https://www.googleapis.com/oauth2/v1/certs)"
client_x509_cert_url = "..."
📊 Sheet StructureYour Google Sheet should have two tabs:Transactions (Columns: Date, Type, Category, Amount, Project, Notes)Blends (Columns: Date, Blend_Name, Version, Formula, Testing_Notes, Rating)
