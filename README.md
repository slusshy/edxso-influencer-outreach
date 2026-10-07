<<<<<<< HEAD
# Fieldnotes — Creator Research

Fieldnotes discovers YouTube creators for a campaign, enriches public channel data, evaluates audience size, topic relevance and recent-video engagement, and prepares personalized outreach drafts for review.

## Features

- Search multiple YouTube creator phrases and deduplicate by channel ID.
- Review public subscriber counts, recent video titles, estimated engagement and publicly listed contact details.
- Set campaign-specific audience, relevance and engagement criteria.
- Prepare and validate personalized email and Instagram DM drafts with Gemini.
- Search, sort, filter, inspect and export campaign results.
- Save campaign snapshots and a simulated outreach review log in SQLite.
- Never send email automatically or invent missing contact information.

## Run locally

Use Python 3.10 or newer.

1. Create and activate a virtual environment.
2. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and set valid `YOUTUBE_API_KEY` and `GEMINI_API_KEY` values.
4. Start the web app:

   ```sh
   python server.py
   ```

5. Open `http://localhost:5000`.

Install test tooling and run the suite with:

```sh
pip install -r requirements-dev.txt
python -m pytest -q
```

## Deploy on Railway

Deploy the project directory (the directory containing `server.py` and `requirements.txt`) from GitHub.

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn server:app --bind 0.0.0.0:$PORT`
- Add `YOUTUBE_API_KEY` and `GEMINI_API_KEY` in Railway service variables. Do not commit `.env` or paste keys into source files.
- For campaign history to survive redeploys, attach a Railway Volume mounted at `/app/data` and set `DATA_DIR=/app/data`.
- Keep one service replica while using SQLite.
- Verify the deployment at `/api/health`.

The application uses YouTube Data API and Gemini quotas and terms. Gemini features require an active, valid Google project and API key. The SQLite database and CSV exports are local generated data; they are excluded from Git.

## Project layout

```text
app/                 Discovery, enrichment, fit rules, personalization and outreach
static/              Fieldnotes browser styles and interactions
templates/           Main Fieldnotes page
tests/               Backend, web and behavior tests
data/                Local database and generated CSV exports
main.py              CLI and research pipeline
server.py            Flask web server and JSON endpoints
requirements.txt     Runtime and test dependencies
requirements-dev.txt Test-only dependencies
Procfile             Gunicorn process command
.env.example         Environment-variable template (placeholders only)
```
=======
# 🤖 AI Influencer Outreach System

An automated AI-powered influencer discovery and outreach pipeline built for the **EDXSO AI Engineer Intern Assignment**.

The system discovers relevant micro-influencers from YouTube, enriches their profiles, filters them based on predefined criteria, generates personalized collaboration messages using Google Gemini, and simulates outreach while maintaining a persistent outreach tracker.

---

## 🚀 Features

- 🔎 Discover 50+ YouTube creators using the YouTube Data API
- 📊 Collect subscriber and engagement metrics
- 🧹 Deduplicate creators using YouTube Channel IDs
- 🎯 Automatically qualify and reject creators
- 📝 Generate qualification and rejection reasons
- 📧 Find publicly available contact emails
- 🤖 Generate personalized collaboration emails using Google Gemini
- 💬 Generate personalized Instagram DMs
- ✅ Validate email and DM word counts
- 🚫 Never guess or fabricate email addresses
- 📤 Simulate email outreach safely
- 🔁 Prevent duplicate outreach
- 🗄️ Store outreach history in SQLite
- 📄 Export influencer and outreach datasets as CSV
- ⚙️ Modular architecture for future scaling

---

## 🏗️ Workflow

```text
YouTube Data API
       ↓
Creator Discovery
       ↓
Data Enrichment
       ↓
Filtering & Classification
       ↓
Qualified Creators
       ↓
Gemini Personalization
       ↓
Email + Instagram DM
       ↓
Message Validation
       ↓
Simulated Outreach
       ↓
SQLite Outreach Tracking
       ↓
CSV Export

🛠️ Tech Stack
Language
Python 3
APIs
YouTube Data API v3
Google Gemini API
Libraries
google-api-python-client
google-genai
python-dotenv
pandas
Storage
SQLite
CSV

