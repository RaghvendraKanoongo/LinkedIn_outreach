from flask import Flask, request, jsonify
from dotenv import load_dotenv 
load_dotenv()
from flask_cors import CORS
from flask import Flask, request, jsonify
from flask_cors import CORS
from apify_client import ApifyClient
from google import genai
import json
import re
import os
import logging
from urllib.parse import urlparse
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for Chrome extension

# Environment variables
APIFY_API_KEY = os.getenv("APIFY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
POSTS_ACTOR_ID = os.getenv("POSTS_ACTOR_ID", "LQQIXN9Othf8f7R5n")  # Default from your script
PROFILE_ACTOR_ID = os.getenv("PROFILE_ACTOR_ID", "2SyF0bVxmgGr8IVCZ")  # Default from your script

# Validate required environment variables
if not APIFY_API_KEY:
    raise ValueError("APIFY_API_KEY environment variable is required")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required")

# Initialize clients
apify_client = ApifyClient(APIFY_API_KEY)
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

def validate_linkedin_url(url):
    """Validate if the provided URL is a valid LinkedIn profile URL"""
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # Check if it's a LinkedIn URL
        if 'linkedin.com' not in parsed.netloc.lower():
            return False
            
        # Check if it's a profile URL
        if '/in/' not in parsed.path:
            return False
            
        return True
    except Exception:
        return False

def scrape_linkedin_posts(linkedin_url, retries=2):
    """Scrape LinkedIn posts using Apify"""
    try:
        logger.info(f"Starting posts scraping for: {linkedin_url}")
        
        run_input = {
            "username": linkedin_url,
            "page_number": 1,
            "limit": 3,
        }
        
        # Start the actor run
        print(POSTS_ACTOR_ID)
        run = apify_client.actor(POSTS_ACTOR_ID).call(run_input=run_input)

       
        
        if not run or 'defaultDatasetId' not in run:
            raise Exception("Apify posts actor failed to return valid run data")
        
        print("========================Hello this is where I am working with ============================")
        print("========================Hello this is where I am working with ============================")
        print("========================Hello this is where I am working with ============================")
        # Get the results
        items = list(apify_client.dataset(run["defaultDatasetId"]).iterate_items())
        print(items)
        if not items:
            logger.warning(f"No posts found for LinkedIn URL: {linkedin_url}")
            return []
            
        logger.info(f"Successfully scraped {len(items)} posts")
        return items
        
    except Exception as e:
        error_msg = f"Apify posts scraping error: {str(e)}"
        logger.error(error_msg)
        
        if retries > 0:
            logger.info(f"Retrying posts scraping... {retries} attempts left")
            time.sleep(2)
            return scrape_linkedin_posts(linkedin_url, retries-1)
        
        raise Exception(error_msg)

def scrape_linkedin_profile(linkedin_url, retries=2):
    """Scrape LinkedIn profile using Apify"""
    try:
        logger.info(f"Starting profile scraping for: {linkedin_url}")
        
        profile_input = {
            "profileUrls": [linkedin_url]
        }
        
        # Start the actor run
        profile_run = apify_client.actor(PROFILE_ACTOR_ID).call(run_input=profile_input)
        
        if not profile_run or 'defaultDatasetId' not in profile_run:
            raise Exception("Apify profile actor failed to return valid run data")
        
        # Get the results
        profile_items = list(apify_client.dataset(profile_run["defaultDatasetId"]).iterate_items())
        print("++++++++++++++++++++++++++++++++hello++++++++++++++")
        print(profile_items)
        print("++++++++++++++++++++++++++++++++hello++++++++++++++")
        if not profile_items:
            raise Exception("No profile data found")
            
        logger.info(f"Successfully scraped profile data")
        return profile_items
        
    except Exception as e:
        error_msg = f"Apify profile scraping error: {str(e)}"
        logger.error(error_msg)
        
        if retries > 0:
            logger.info(f"Retrying profile scraping... {retries} attempts left")
            time.sleep(2)
            return scrape_linkedin_profile(linkedin_url, retries-1)
        
        raise Exception(error_msg)

def extract_profile_data(data):
    """Format profile data into readable text (in-memory)"""
    try:
        profile_info = data[0]
        formatted_data = []

        formatted_data.append("--- Profile Summary ---\n")
        formatted_data.append(f"Full Name: {profile_info.get('fullName', 'N/A')}")
        formatted_data.append(f"Headline: {profile_info.get('headline', 'N/A')}")
        formatted_data.append(f"Current Role: {profile_info.get('jobTitle', 'N/A')} at {profile_info.get('companyName', 'N/A')}")
        formatted_data.append(f"Location: {profile_info.get('addressCountryOnly', 'N/A')}")

        formatted_data.append("\n--- About Section ---\n")
        formatted_data.append(f"{profile_info.get('about', 'N/A')}")

        formatted_data.append("\n--- Skills ---\n")
        skills = [skill['title'] for skill in profile_info.get('skills', []) if 'title' in skill]
        formatted_data.append(", ".join(skills))

        formatted_data.append("\n--- Experience ---\n")
        experiences = profile_info.get('experiences', [])
        for exp in experiences:
            title = exp.get('title', 'N/A')
            company = exp.get('subtitle', 'N/A') if not exp.get('breakdown', False) else exp.get('title', 'N/A')
            caption = exp.get('caption', 'N/A')
            description = []
            
            if exp.get('breakdown', False):
                for sub in exp.get('subComponents', []):
                    for desc_item in sub.get('description', []):
                        if desc_item.get('type') == 'textComponent':
                            description.append(desc_item.get('text', ''))
            else:
                for sub in exp.get('subComponents', []):
                    for desc_item in sub.get('description', []):
                        if desc_item.get('type') == 'textComponent':
                            description.append(desc_item.get('text', ''))

            formatted_data.append(f"- {title} at {company} ({caption})")
            if description:
                formatted_data.append("  Description:")
                for d in description:
                    formatted_data.append(f"  - {d.strip()}")

        formatted_data.append("\n--- Education and Certifications ---\n")
        educations = profile_info.get('educations', [])
        for edu in educations:
            school = edu.get('title', 'N/A')
            degree = edu.get('subtitle', 'N/A')
            caption = edu.get('caption', 'N/A')
            formatted_data.append(f"- {degree} from {school} ({caption})")

            for sub in edu.get('subComponents', []):
                for desc_item in sub.get('description', []):
                    if desc_item.get('text', '').startswith('Activities and societies:'):
                        formatted_data.append(f"  {desc_item.get('text')}")

        licenses = profile_info.get('licenseAndCertificates', [])
        for cert in licenses:
            formatted_data.append(f"- {cert.get('title', 'N/A')} ({cert.get('subtitle', 'N/A')})")

        return "\n".join(formatted_data)
        
    except Exception as e:
        logger.error(f"Error extracting profile data: {str(e)}")
        raise Exception(f"Profile data formatting error: {str(e)}")

def extract_posts_data(data):
    """Format posts data into readable text (in-memory)"""
    try:
        formatted_data = []

        for i, post in enumerate(data):
            hashtags = re.findall(r'#(\w+)', post.get('text', ''))
            
            original_author = "N/A"
            if post.get('post_type') in ['repost', 'quote'] and 'reshared_post' in post:
                author_info = post['reshared_post'].get('author', {})
                first_name = author_info.get('first_name', '')
                last_name = author_info.get('last_name', '')
                original_author = f"{first_name} {last_name}".strip()
                if not original_author:
                    original_author = first_name

            formatted_data.append(f"--- Post #{i+1} ---\n")
            formatted_data.append(f"Posted: {post.get('posted_at', {}).get('relative', 'N/A')}")
            formatted_data.append(f"Post URL: {post.get('url', 'N/A')}")
            formatted_data.append(f"Reactions: {post.get('stats', {}).get('total_reactions', 'N/A')}")
            formatted_data.append(f"Comments: {post.get('stats', {}).get('comments', 'N/A')}")
            
            if original_author != "N/A":
                formatted_data.append(f"Original Author/Company: {original_author}")
                
            formatted_data.append("\n--- Post Content ---\n")
            formatted_data.append(f"{post.get('text', 'N/A')}")
            
            formatted_data.append("\n--- Hashtags ---\n")
            if hashtags:
                formatted_data.append(", ".join(hashtags))
            else:
                formatted_data.append("No hashtags found.")

            formatted_data.append("\n" + "="*50 + "\n")
            
        return "\n".join(formatted_data)
        
    except Exception as e:
        logger.error(f"Error extracting posts data: {str(e)}")
        raise Exception(f"Posts data formatting error: {str(e)}")

def generate_sales_hooks(profile_text, posts_text):
    """Generate sales hooks using Gemini LLM (in-memory)"""
    try:
        prompt_text = (
            "Can you give me hooks for outreaching this profile. I have scrapped the LinkedIn data for "
            "the person (his profile information and his past posts). I want to write a catchy message or "
            "have talking points for a call. Can you read it all and get me a small, concise, formatted data "
            "that looks at his recent posts and adds the major details that might help me in the call, in short "
            "so I know what he is interested in. Also, can I get his profile information "
            "in short that I could need in the calls. Below is his profile data and post data again only get me vvimp points from his post that I can use in messaging or calling don't give me bulk data:\n\n"
        )

        combined_content = prompt_text + profile_text + "\n\n" + posts_text

        logger.info("Generating sales hooks with Gemini LLM")
        
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20", 
            contents=combined_content
        )
        
        if not response or not response.text:
            raise Exception("LLM returned empty response")
            
        # Parse the response into structured hooks
        hooks_text = response.text.strip()
        
        # Split the response into individual hooks/points
        # This is a simple approach - you might want to refine this based on actual LLM output format
        hooks = []
        lines = hooks_text.split('\n')
        current_hook = ""
        
        for line in lines:
            line = line.strip()
            if line:
                # If line starts with bullet point, dash, or number, it's likely a new hook
                if line.startswith(('•', '-', '*', '1.', '2.', '3.', '4.', '5.')):
                    if current_hook:
                        hooks.append(current_hook.strip())
                    current_hook = line
                else:
                    if current_hook:
                        current_hook += " " + line
                    else:
                        current_hook = line
        
        # Add the last hook
        if current_hook:
            hooks.append(current_hook.strip())
        
        # If no structured hooks found, return the full response as a single hook
        if not hooks:
            hooks = [hooks_text]
        
        logger.info(f"Generated {len(hooks)} sales hooks")
        return hooks
        
    except Exception as e:
        error_msg = f"LLM generation error: {str(e)} - Failed to generate sales hooks from LinkedIn data"
        logger.error(error_msg)
        raise Exception(error_msg)


