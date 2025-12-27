# app/prompts/platform_prompts.py

from app.utils.scoring import scoring_instructions

# --------------------------------------------------
# PLATFORM-SPECIFIC LOGIC BLOCKS
# --------------------------------------------------

WEBSITE_LOGIC = """
Analyze this as a business website.

Create sections such as:
- First Impression & Clarity
- Content Quality
- Trust & Credibility
- SEO & Discoverability
- Conversion Readiness

Focus on:
- Value proposition clarity
- Messaging and copy quality
- CTAs and funnel logic
- SEO basics (structure, intent match)
"""

INSTAGRAM_LOGIC = """
Analyze this as an Instagram brand profile.

Create sections such as:
- Profile Optimization
- Content Strategy
- Engagement & Community
- Growth & Discoverability
- Conversion Readiness

Focus on:
- Bio clarity and keywords
- Reel vs post mix
- Engagement quality
- CTA usage (bio link, DMs)
"""

LINKEDIN_PROFILE_LOGIC = """
Analyze this as a personal LinkedIn profile.

Create sections such as:
- Positioning & Headline
- Content & Thought Leadership
- Credibility Signals
- Network & Visibility
- Inbound Opportunity Readiness

Focus on:
- Professional clarity
- Authority building
- Consistency of posting
"""

LINKEDIN_COMPANY_LOGIC = """
Analyze this as a LinkedIn company page.

Create sections such as:
- Brand Positioning
- Content Strategy
- Employer & Brand Trust
- Visibility & Reach
- Lead & Interest Generation
"""

X_LOGIC = """
Analyze this as an X (Twitter) profile.

Create sections such as:
- Voice & Positioning
- Content & Opinions
- Engagement Strategy
- Network Quality
- Influence & Reach

Focus on:
- Thought leadership
- Reply behavior
- Content consistency
"""

YOUTUBE_LOGIC = """
Analyze this as a YouTube channel.

Create sections such as:
- Channel Positioning
- Content Quality & Hooks
- Consistency & Format
- Discoverability
- Audience Conversion

Focus on:
- Thumbnails and titles
- Retention logic
- CTA usage
"""

REDDIT_PROFILE_LOGIC = """
Analyze this as a Reddit user profile.

Create sections such as:
- Authenticity & Behavior
- Contribution Quality
- Community Interaction
- Trust Signals
- Promotion Risk
"""

REDDIT_COMMUNITY_LOGIC = """
Analyze this as a Reddit community (subreddit).

Create sections such as:
- Community Purpose
- Engagement Health
- Content Quality
- Moderation Quality
- Growth Potential
"""

# --------------------------------------------------
# PROMPT BUILDER
# --------------------------------------------------

def get_platform_prompt(asset_type: str, url: str, content: str) -> str:
    base_voice = """
You are a senior marketing analyst advising a real business owner.

Speak like a human consultant:
- Calm
- Honest
- Practical
- Slightly opinionated

No emojis. No hype. No generic AI tone.
"""

    platform_logic = {
        "website": WEBSITE_LOGIC,
        "instagram_profile": INSTAGRAM_LOGIC,
        "linkedin_profile": LINKEDIN_PROFILE_LOGIC,
        "linkedin_company": LINKEDIN_COMPANY_LOGIC,
        "x_profile": X_LOGIC,
        "youtube_channel": YOUTUBE_LOGIC,
        "reddit_profile": REDDIT_PROFILE_LOGIC,
        "reddit_community": REDDIT_COMMUNITY_LOGIC,
    }.get(asset_type, WEBSITE_LOGIC)

    return f"""
{base_voice}

Asset type: {asset_type}
URL: {url}

Extracted content:
{content}

{platform_logic}

Return STRICT JSON in this shape:
{{
  "overview": "string",
  "target_audience": "string",
  "sections": [
    {{
      "id": "string",
      "title": "string",
      "insights": ["string"]
    }}
  ],
  "verdicts": {{
    "marketing": "string",
    "strategic": "string"
  }},
  "score": {{
    "value": number,
    "reasoning": "string"
  }}
}}

{scoring_instructions()}
"""
