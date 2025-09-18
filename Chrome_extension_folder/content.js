// Content script for LinkedIn Outreach Message Generator Extension
// This script runs on LinkedIn pages to provide additional functionality

(function() {
    'use strict';
    
    // Check if we're on a LinkedIn profile page
    function isLinkedInProfilePage() {
        return window.location.hostname.includes('linkedin.com') && 
               window.location.pathname.includes('/in/');
    }
    
    // Extract LinkedIn profile URL from current page
    function extractLinkedInProfileUrl() {
        try {
            const currentUrl = window.location.href;
            const urlObj = new URL(currentUrl);
            
            if (!urlObj.hostname.includes('linkedin.com') || !urlObj.pathname.includes('/in/')) {
                return null;
            }
            
            // Clean the URL to get just the profile URL
            const pathMatch = urlObj.pathname.match(/\/in\/([^\/]+)/);
            if (pathMatch) {
                return `https://www.linkedin.com/in/${pathMatch[1]}/`;
            }
            return null;
        } catch (e) {
            console.error('Error extracting LinkedIn URL:', e);
            return null;
        }
    }
    
    // Send profile URL to extension popup when requested
    function handleMessage(request, sender, sendResponse) {
        if (request.action === 'getLinkedInUrl') {
            const profileUrl = extractLinkedInProfileUrl();
            const isProfile = isLinkedInProfilePage();
            
            sendResponse({
                success: true,
                profileUrl: profileUrl,
                isLinkedInProfile: isProfile,
                currentUrl: window.location.href
            });
        }
        
        if (request.action === 'checkPageType') {
            sendResponse({
                isLinkedInProfile: isLinkedInProfilePage(),
                profileUrl: extractLinkedInProfileUrl()
            });
        }
    }
    
    // Listen for messages from popup
    chrome.runtime.onMessage.addListener(handleMessage);
    
    // Optional: Add visual indicators or helpers (can be extended later)
    function addExtensionIndicator() {
        if (!isLinkedInProfilePage()) return;
        
        // This could be used to add visual indicators on the page
        // For now, we'll keep it minimal
        console.log('LinkedIn Outreach Generator: Profile page detected');
    }
    
    // Initialize when page loads
    function initialize() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', addExtensionIndicator);
        } else {
            addExtensionIndicator();
        }
    }
    
    // Handle single-page app navigation (LinkedIn uses React Router)
    let lastUrl = location.href;
    new MutationObserver(() => {
        const url = location.href;
        if (url !== lastUrl) {
            lastUrl = url;
            setTimeout(addExtensionIndicator, 1000); // Wait for page to settle
        }
    }).observe(document, { subtree: true, childList: true });
    initialize();
    
})();