def generate_outreach_message(profile_text, posts_text):
    """Generates a personalized, human-sounding outreach message using Gemini LLM."""
    try:
        
        prompt = """
            You are a professional B2B marketer writing LinkedIn connection request messages on behalf of Consultadd, a Custom AI Solutions provider for SMBs. Your goal is to craft authentic, relationship-first connection requests for C-level executives, founders, and decision-makers. These messages must sound natural, personal, and human — not AI-generated or salesy.
Writing Guidelines
Tone & Style
Warm, conversational, professional.
Avoid salesy language, jargon, or generic “template” feel.
Messages should feel like they were written after genuinely reviewing the prospect’s profile or posts.
Personalization Basis
Use available inputs:
Career milestones, promotions, education, or skills.
Company growth, product launches, or announcements.
Industry expertise, domain authority, or thought leadership.
LinkedIn posts or shared content (if available).
Shared connections, events, or webinars.
If no posts are available, rely entirely on profile data (role, experience, company, expertise).
Choose one personalization angle per message.
Message Structure
Keep under 300 characters (short, clear, easy to read).
No brand mention in the first message unless the profile signals high relevance to AI solutions.
Focus on rapport-building, curiosity, and genuine interest.
End with a soft invitation to connect (not a CTA to buy).
Output Format
Generate exactly 5 different messages.
Each message must use a different personalization angle.
Separate each message with this delimiter:
 ---MESSAGE_SEPARATOR---
Example Output Format
Message 1 text here
---MESSAGE_SEPARATOR---
Message 2 text here
---MESSAGE_SEPARATOR---
Message 3 text here
---MESSAGE_SEPARATOR---
Message 4 text here
---MESSAGE_SEPARATOR---
Message 5 text here
Input Data
Use the following to personalize:
PROFILE DATA:
 {profile_data}
RECENT POSTS:
 {post_data}
""".format(profile_data=profile_text, post_data=posts_text)
        
        # Updated prompt to return structured messages with clear separators
        # prompt = """
        # You are an expert sales outreach copywriter. Your style is casual, authentic, and sounds like a message from a real peer, not a robot or a corporate template.

        # Your goal is to write short, personalized LinkedIn messages (under 60 words each) to start a conversation. The primary objective is to get a reply, NOT to sell a product.

        # Follow these strict rules:
        # - DO NOT use overly formal language like "I trust this message finds you well."
        # - DO NOT use generic compliments like "your impressive career."
        # - DO NOT mention my product, my company, or ask for a meeting.
        # - DO NOT use corporate buzzwords like "synergy" or "leverage."

        # Follow this exact process for EACH of the 5 messages:
        # 1. **Find the Hook:** Scour the recent posts for specific and interesting points.
        # 2. **Draft a 3-Sentence Message:**
        #     - **Sentence 1 (The Specific Observation):** Start by directly mentioning the specific detail you found.
        #     - **Sentence 2 (The Curious Question):** Ask a genuine, open-ended question about it that invites their expertise.
        #     - **Sentence 3 (The Simple Sign-off):** End with a casual, low-pressure closing.

        # IMPORTANT: Return EXACTLY 5 messages separated by "---MESSAGE_SEPARATOR---" so I can parse them programmatically.

        # Format example:
        # Message 1 content here
        # ---MESSAGE_SEPARATOR---
        # Message 2 content here
        # ---MESSAGE_SEPARATOR---
        # Message 3 content here
        # ---MESSAGE_SEPARATOR---
        # Message 4 content here
        # ---MESSAGE_SEPARATOR---
        # Message 5 content here

        # Now, analyze the data below and generate 5 different messages.

        # --- PROFILE DATA ---
        # {profile_data}

        # --- RECENT POSTS ---
        # {post_data}
        # """.format(profile_data=profile_text, post_data=posts_text)


        logger.info("Generating personalized outreach messages with Gemini LLM")
        
        response = gemini_client.models.generate_content(
            model="gemini-1.5-flash-latest",
            contents=prompt
        )
        
        if not response or not response.text:
            raise Exception("LLM returned empty response")
            
        # Parse the response into individual messages
        messages_text = response.text.strip()
        
        # Split by separator and clean up
        messages = []
        if "---MESSAGE_SEPARATOR---" in messages_text:
            raw_messages = messages_text.split("---MESSAGE_SEPARATOR---")
            for msg in raw_messages:
                clean_msg = msg.strip()
                if clean_msg:
                    messages.append(clean_msg)
        else:
            # Fallback: if separator not found, try to parse existing format
            # Look for "**Message X" patterns and extract content
            lines = messages_text.split('\n')
            current_message = ""
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Check if this line starts a new message
                if line.startswith('**Message') and ':' in line:
                    # Save previous message if it exists
                    if current_message:
                        messages.append(current_message.strip())
                        current_message = ""
                elif line.startswith('>'):
                    # This is message content (starts with >)
                    message_content = line[1:].strip()  # Remove the > symbol
                    if current_message:
                        current_message += " " + message_content
                    else:
                        current_message = message_content
                elif not line.startswith('**') and current_message:
                    # Continue building current message
                    current_message += " " + line
            
            # Add the last message
            if current_message:
                messages.append(current_message.strip())
        
        # Ensure we have at least one message
        if not messages:
            messages = [messages_text]
        
        # Limit to 5 messages and clean them up
        messages = messages[:5]
        cleaned_messages = []
        for msg in messages:
            # Remove any remaining formatting characters
            cleaned_msg = msg.replace('>', '').replace('**', '').strip()
            if cleaned_msg:
                cleaned_messages.append(cleaned_msg)
        
        logger.info(f"Successfully generated {len(cleaned_messages)} outreach messages.")
        return cleaned_messages
        
    except Exception as e:
        error_msg = f"LLM message generation error: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

