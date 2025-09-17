// Background script for LinkedIn Outreach Message Generator Extension

// Extension installation handler
chrome.runtime.onInstalled.addListener((details) => {
    console.log('LinkedIn Outreach Message Generator installed');
    
    if (details.reason === 'install') {
        console.log('Extension installed for the first time');
    } else if (details.reason === 'update') {
        console.log('Extension updated');
    }
});

// Handle extension icon click (optional - popup handles most functionality)
chrome.action.onClicked.addListener((tab) => {
    console.log('Extension icon clicked on tab:', tab.url);
});

// Listen for messages from content scripts or popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('Background script received message:', request);
    
    if (request.action === 'checkLinkedInPage') {
        // Check if current tab is a LinkedIn profile page
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            const currentTab = tabs[0];
            const isLinkedIn = currentTab.url.includes('linkedin.com/in/');
            sendResponse({ isLinkedInProfile: isLinkedIn, url: currentTab.url });
        });
        return true; // Keep message channel open for async response
    }
    
    if (request.action === 'log') {
        console.log('Log from content/popup:', request.message);
        sendResponse({ success: true });
    }
});

// Optional: Handle tab updates to manage extension state
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url) {
        const isLinkedInProfile = tab.url.includes('linkedin.com/in/');
        
        // You could update extension icon here based on page type
        if (isLinkedInProfile) {
            chrome.action.setIcon({
                tabId: tabId,
                path: {
                    "16": "icons/icon16.png",
                    "32": "icons/icon32.png",
                    "48": "icons/icon48.png",
                    "128": "icons/icon128.png"
                }
            });
        }
    }
});