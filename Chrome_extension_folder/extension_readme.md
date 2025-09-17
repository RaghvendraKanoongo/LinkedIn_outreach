# LinkedIn Outreach Message Generator Chrome Extension

A Chrome extension that generates personalized LinkedIn outreach messages using AI, designed to help sales teams create authentic, conversation-starting messages.

## 🚀 Features

- **Auto-Detection**: Automatically detects LinkedIn profile pages
- **AI-Powered**: Generates 5 personalized outreach messages using Gemini AI
- **One-Click Copy**: Easy copy functionality for each message
- **Regenerate**: Get new messages with a single click
- **Professional UI**: Clean, intuitive interface
- **Error Handling**: Comprehensive error handling with user feedback

## 📋 Prerequisites

- Chrome browser
- Flask server running on `http://127.0.0.1:5020`
- Apify API key
- Google Gemini API key

## 🛠️ Installation

### 1. Flask Server Setup

First, ensure your Flask server is running with the updated code. You'll need these environment variables:

```bash
# Create a .env file with:
APIFY_API_KEY=your_apify_key_here
GEMINI_API_KEY=your_gemini_key_here
POSTS_ACTOR_ID=LQQIXN9Othf8f7R5n
PROFILE_ACTOR_ID=2SyF0bVxmgGr8IVCZ
```

Install dependencies:
```bash
pip install flask flask-cors apify-client google-generativeai python-dotenv
```

Run the server:
```bash
python app.py
```

### 2. Chrome Extension Installation

1. **Download Extension Files**: Save all the extension files to a folder:
   - `manifest.json`
   - `popup.html`
   - `popup.css`
   - `popup.js`
   - `background.js`
   - `content.js`

2. **Create Icons Folder**: Create an `icons` folder and add icon files:
   - `icon16.png` (16x16 pixels)
   - `icon32.png` (32x32 pixels)
   - `icon48.png` (48x48 pixels)
   - `icon128.png` (128x128 pixels)

   *Note: You can use any LinkedIn-themed icons or create simple placeholder icons for testing.*

3. **Load Extension in Chrome**:
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top-right corner)
   - Click "Load unpacked"
   - Select the folder containing your extension files
   - The extension should now appear in your extensions list

## 📁 File Structure

```
linkedin-outreach-extension/
├── manifest.json              # Extension configuration
├── popup.html                 # Extension popup UI
├── popup.css                  # Styling for popup
├── popup.js                   # Main extension logic
├── background.js              # Background script
├── content.js                 # Content script for LinkedIn pages
├── icons/                     # Extension icons
│   ├── icon16.png
│   ├── icon32.png
│   ├── icon48.png
│   └── icon128.png
└── README.md                  # This file
```

## 🎯 How to Use

1. **Navigate to LinkedIn**: Go to any LinkedIn profile page (e.g., `linkedin.com/in/username/`)

2. **Click Extension**: Click the extension icon in your browser toolbar

3. **Generate Messages**: Click "Generate Messages" to create 5 personalized outreach messages

4. **Copy Messages**: Use the "Copy" button next to any message you want to use

5. **Regenerate**: Click "Regenerate Messages" to get 5 new messages

## 🔧 Configuration

### API Endpoint Configuration

If your Flask server runs on a different URL, update the `API_BASE_URL` in `popup.js`:

```javascript
const API_BASE_URL = 'http://your-server:port';
```

### Styling Customization

Modify `popup.css` to customize the appearance:
- Colors: Update the gradient and LinkedIn blue colors
- Sizing: Adjust popup dimensions (currently 400x600px)
- Fonts: Change the font family if needed

## 🐛 Troubleshooting

### Extension Not Working
1. Check if Flask server is running on `http://127.0.0.1:5020`
2. Verify all environment variables are set correctly
3. Check browser console for error messages (F12 → Console tab)

### "Not LinkedIn Profile" Message
- Ensure you're on a LinkedIn profile page (`linkedin.com/in/username`)
- Try refreshing the page and clicking the extension again

### API Errors
- Check Flask server logs for detailed error messages
- Verify Apify and Gemini API keys are valid
- Ensure you have sufficient API credits

### No Messages Generated
- Check if the LinkedIn profile has recent posts
- Verify Apify actors are working correctly
- Check Gemini API rate limits

## 📊 API Response Format

The Flask server returns messages in this format:

```json
{
  "success": true,
  "messages": [
    "Message 1 content...",
    "Message 2 content...",
    "Message 3 content...",
    "Message 4 content...",
    "Message 5 content..."
  ],
  "profile_name": "John Doe",
  "total_messages": 5
}
```

## 🔒 Privacy & Security

- Extension only works on LinkedIn profile pages
- No data is stored locally in the browser
- All processing happens on your Flask server
- LinkedIn URLs are only sent to your own server

## 🚀 Future Enhancements

- Custom message templates
- Message history/favorites
- Bulk processing for multiple profiles
- Integration with CRM systems
- A/B testing for message effectiveness

## 🆘 Support

If you encounter issues:

1. Check Flask server logs for detailed error messages
2. Open browser DevTools (F12) and check the Console tab
3. Verify all API keys and environment variables are correct
4. Test the Flask API directly using curl or Postman

## 📝 License

This is a custom sales enablement tool. Use responsibly and in accordance with LinkedIn's Terms of Service.