# def generate_outreach_message(profile_text, posts_text):
#     """Generates a personalized, human-sounding outreach message using Gemini LLM."""
#     try:
#         # 1. The new prompt for generating a conversational message
#         prompt = """
#         You are an expert sales outreach copywriter. Your style is casual, authentic, and sounds like a message from a real peer, not a robot or a corporate template.

#         Your goal is to write a short, personalized LinkedIn message (under 60 words) to start a conversation. The primary objective is to get a reply, NOT to sell a product.

#         Follow these strict rules:
#         - DO NOT use overly formal language like "I trust this message finds you well."
#         - DO NOT use generic compliments like "your impressive career."
#         - DO NOT mention my product, my company, or ask for a meeting.
#         - DO NOT use corporate buzzwords like "synergy" or "leverage."

#         Follow this exact process:
#         1.  **Find the Hook:** Scour the recent posts for the single most specific and interesting point. It could be a unique opinion, a question they asked, or a 
#         specific project they mentioned.
#         2.  **Draft a 3-Sentence Message:**
#             - **Sentence 1 (The Specific Observation):** Start by directly mentioning the specific detail you found.
#             - **Sentence 2 (The Curious Question):** Ask a genuine, open-ended question about it that invites their expertise.
#             - **Sentence 3 (The Simple Sign-off):** End with a casual, low-pressure closing.
#         also provide me 5 different messages so I can select from them also this is an api call so just formate it by spaces
#         Now, analyze the data below and generate the message.