📁 Project Structure
edxso-ai-influencer-outreach/
│
├── app/
│   ├── discovery/
│   │   └── youtube.py
│   │
│   ├── enrichment/
│   │   ├── metrics.py
│   │   └── contact.py
│   │
│   ├── filtering/
│   │   └── qualification.py
│   │
│   ├── personalization/
│   │   ├── gemini.py
│   │   └── validator.py
│   │
│   ├── outreach/
│   │   └── email_sender.py
│   │
│   └── database/
│       ├── db.py
│       └── export_outreach.py
│
├── data/
│   ├── influencers.csv
│   ├── outreach.db
│   └── outreach_tracker.csv
│
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
🔍 Influencer Discovery

The discovery layer uses the YouTube Data API v3.

The system searches multiple AI and technology-related queries, including:

AI tools
Machine learning
Generative AI
LLM tutorials
AI automation
Python AI

Each result provides information such as:

Channel name
Channel ID
Platform
Profile URL

YouTube Channel ID is used as the unique creator identifier to prevent duplicate records.

Example
python main.py --target 150
📊 Data Enrichment

After discovery, creator profiles are enriched with additional information.

Field	Description
Channel Name	Creator/channel name
Channel ID	Unique YouTube identifier
Platform	YouTube
Profile URL	Creator profile
Subscribers	Subscriber count
Engagement Rate	Estimated engagement metric
Category	AI/Technology classification
Content Themes	Creator content context
Contact Email	Public email if available
📈 Engagement Rate

The system calculates an estimated engagement rate using publicly available interaction data from recent videos.

The metric is used as a qualification signal rather than being treated as an official YouTube-provided metric.

The number of recent videos used during enrichment can be configured.

🎯 Filtering & Classification

The current filtering category is:

AI / Technology Micro-Influencers

The primary micro-influencer criterion is:

5,000 <= subscribers <= 100,000

Additional qualification signals include:

AI/Technology content relevance
Content themes
Engagement rate

Each creator receives one of the following statuses:

Qualified

or:

Rejected

The system also records a filter_reason explaining the decision.

Example
Status: Qualified

Reason:
Creator is within the target follower range and produces
relevant AI/technology content.
📧 Contact Enrichment

The system attempts to identify publicly available contact emails.

If an email cannot be found, the system stores:

Not Found

The system does not guess or generate email addresses.

This prevents fabricated contact information and follows the assignment requirements.

🤖 AI Personalization

Google Gemini is used to generate personalized collaboration messages for qualified creators.

For every qualified creator, the system generates:

Email Collaboration Pitch

Required length:

60–90 words
Instagram DM

Required length:

15–30 words

The personalization uses available creator information such as:

Creator name
Platform
Category
Content themes
Subscriber count

The Gemini prompt instructs the model not to invent information such as:

Recent videos
Audience demographics
Achievements
Brand partnerships
Contact information
💬 Personalized Outreach

The generated email and Instagram DM are dynamically personalized according to the creator's niche and available content context.

For example, an AI automation creator can receive outreach focused on AI automation, while an ML educator can receive messaging focused on machine learning content.

The generated messages are stored in influencers.csv.

✅ Message Validation

Generated messages are automatically validated against the assignment requirements.

Email
60–90 words
Instagram DM
15–30 words

Messages outside the required range are detected before being treated as valid output.

📤 Outreach Sending Layer

The project implements a simulated email sending workflow.

The process is:

Qualified Creator
       ↓
Valid Email?
   ↙       ↘
 No        Yes
 ↓          ↓
Skip    Already Contacted?
             ↙      ↘
           Yes       No
            ↓         ↓
          Skip     Simulate
                      ↓
                    Log

The system:

Selects qualified creators.
Checks for a valid public email.
Retrieves the personalized email.
Checks for previous outreach.
Simulates sending.
Records the result.

Example statuses:

Skipped - email not found
Simulated - ready for review
📱 Instagram DM

The system generates personalized Instagram DMs but does not attempt to bypass Instagram platform restrictions.

The generated DM can be reviewed and manually sent.

This demonstrates the personalization workflow while respecting platform restrictions.

🔁 Duplicate Prevention

The outreach database uses the combination of:

campaign_id + channel_id

to identify a unique outreach record.

Before an outreach attempt, the system checks whether the creator has already been contacted.

This prevents duplicate outreach within the same campaign.

🗄️ Outreach Tracking

SQLite is used for persistent outreach tracking.

The database records:

Campaign ID
Channel ID
Influencer
Email
Message generated
Sent status
Timestamp
Status
Error information

Database:

data/outreach.db

The database can also be exported as:

