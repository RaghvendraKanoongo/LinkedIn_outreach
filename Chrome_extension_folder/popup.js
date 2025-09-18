// Configuration
const API_BASE_URL = 'https://linkedin-outreach.onrender.com/';

// DOM Elements
const loadingState = document.getElementById('loading-state');
const errorState = document.getElementById('error-state');
const notLinkedInState = document.getElementById('not-linkedin-state');
const successState = document.getElementById('success-state');
const initialState = document.getElementById('initial-state');
const generateBtn = document.getElementById('generate-btn');
const regenerateBtn = document.getElementById('regenerate-btn');
const retryBtn = document.getElementById('retry-btn');
const messagesContainer = document.getElementById('messages-container');
const profileNameEl = document.getElementById('profile-name');
const messageCountEl = document.getElementById('message-count');
const errorMessageEl = document.getElementById('error-message');

// State management
let currentLinkedInUrl = '';
let isGenerating = false;

// Utility functions
function hideAllStates() {
    loadingState.style.display = 'none';
    errorState.style.display = 'none';
    notLinkedInState.style.display = 'none';
    successState.style.display = 'none';
    initialState.style.display = 'none';
}

function showState(stateElement) {
    hideAllStates();
    stateElement.style.display = 'flex';
}

function isLinkedInProfile(url) {
    try {
        const urlObj = new URL(url);
        return urlObj.hostname.includes('linkedin.com') && urlObj.pathname.includes('/in/');
    } catch (e) {
        return false;
    }
}

function extractLinkedInUrl(url) {
    try {
        const urlObj = new URL(url);
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

function createMessageElement(message, index) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message-item';
    
    const messageText = document.createElement('p');
    messageText.className = 'message-text';
    messageText.textContent = message;
    
    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-btn';
    copyBtn.textContent = 'Copy';
    copyBtn.onclick = () => copyMessage(message, copyBtn);
    
    messageDiv.appendChild(messageText);
    messageDiv.appendChild(copyBtn);
    
    return messageDiv;
}

function copyMessage(message, buttonElement) {
    navigator.clipboard.writeText(message).then(() => {
        const originalText = buttonElement.textContent;
        buttonElement.textContent = 'Copied!';
        buttonElement.classList.add('copied');
        
        setTimeout(() => {
            buttonElement.textContent = originalText;
            buttonElement.classList.remove('copied');
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy message:', err);
        buttonElement.textContent = 'Error';
        setTimeout(() => {
            buttonElement.textContent = 'Copy';
        }, 2000);
    });
}

async function generateMessages() {
    if (isGenerating) return;
    
    try {
        isGenerating = true;
        showState(loadingState);
        
        console.log('Generating messages for URL:', currentLinkedInUrl);
        
        const response = await fetch(`${API_BASE_URL}/get-outreach-message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                linkedin_url: currentLinkedInUrl
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Server error occurred');
        }
        
        if (!data.success) {
            throw new Error(data.error || 'Failed to generate messages');
        }
        
        // Display success state
        displayMessages(data.messages, data.profile_name, data.total_messages);
        
    } catch (error) {
        console.error('Error generating messages:', error);
        showError(error.message || 'Failed to generate messages. Please try again.');
    } finally {
        isGenerating = false;
    }
}

function displayMessages(messages, profileName, totalMessages) {
    // Clear previous messages
    messagesContainer.innerHTML = '';
    
    // Set profile info
    profileNameEl.textContent = profileName || 'LinkedIn Profile';
    messageCountEl.textContent = totalMessages || messages.length;
    
    // Create message elements
    messages.forEach((message, index) => {
        const messageElement = createMessageElement(message, index);
        messagesContainer.appendChild(messageElement);
    });
    
    showState(successState);
}

function showError(message) {
    errorMessageEl.textContent = message;
    showState(errorState);
}

async function getCurrentTab() {
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        return tab;
    } catch (error) {
        console.error('Error getting current tab:', error);
        return null;
    }
}

async function initializeExtension() {
    try {
        const tab = await getCurrentTab();
        
        if (!tab) {
            showError('Unable to access current tab');
            return;
        }
        
        const extractedUrl = extractLinkedInUrl(tab.url);
        
        if (!extractedUrl) {
            showState(notLinkedInState);
            return;
        }
        
        currentLinkedInUrl = extractedUrl;
        console.log('Detected LinkedIn profile URL:', currentLinkedInUrl);
        
        showState(initialState);
        
    } catch (error) {
        console.error('Error initializing extension:', error);
        showError('Failed to initialize extension');
    }
}

// Event listeners
generateBtn.addEventListener('click', generateMessages);
regenerateBtn.addEventListener('click', generateMessages);
retryBtn.addEventListener('click', generateMessages);

// Initialize extension when popup opens
document.addEventListener('DOMContentLoaded', initializeExtension);

// Handle tab updates (if user navigates while popup is open)
if (chrome.tabs && chrome.tabs.onUpdated) {
    chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
        if (changeInfo.status === 'complete' && tab.active) {
            initializeExtension();
        }
    });
}