#         --- PROFILE DATA ---
#         {profile_data}

#         --- RECENT POSTS ---
#         {post_data}
#         """.format(profile_data=profile_text, post_data=posts_text)

#         logger.info("Generating personalized outreach message with Gemini LLM")
        
#         response = gemini_client.models.generate_content(
#             model="gemini-1.5-flash-latest",
#             contents=prompt
#         )
        
#         if not response or not response.text:
#             raise Exception("LLM returned empty response")
            
#         # 2. The response handling is now much simpler
#         message = response.text.strip()
        
#         logger.info("Successfully generated outreach message.")
#         return message
        
#     except Exception as e:
#         error_msg = f"LLM message generation error: {str(e)}"
#         logger.error(error_msg)
#         raise Exception(error_msg)

@app.route('/get-hooks', methods=['POST'])
def get_sales_hooks():
    """Main API endpoint to generate sales hooks from LinkedIn URL"""
    try:
        # Get LinkedIn URL from request
        data = request.get_json()
        
        if not data or 'linkedin_url' not in data:
            return jsonify({
                'error': 'Missing linkedin_url in request body',
                'success': False
            }), 400
        
        linkedin_url = data['linkedin_url'].strip()
        
        # Validate LinkedIn URL
        if not validate_linkedin_url(linkedin_url):
            return jsonify({
                'error': f'Cannot find valid LinkedIn URL: {linkedin_url}',
                'success': False
            }), 400
        
        logger.info(f"Processing LinkedIn URL: {linkedin_url}")
        
        # Step 1: Scrape LinkedIn data using Apify
        try:
            posts_data = scrape_linkedin_posts(linkedin_url)
            profile_data = scrape_linkedin_profile(linkedin_url)
        except Exception as e:
            return jsonify({
                'error': f"Error on Apify scraping: {str(e)}",
                'success': False
            }), 500
        
        # Step 2: Format the scraped data
        try:
            profile_text = extract_profile_data(profile_data)
            posts_text = extract_posts_data(posts_data) if posts_data else "No recent posts found."
        except Exception as e:
            return jsonify({
                'error': f"Data formatting error: {str(e)}",
                'success': False
            }), 500
        
        # Step 3: Generate sales hooks using LLM
        try:
            hooks = generate_sales_hooks(profile_text, posts_text)
        except Exception as e:
            return jsonify({
                'error': str(e),
                'success': False
            }), 500
        
        # Return successful response
        return jsonify({
            'hooks': hooks,
            'success': True,
            'profile_name': profile_data[0].get('fullName', 'N/A') if profile_data else 'N/A',
            'total_hooks': len(hooks)
        }), 200
        
    except Exception as e:
        logger.error(f"Unexpected error in get_sales_hooks: {str(e)}")
        return jsonify({
            'error': f'Unexpected server error: {str(e)}',
            'success': False
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Sales Hooks Generator',
        'version': '1.0.0'
    }), 200

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        'message': 'Sales Hooks Generator API',
        'endpoints': {
            'POST /get-hooks': 'Generate sales hooks from LinkedIn URL',
            'GET /health': 'Health check',
        },
        'usage': {
            'POST /get-hooks': {
                'body': {'linkedin_url': 'https://www.linkedin.com/in/username/'},
                'response': {'hooks': ['hook1', 'hook2'], 'success': True}
            }
        }
    })