data/outreach_tracker.csv

Example statuses include:

Skipped - email not found
Simulated - ready for review
Sent
Failed
📄 Output Files
Influencer Dataset
data/influencers.csv

Important fields include:

channel_name
channel_id
platform
profile_url
subscribers
engagement_rate
category
content_themes
contact_email
status
filter_reason
email_pitch
instagram_dm
Outreach Tracker
data/outreach_tracker.csv

Contains the outreach status for qualified creators.

🚀 Installation
1. Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd edxso-ai-influencer-outreach
2. Create a virtual environment

Windows:

python -m venv venv
venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
🔐 Environment Variables

Create a .env file in the project root:

YOUTUBE_API_KEY=your_youtube_api_key
GEMINI_API_KEY=your_gemini_api_key

Never commit the .env file to GitHub.

A .env.example file is included as a template.

▶️ Running the Project
Discovery only
python main.py --target 150
Discovery + AI personalization
python main.py --target 150 --personalize
Complete workflow with simulated outreach
python main.py --target 150 --personalize --simulate-send

The --simulate-send option does not send real emails.

🧪 Example Run

A typical workflow looks like:

Discovered 150 unique creators

Qualified 22 / 150

Generated personalized messages

Simulated outreach:
- Skipped - email not found
- Simulated - ready for review

Saved dataset to:
data/influencers.csv

Saved outreach tracker to:
data/outreach_tracker.csv

The exact number of qualified creators may vary between runs because API search results and publicly available creator data can change.

⚠️ Limitations
YouTube API

The system is limited to information exposed through the YouTube Data API and publicly available creator information.

Contact Information

Many creators do not publicly expose an email address. These records are stored as:

Not Found

rather than being guessed.

Engagement Rate

The engagement rate is an estimated metric based on publicly available video interaction data.

Instagram

Instagram DM automation is intentionally not implemented through unauthorized methods.

Gemini API

Gemini API rate limits can affect personalization throughput, especially when using free-tier API access.

The personalization layer is modular so another LLM provider can be integrated later.

📈 Scalability

The current architecture is modular and can be extended beyond the initial test run.

Potential improvements include:

Instagram and TikTok integrations
Asynchronous API processing
Batch LLM requests
Queue-based processing
PostgreSQL instead of SQLite
Gmail API integration
CRM integration
Automated response tracking
Campaign analytics dashboard
Advanced creator ranking
Audience demographic analysis

The discovery layer can also be extended to other niches such as:

Fitness
Beauty
Fashion
Fintech
Gaming
Parenting
Lifestyle
Crypto
Technology
🧠 Engineering Decisions
Why YouTube Data API?

It provides structured creator and channel information without requiring unauthorized scraping.

Why Channel ID for deduplication?

Channel names are not guaranteed to be unique. YouTube Channel IDs provide a stable unique identifier.

Why Gemini?

The assignment requires LLM-based personalization but does not mandate a specific provider. Gemini was selected as the LLM provider and integrated as a modular personalization component.

Why SQLite?

SQLite provides persistent local storage without requiring an external database server, making it suitable for this prototype.

Why simulated sending?

It demonstrates the complete outreach workflow without accidentally sending real emails during testing.

🔒 Data & Security

The project follows these principles:

API keys are stored in environment variables.
API keys are not committed to GitHub.
Only publicly available contact information is used.
Email addresses are never guessed.
Instagram restrictions are not bypassed.
Email sending defaults to simulation.
📋 Assignment Requirement Coverage
Requirement	Implementation
50+ influencers	YouTube API discovery
Micro-influencer filtering	5K–100K subscriber range
Category filtering	AI / Technology
Classification	Qualified / Rejected
Rejection reason	filter_reason
Profile enrichment	Metrics + content + contact
Contact email	Public email enrichment
Missing email handling	Not Found
AI personalization	Google Gemini
Email pitch	60–90 words
Instagram DM	15–30 words
Message validation	Automated validator
Sending layer	Simulated email
Duplicate prevention	SQLite
Outreach tracker	SQLite + CSV
Error handling	API/data/send failures
Documentation	README
📸 Demo

The project can be demonstrated through:

YouTube creator discovery output
influencers.csv
Personalized email and Instagram DM
Simulated email output
outreach_tracker.csv
SQLite outreach records
👨‍💻 Author

Aayush Maan

Built as part of the EDXSO AI Engineer Intern Assignment.
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e