@app.route('/get-outreach-message', methods=['POST'])
def get_outreach_message_endpoint():
    """Generate personalized LinkedIn outreach messages"""
    try:
        data = request.get_json()
            
        if not data or 'linkedin_url' not in data:
            return jsonify({
                'error': 'Missing linkedin_url in request body',
                'success': False
            }), 400
            
        linkedin_url = data['linkedin_url'].strip()
        
        # Validate LinkedIn URL
        if not validate_linkedin_url(linkedin_url):
            return jsonify({
                'error': f'Cannot find valid LinkedIn URL: {linkedin_url}',
                'success': False
            }), 400
        
        logger.info(f"Processing LinkedIn URL for outreach messages: {linkedin_url}")

        # Step 1: Scrape LinkedIn data using Apify
        try:
            posts_data = scrape_linkedin_posts(linkedin_url)
            profile_data = scrape_linkedin_profile(linkedin_url)
        except Exception as e:
            return jsonify({
                'error': f"Error on Apify scraping: {str(e)}",
                'success': False
            }), 500
        
        # Step 2: Format the scraped data
        try:
            profile_text = extract_profile_data(profile_data)
            posts_text = extract_posts_data(posts_data) if posts_data else "No recent posts found."
        except Exception as e:
            return jsonify({
                'error': f"Data formatting error: {str(e)}",
                'success': False
            }), 500

        # Step 3: Generate the outreach messages using the updated function
        try:
            messages = generate_outreach_message(profile_text, posts_text)
        except Exception as e:
            return jsonify({
                'error': str(e),
                'success': False
            }), 500

        # Return the successful response with messages array
        return jsonify({
            'success': True,
            'messages': messages,
            'profile_name': profile_data[0].get('fullName', 'N/A') if profile_data else 'N/A',
            'total_messages': len(messages)
        }), 200

    except Exception as e:
        logger.error(f"Unexpected error in get_outreach_message_endpoint: {str(e)}")
        return jsonify({
            'error': f'Unexpected server error: {str(e)}',
            'success': False
        }), 500




# @app.route('/get-outreach-message', methods=['POST']) # Renamed for clarity
# def get_outreach_message_endpoint():
    
#     data = request.get_json()
        
#     if not data or 'linkedin_url' not in data:
#             return jsonify({
#                 'error': 'Missing linkedin_url in request body',
#                 'success': False
#             }), 400
        
#     linkedin_url = data['linkedin_url'].strip()

#     try:
#         # Step 1 & 2 are the same (scrape and format data)
#         posts_data = scrape_linkedin_posts(linkedin_url)
#         profile_data = scrape_linkedin_profile(linkedin_url)
#         profile_text = extract_profile_data(profile_data)
#         posts_text = extract_posts_data(posts_data) if posts_data else "No recent posts found."

#         # Step 3: Generate the outreach message using the new function
#         outreach_message = generate_outreach_message(profile_text, posts_text)

#         # Return the successful response with the message
#         return jsonify({
#             'success': True,
#             'message': outreach_message,
#             'profile_name': profile_data[0].get('fullName', 'N/A')
#         }), 200

#     except Exception as e:
#         error_msg = f"LLM generation error: {str(e)} - Failed to generate sales hooks from LinkedIn data"
#         logger.error(error_msg)
#         raise Exception(error_msg)

if __name__ == '__main__':
    logger.info("Starting Sales Hooks Generator API Server")
    print('trying')
    logger.info(f"Apify API Key: {'✓ Set' if APIFY_API_KEY else '✗ Missing'}")
    print('Yes')
    logger.info(f"Gemini API Key: {'✓ Set' if GEMINI_API_KEY else '✗ Missing'}")
    logger.info(f"Posts Actor ID: {POSTS_ACTOR_ID}")
    logger.info(f"Profile Actor ID: {PROFILE_ACTOR_ID}")
    


    app.run(debug=True, host='0.0.0.0', port=5020)







# from flask import Flask, render_template
# app = Flask(__name__)
# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"

# @app.route("/products")
# def product_page():
#     return render_template('index.html')
#     # return "<p>This is product Page</p>"

# def hello_world():
#     return "<p>Hello, World!</p>"
# if __name__ == "__main__":  
#     app.run(debug=True, port=8000)