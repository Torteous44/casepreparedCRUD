from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
import secrets
import time
from datetime import datetime, timedelta
import os
import logging
from fastapi import APIRouter, Query, Path, HTTPException, status, Body
from pydantic import BaseModel

# We're not importing the authentication dependencies as these will be public endpoints
from app.db.session import get_db
from app.services import credential as credential_service

router = APIRouter()
logger = logging.getLogger(__name__)

# Hardcoded demo interview templates
DEMO_TEMPLATES = {
    "market-entry": {
        "id": "11111111-1111-1111-1111-111111111111",
        "case_type": "Market Entry",
        "lead_type": "Interviewer-led",
        "difficulty": "Medium",
        "company": "CoffeeChain",
        "industry": "Food & Beverage",
        "title": "CoffeeChain Market Entry Strategy",
        "description_short": "Help CoffeeChain decide if they should enter the European market with their premium coffee products.",
        "description_long": "CoffeeChain is a US-based premium coffee chain looking to expand internationally. They're considering entering the European market but are unsure about the market dynamics, competition, and potential profitability. Your task is to assess if this is a good strategic move.",
        "image_url": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "duration": 30,
        "questions": [
		{
			"number": 1,
			"title": "Opening",
			"prompt": (
				"<prompt>\n"
				"Question #1 - Opening\n"
				"<caseprompt>\n"
				"You are an interviewer for McKinsey and Company conducting a case interview. "
				"Introduce yourself as an interviewer for McKinsey, then read the following prompt:\n"
				"\"The pandemic-induced collapse in oil prices sharply reduced profitability of Premier Oil, "
				"a major UK-based offshore upstream oil and gas producer. Premier Oil operates rigs in seven areas "
				"in the North Sea. The CEO has brought your team in to design a profitability improvement plan.\"\n"
				"\n<question prompt>\n"
				"You are in the opening stage of the interview. You are to answer any clarifying questions regarding the prompt. "
				"The candidate is expected to follow these steps:\n"
				"1) Restate the prompt: Candidates should restate the prompt to ensure alignment with the interviewer.\n"
				"2) Add colors (optional): Candidates can react to the prompt with quick thoughts demonstrating business acumen, e.g.:\n"
				"   • \"It makes sense as the drop in travel and slowed economic growth during the pandemic led to lower demand for fuel.\"\n"
				"   • \"Profitability issues might be even more challenging in the future as renewables and e-mobility gain prominence.\"\n"
				"   • \"Interesting problem, especially given the unfavorable macrotrend as low-cost oil reserves are running out, "
				"and I'd imagine that oil extraction costs will only increase in the future.\"\n"
				"3) Candidates ask 2-3 questions: It is common for candidates to ask 2-3 clarifying questions before designing their framework. "
				"Typical questions include:\n"
				"   • Geography of client's operations/sales\n"
				"   • Financial goal\n"
				"   • Business model of the client\n"
				"4) Ask for a moment to structure: Candidates typically ask for a couple of minutes to structure their approach. "
				"Sometimes during interviewer-driven cases, interviewers ask the first question, and then the candidate takes time to build their framework.\n"
				"\n<interview context>\n"
				"Provide this additional information to the candidate only upon request:\n"
				"   • The client has assets only in the North Sea and doesn't plan to adjust its asset portfolio.\n"
				"   • The profitability for 2020 was -12% (losses), which was common in the industry that year.\n"
				"   • There is no specific goal to improve profitability.\n"
				"   • The client is an independent oil and gas company owned by a wide variety of strategic investors.\n"
				"</prompt>"""
			)
		},
		{
			"number": 2,
			"title": "Initial Structuring",
			"prompt": (
				"<prompt>\n"
				"Question #2:\n"
				"<caseprompt>\n"
				"You are an interviewer for McKinsey and Company conducting a case interview. "
				"Be critical of answers and guide the interviewee slowly to the structure provided, without giving them the answer.\n"
				"This is the context for the interview:\n"
				"\"Our client for this case interview is Premier Oil. The pandemic-induced collapse in oil prices sharply reduced profitability "
				"of Premier Oil, a major UK-based offshore upstream oil and gas producer. Premier Oil operates rigs in seven areas in the North Sea. "
				"The CEO has brought your team in to design a profitability improvement plan.\"\n"
				"\n<question prompt>\n"
				"You are on the first question in the interview. Read the following question in quotations aloud:\n"
				"\"What factors would you consider to work on this problem?\"\n"
				"The candidate is expected to follow these steps:\n"
				"1) Do horizontal presentation: Start with a 15-second big-picture overview.\n"
				"2) Key points: Ensure the candidate covers all key points typical for a profitability case structure:\n"
				"   a) Profitability and analysis (Revenue and cost structures)\n"
				"   b) Business Model (Client segments, product portfolio)\n"
				"   c) External factors (Growth, competition, typical margin)\n"
				"3) Add stories (optional): Candidates can incorporate 2-3 stories into their structure presentation to avoid a cookie-cutter approach:\n"
				"   a) \"It's a capex-heavy business, so economies of scale are crucial.\"\n"
				"   b) \"Crude oil is a commodity highly dependent on global markets, so we don't determine our pricing strategy much.\"\n"
				"   c) \"Offshore platforms are likely subject to strict environmental regulation, which might manifest in higher costs.\"\n"
				"4) Finish with a question: At the end of the structure presentation, it is helpful for the candidate to show they can drive the team forward and prioritize by asking a question.\n"
				"\n<interview context>\n"
				"This is a potential example of how a candidate may structure their approach. Use this as an example only.\n"
				"Factors to consider in this problem:\n"
				"Upstream oil and gas companies:\n"
				"Typical margins:\n"
				"   • Cost structure of several major players [for benchmarking]\n"
				"   • Major trends (apart from pandemic)\n"
				"Premier Oil:\n"
				"Major accounts (clients):\n"
				"   • Product portfolio (crude oil, gas?)\n"
				"   • Operations and value chain (e.g., extraction, pipe transportation)\n"
				"Financial Analysis:\n"
				"   • Revenue analysis\n"
				"   • Cost structure (Fixed costs, variable costs)\n"
				"Profitability Improvement Areas:\n"
				"   • Boost revenue (secure new contracts)\n"
				"   • Reduce costs (Optimize fixed costs, streamline variable costs)\n"
				"</prompt>"""
			)
		},
		{
			"number": 3,
			"title": "Cost Breakdown",
			"prompt": (
				"<prompt>\n"
				"Question #3\n"
				"<caseprompt>\n"
				"You are an interviewer for McKinsey and Company conducting a case interview. "
				"Be critical of answers and guide the interviewee slowly to the structure provided, without giving them the answer.\n"
				"This is the context for the interview:\n"
				"Our client for this case interview is Premier Oil. The pandemic-induced collapse in oil prices sharply reduced profitability "
				"of Premier Oil, a major UK-based offshore upstream oil and gas producer. Premier Oil operates rigs in seven areas in the North Sea. "
				"The CEO has brought your team in to design a profitability improvement plan. Do not read it out loud; jump straight to the question.\n"
				"\n<question prompt>\n"
				"You are on the second question in the interview. Read the following question in quotations aloud:\n"
				"\"Welcome to question #2: Given there is not much Premier Oil can do to increase sales, the manager wants us to focus on costs. "
				"To begin with, what are Premier Oil's major expenses?\"\n"
				"The candidate is expected to follow these steps:\n"
				"1) Do horizontal presentation (optional, but encouraged): Structure brainstorming and offer a 10-second top-down overview, e.g., "
				"\"Great question! I'd like to break down costs into fixed and variable. On the fixed side, I'm thinking about...\"\n"
				"2) Provide at least 4 ideas: Push the candidate to provide at least 4 ideas.\n"
				"3) Add color (optional): To impress the interviewer, candidates can contextualize some of their ideas.\n"
				"\n<interview context>\n"
				"This is just one of many potential ways to brainstorm. Please treat this example only as a reference point. "
				"The candidate is expected to generate at least 4 ideas. If the candidate has generated 4-6 ideas, you are free to conclude the interview.\n"
				"Key costs to consider in this problem:\n"
				"Fixed Costs:\n"
				"   1) Maintenance [this is a capex-heavy business with lots of equipment]\n"
				"   2) R&D [oil companies do a lot of oil exploration]\n"
				"   3) Overhead [central services and management]\n"
				"   4) Energy [to run platform]\n"
				"(Minor fixed Costs: Marketing, Rent - most rigs are likely owned by the client)\n"
				"\nVariable Costs:\n"
				"   5) Labor\n"
				"   6) Supplies to accommodate employees who live on the platform\n"
				"   7) Supplies for oil extraction [if any]\n"
				"   8) Transportation [e.g., pipeline transportation; if paid by volume]\n"
				"</prompt>"""
			)
		},
		{
			"number": 4,
			"title": "Maintenance Cost Drivers",
			"prompt": (
				"<prompt>\n"
				"Question #4\n"
				"<caseprompt>\n"
				"You are an interviewer for McKinsey and Company conducting a case interview. "
				"Be critical of answers and guide the interviewee slowly to the structure provided, without giving them the answer.\n"
				"This is the context for the interview:\n"
				"Our client for this case interview is Premier Oil. The pandemic-induced collapse in oil prices sharply reduced profitability "
				"of Premier Oil, a major UK-based offshore upstream oil and gas producer. Premier Oil operates rigs in seven areas in the North Sea. "
				"The CEO has brought your team in to design a profitability improvement plan. Do not read it out loud; jump straight to the question.\n"
				"\n<question prompt>\n"
				"You are on the first question in the interview. Read the following question in quotations aloud:\n"
				"\"Welcome back, let's move on to question #3: Let's talk about the maintenance costs now. "
				"We've learned that they have been increasing for Premier Oil's offshore platforms. What might be the reasons behind it?\"\n"
				"The candidate is expected to follow these steps:\n"
				"1) Do horizontal presentation (optional, but encouraged): Structure brainstorming and offer a 10-second top-down overview, e.g., "
				"\"Sure, I'll be glad to look into that. I'm thinking about maintenance costs through the lens of scheduled/routine maintenance and reactive/emergency maintenance. "
				"On the scheduled one, I can see...\"\n"
				"2) Provide at least 4 ideas: Push the candidate to provide at least 4 ideas. If they are not providing sufficient ideas, ask again for more detail.\n"
				"3) Add color (optional): To impress the interviewer, candidates can contextualize some of their ideas (examples seen in [] in interview context).\n"
				"\n<interview context>\n"
				"This is just one of many potential ways to brainstorm. Please treat this example only as a reference point. "
				"The candidate is expected to generate at least 4 ideas. If the candidate has generated 4-6 ideas, you are free to conclude the interview.\n"
				"Key cost reasons to consider in this problem:\n"
				"Routine scheduled maintenance:\n"
				"   Higher frequency:\n"
				"   • Aging equipment [older machinery requires more frequent maintenance]\n"
				"   • More strict environmental restrictions requiring frequent check-ups [especially after the environmental disaster in Gulf of Mexico where offshore oil rig explored 10 years ago]\n"
				"   • Increasing prices of spare parts\n"
				"   • Growing technicians' salaries\n"
				"   • New equipment that requires more expensive maintenance\n"
				"   • More expansive transportation of spare parts/technicians [helicopters]\n"
				"\nReactive emergency maintenance:\n"
				"   • Poor alert system that led to accidents\n"
				"   • Lack of training on how to maintain equipment, aging equipment\n"
				"   • Decreasing quality of extracted oil which erodes the equipment\n"
				"   • Too long for technicians to arrive from land - a critical machine may fail\n"
				"\nHigher Costs per repair:\n"
				"   • Higher share of expensive equipment that broke down\n"
				"   • Higher share of major accidents [that cause larger damage]\n"
				"</prompt>"""
			)
		}
	]

    },
    "profitability": {
        "id": "22222222-2222-2222-2222-222222222222",
        "case_type": "Profitability",
        "lead_type": "Candidate-led",
        "difficulty": "Hard",
        "company": "TechNow",
        "industry": "Technology",
        "title": "TechNow Profitability Challenge",
        "description_short": "Help TechNow identify why their profits have declined by 30% over the past year.",
        "description_long": "TechNow is a leading technology retailer that has seen a 30% decline in profitability over the past year despite stable revenues. The CEO has hired you to diagnose the causes of this decline and recommend solutions to restore profitability.",
        "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "duration": 35,
        "questions": [
		{
			"number": 1,
			"title": "Opening",
			"prompt": """<prompt>\nQuestion #1 - Opening\n<caseprompt>\nYou are an interviewer for Bain and Company. You are conducting a case interview.\nIntroduce yourself as an interviewer for Bain, then read out the following prompt below in quotations. \n\"Henderson Electric offers industrial air conditioning units, maintenance services and Internet-of- Things (IoT) enabled software to monitor the air conditioning system functionality in real-time. The overall sales are $1B, however the software revenue remains low. The CEO has hired your team to design a revenue growth plan to boost sales of their IoT-enabled software.\"\n\n<question prompt>\nYou are in the opening stage of the interview. \nYou are to answer any clarifying questions regarding the prompt.\nThe candidate is expected to follow these steps:\n\n1) Restate the prompt: Typically the candidates are expected to restate the prompt to make sure they are on the same page with the interviewer\n\n2) Add colors (optional): Candidates can react to the prompt by providing some quick thoughts which will demonstrate candidates' business acumen, e.g.:\n•  "It seems like a market with high switching costs for factories, so they should have really strong reasons to change their software providers"\n•  "It's great to see that our client has large scale, which means they probably enjoy large marketing and R&D budgets to upgrade and promote their software"\n•  "It's an interesting space as due to the global warming the demand for cooling systems might be growing at an accelerated pace. Now, macrotrend towards energy efficiency might boost the demand for monitoring software of air conditioners"\n\n3) Candidates ask 2-3 questions: It is common that candidates ask 2-3 clarifying questions before designing their framework. Typical questions include:\n• Geography of client's operations/sales\n• Financial goal\n• Business model of the client\n\n4) Ask for a moment to structure: Typically candidates ask for a couple of minutes to structure their approach\n• Sometimes during interviewer-driven cases, the interviewers ask the first question and then the candidate takes time to build their framework\n\n<interview context>\nProvide this additional information to the candidate only upon request\n• The client offers all kind of air conditioning units and cooling equipment\n• The software alerts customers on system failure, unusual behavior, and maintenance cycle to reduce repair costs\n• The software is versatile and can work on equipment of other producers too\n• No revenue goals provided\n• The client serves a wide variety of storage facilities and factories - food processing, medicine production, computer chip manufacturing, etc.\n</prompt>"""
		},
		{
			"number": 2,
			"title": "Structuring Low Software Sales Analysis",
			"prompt": """<prompt>\nQuestion #2\n<caseprompt>\nYou are an interviewer for Bain and Company. You are conducting a case interview. Be critical of answers and guide interviewee slowly to the structure provided, without giving them the answer.\n\nThis is the context for the interview, do not read it out loud.\n\"Henderson Electric offers industrial air conditioning units, maintenance services and Internet-of- Things (IoT) enabled software to monitor the air conditioning system functionality in real-time. The overall sales are $1B, however the software revenue remains low. The CEO has hired your team to design a revenue growth plan to boost sales of their IoT-enabled software.\"\n\n<question prompt>\nYou are on the first question in the interview. Read the following question in quotations aloud:\n\"How would you approach analysing the low sales of the client's software and developing recommendations?\"\n\nThe candidate is expected to follow these steps:\n1) Do horizontal presentation: The best practice is to start with a 15-second big-picture overview\n2) Key points: Make sure that the candidate covers all key points typical for a revenue growth case structure:\na) Profitability and analysis (Revenue and cost structures)\nb) Business Model (Client segments, product portfolio)\nc) External factors (Growth, competition, typical margin)\n3) Add stories (optional):\na) "I'd think that monitoring software has likely been around for a while, so this is a mature market and thus its growth rate might be in low single-digit numbers"\nb) "The production of industrial air conditioning systems is likely capex-heavy and requires decent amount of R&D, thus the barriers for entry are fairly high, which makes me believe this is a consolidated space with just a few big-name players"\nc) "Given seemingly limited number of use cases for this software which include reporting and remote control, it's likely commoditized and doesn't provide distinguished differentiation points"\n4) Finish with a question: Ask a prioritization or next step question\n\n<interview context>\nExample structure:\n1) Software for industrial HVAC Equipment\n- Growth rate of the segment\n- Major software providers (incl. market share, positioning)\n- Recent trends in adoption of this software type\n\n2) Henderson Electric\n- Differentiating points of IoT- enabled software\n- Target client groups and their key purchasing decision-making factors\n- Salesforce and its efficiency\n\n3) Analysis of software sales\n- Pricing model (e.g. one-time payment, subscription)\n- Number of clients and growth rate\n- Revenue structure by type of clients\n\n4) Revenue Growth Strategies\n- Marketing strategy\n- Pricing strategy\n- Distribution channels\n- Value proposition\n</prompt>"""
		},
		{
			"number": 3,
			"title": "Growth Strategy Brainstorm",
			"prompt": """<prompt>\nQuestion #3\n<caseprompt>\nYou are an interviewer for Bain and Company. You are conducting a case interview. Be critical of answers and guide interviewee slowly to the structure provided, without giving them the answer.\n\nThis is the context for the interview, do not read it out loud.\n\"Henderson Electric offers industrial air conditioning units, maintenance services and Internet-of- Things (IoT) enabled software to monitor the air conditioning system functionality in real-time. The overall sales are $1B, however the software revenue remains low. The CEO has hired your team to design a revenue growth plan to boost sales of their IoT-enabled software.\"\n\n<question prompt>\nYou are on the second question in the interview. Read the following question in quotations aloud:\n"Welcome back! Here is the second question in the case: Any ideas on how to help Henderson Electric increase the sales of their monitoring software?"\n\nThe candidate is expected to follow these steps:\n1) Optional horizontal structure: "Sure, I'd like to think about four types of revenue growth ideas - first, improving marketing; secondly, optimizing pricing strategy; thirdly, strengthening distribution channels; and finally ensuring strong value proposition"\n\n2) Provide at least 4 ideas\n3) Add color (optional)\n\n<interview context>\nIdeas to explore:\n1) Upgrade marketing strategy\n- Organize more marketing events\n- Publish analytical reports\n- Invest in campaigns and promotions\n\n2) Change pricing\n- Adjust pricing levels to match WTP\n- Bundle software with equipment\n- Offer different monetization models (tiers, free trials)\n\n3) Increase efficiency of distribution\n- Improve Salesforce training and culture\n- Address objections and follow-up rigorously\n\n4) Improve and expand value proposition\n- Customize features\n- Add support services\n- Reinforce QA/tester teams\n</prompt>"""
		},
		{
			"number": 4,
			"title": "Understanding Market Adoption Gap",
			"prompt": """<prompt>\nQuestion #4\n<caseprompt>\nYou are an interviewer for Bain and Company. You are conducting a case interview. Be critical of answers and guide interviewee slowly to the structure provided, without giving them the answer.\n\nThis is the context for the interview, do not read it out loud.\n\"Henderson Electric offers industrial air conditioning units, maintenance services and Internet-of- Things (IoT) enabled software to monitor the air conditioning system functionality in real-time. The overall sales are $1B, however the software revenue remains low. The CEO has hired your team to design a revenue growth plan to boost sales of their IoT-enabled software.\"\n\n<question prompt>\nYou are on the third question in the interview. Read the following question in quotations aloud:\n"Welcome back to question #3 in our interview. Out of 16k large manufacturing facilities in the U.S. only 4k have adopted the software to monitor and manage their air conditioning units. Why don't the rest 12k do the same?"\n\nThe candidate is expected to follow these steps:\n1) Optional horizontal breakdown\n2) Provide at least 4 ideas\n3) Add color (optional)\n\n<interview context>\nFactors to consider:\n1) Financial Reasons\n- High price, high customization costs\n- In-house IT burden\n- Unclear ROI\n\n2) Low Perceived Value\n- Lack of awareness\n- Manual systems working fine\n- Few units on site\n\n3) Risks\n- Locked-in contracts\n- Bugs, usability issues\n- Implementation disruptions\n- Poor vendor support\n- Security and IT concerns\n</prompt>"""
		}
	]

    },
    "merger": {
        "id": "33333333-3333-3333-3333-333333333333",
        "case_type": "Merger & Acquisition",
        "lead_type": "Interviewer-led",
        "difficulty": "Medium",
        "company": "HealthFirst",
        "industry": "Healthcare",
        "title": "HealthFirst Acquisition Decision",
        "description_short": "Help HealthFirst evaluate the potential acquisition of MediTech, a healthcare technology startup.",
        "description_long": "HealthFirst, a major healthcare provider, is considering acquiring MediTech, a promising healthcare technology startup with an innovative patient management platform. Your task is to evaluate whether this acquisition makes strategic and financial sense.",
        "image_url": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "duration": 30,
        "questions": [
		{
			"number": 1,
			"title": "Opening",
			"prompt": """<prompt>\nQuestion #1 - Opening\n<caseprompt>\nYou are an interviewer for Boston Consulting Group. You are conducting a case interview.\n\nIntroduce yourself as an interviewer for BCG, then read out the following prompt below in quotations. \n\"Betacer is a major U.S. electronics manufacturer that offers laptop and desktop PCs, tablets, smartphones, monitors, projectors and cloud solutions for home users, business and government. Given low or negative growth rate in various segments of the electronics industry, Betacer is looking for expansion opportunities and is considering entering the U.S. video- game market. They've reached out to you to get your advice on whether this is a wise idea.\"\n\n<question prompt>\nYou are in the opening stage of the interview. \nYou are to answer any clarifying questions regarding the prompt.\nThe candidate is expected to follow these steps:\n\n1) Restate the prompt: Typically the candidates are expected to restate the prompt to make sure they are on the same page with the interviewer\n\n2) Add colors (optional): Candidates can react to the prompt by providing some quick thoughts which will demonstrate candidates' business acumen, e.g.:\n"At first glance this choice makes sense, as the pandemic likely positively affected the video-game market. Driven by anxieties and social isolation people turned to video-games to entertain themselves, fill their time and connect with friends"\n•  "Betacer might expect some marketing and distribution synergies as they produce smartphones and PC, major video-gaming platforms"\n•  "Great to see that Betacer is a big-name player as they likely enjoy high brand awareness and deep marketing pockets which they might leverage for their market expansion"\n\n3) Candidates ask 2-3 questions: It is common that candidates ask 2-3 clarifying questions before designing their framework. Typical questions include:\n• Geography of client's operations/sales\n• Financial goal\n• Business model of the client\n\n4) Ask for a moment to structure: Typically candidates ask for a couple of minutes to structure their approach\n• Sometimes during interviewer-driven cases, the interviewers ask the first question and then the candidate takes time to build their framework\n\n<interview context>\nProvide this additional information to the candidate only upon request\n• Betacer would like to payback their investment within 2 years after the market entry\n• Betacer plans to target the mass market, not hardcore gamers\n• The client would like to focus on the U.S. video-game market\n• It's a $175B global market that sky- rocketed in 2020 (see Appendix 1)\n• It's a fragmented space with a lot of big-name players (see Appendix 2)\n• The U.S. video-game market was at $41B in 2020 (see Appendix 3)\n• Betacer doesn't want to explore other growth opportunities but to focus on this market expansion\n</prompt>"""
		},
		{
			"number": 2,
			"title": "Market Entry Assessment",
			"prompt": """<prompt>\nQuestion #2\n<caseprompt>\nYou are an interviewer for Boston Consulting Group. You are conducting a case interview. Be critical of answers and guide interviewee slowly to the structure provided, without giving them the answer.\n\nThis is the context for the interview, do not read it out loud.\n\"Betacer is a major U.S. electronics manufacturer that offers laptop and desktop PCs, tablets, smartphones, monitors, projectors and cloud solutions for home users, business and government. Given low or negative growth rate in various segments of the electronics industry, Betacer is looking for expansion opportunities and is considering entering the U.S. video- game market. They've reached out to you to get your advice on whether this is a wise idea.\"\n\n<question prompt>\nYou are on the first question in the interview. Read the following question in quotations aloud:\n"Question #1: What factors would you consider to suggest whether Betacer should enter the video-game market?"\n\nThe candidate is expected to follow these steps:\n1) Do horizontal presentation: The best practice is to start with a 15-second big-picture overview\n2) Key points: Make sure that the candidate covers all key points typical for a market entry case structure:\n• Market assessment: Size, growth, competition, typical profitability\n• Business model: Client segments, product portfolio\n• Financial analysis: Expected profitability, expected capex, investment criteria \n\n3) Add stories (optional):\n"My running hypothesis is that this is an enormous market as video-gaming is one of the major entertainment ways nowadays, and is part of the lifestyle for many"\n"This is likely a capex-intensive and thus volume-driven business with high R&D costs and thus number of users might be a key success factor"\n"Barriers for entry for some video-game segments might be low. For example, smartphone games are sold through a transparent well-developed app stores like Apple and Google Play that provide direct access to end users"\n\n4) Finish with a question\n\n<interview context>\nFactors to consider:\n• Video game market: size and growth, major video game producers, typical profitability, substitutes \n• Betacer: Target customer segments, Offerings (video games, platforms, etc), Planned distribution channels \n• Financial Assessment: Expected profitability, forecasted revenue and growth, market share, costs, required capex, payback period\n• Potential market entry risks: Market specific, financial, operational\n</prompt>"""
		},
		{
			"number": 3,
			"title": "Customer Adoption Drivers",
			"prompt": """<prompt>\nQuestion #3:\n<caseprompt>\nYou are an interviewer for Boston Consulting Group. You are conducting a case interview. Be critical of answers and guide interviewee slowly to the structure provided, without giving them the answer.\n\nThis is the context for the interview, do not read it out loud.\n\"Betacer is a major U.S. electronics manufacturer that offers laptop and desktop PCs, tablets, smartphones, monitors, projectors and cloud solutions for home users, business and government. Given low or negative growth rate in various segments of the electronics industry, Betacer is looking for expansion opportunities and is considering entering the U.S. video- game market. They've reached out to you to get your advice on whether this is a wise idea.\"\n\n<question prompt>\nYou are on the second question in the interview. Read the following question in quotations aloud:\n"Welcome back, here is question #2: What factors would you consider to suggest whether Betacer should enter the video-game market?"\n\nThe candidate is expected to follow these steps:\n1) Do horizontal presentation (optional): "Sure, I'd like to think about purchasing reasons through four areas - marketing/perception, pricing, distribution, and value proposition. On the marketing side, the reasons might be..."\n2) Provide at least 4 ideas\n3) Add color (optional)\n\n<interview context>\nIdeas to explore:\n• Great perception: brand awareness, social pressure, peer recommendations, high ratings\n• Appealing pricing: free trials, affordable pricing, compatibility with existing devices\n• Convenient distribution: easy app store/online access\n• Strong value proposition: popular genres, platform compatibility, social/interactive elements, novelty\n</prompt>"""
		},
		{
			"number": 4,
			"title": "Synergy Opportunities",
			"prompt": """<prompt>\nQuestion #4:\n<caseprompt>\nYou are an interviewer for Boston Consulting Group. You are conducting a case interview. Be critical of answers and guide interviewee slowly to the structure provided, without giving them the answer.\n\nThis is the context for the interview, do not read it out loud.\n\"Betacer is a major U.S. electronics manufacturer that offers laptop and desktop PCs, tablets, smartphones, monitors, projectors and cloud solutions for home users, business and government. Given low or negative growth rate in various segments of the electronics industry, Betacer is looking for expansion opportunities and is considering entering the U.S. video- game market. They've reached out to you to get your advice on whether this is a wise idea.\"\n\n<question prompt>\nYou are on the third question in the interview. Read the following question in quotations aloud:\n"Welcome back, let's jump into question #3: What synergies might Betacer capture by entering the video-game market?"\n\nThe candidate is expected to follow these steps:\n1) Do horizontal presentation (optional): "Great question. I'd like to break it down into revenue synergies and cost synergies"\n2) Provide at least 4 ideas\n3) Add color (optional)\n\n<interview context>\nRevenue Synergies:\n• Leverage distribution infrastructure\n• Bundle hardware and games\n• Use brand awareness and co-marketing\n\nCost Synergies:\n• Shared overhead and services\n• Volume discounts through larger sales partnerships\n</prompt>"""
		}
	]

    }
}

# Demo interview IDs for tracking "sessions"
DEMO_INTERVIEWS = {
    "market-entry": "44444444-4444-4444-4444-444444444444",
    "profitability": "55555555-5555-5555-5555-555555555555",
    "merger": "66666666-6666-6666-6666-666666666666"
}

# In-memory storage for demo session progress (this would be in a database in production)
# Format: {"interview_id": {"current_question": 1, "questions_completed": []}}
DEMO_PROGRESS = {}

@router.get("/templates", response_model=List[Dict[str, Any]])
def list_demo_templates() -> Any:
    """
    List all available demo interview templates
    """
    templates = []
    for case_type, template in DEMO_TEMPLATES.items():
        templates.append({
            "id": template["id"],
            "case_type": template["case_type"],
            "lead_type": template["lead_type"],
            "difficulty": template["difficulty"],
            "company": template["company"],
            "industry": template["industry"],
            "title": template["title"],
            "description_short": template["description_short"],
            "description_long": template["description_long"],
            "image_url": template["image_url"],
            "duration": template["duration"]
        })
    return templates

@router.get("/templates/{template_id}", response_model=Dict[str, Any])
def get_demo_template(template_id: str) -> Any:
    """
    Get a specific demo template by ID
    """
    for case_type, template in DEMO_TEMPLATES.items():
        if template["id"] == template_id:
            return template
    
    raise HTTPException(
        status_code=404,
        detail="Demo template not found"
    )

@router.get("/interviews/{case_type}", response_model=Dict[str, Any])
def get_demo_interview(case_type: str = Path(..., description="Demo case type: market-entry, profitability, or merger")) -> Any:
    """
    Get a demo interview by case type
    """
    if case_type not in DEMO_TEMPLATES:
        raise HTTPException(
            status_code=404,
            detail=f"Demo interview not found. Available options: {', '.join(DEMO_TEMPLATES.keys())}"
        )
    
    template = DEMO_TEMPLATES[case_type]
    interview_id = DEMO_INTERVIEWS[case_type]
    
    # Initialize or get progress data
    if interview_id not in DEMO_PROGRESS:
        DEMO_PROGRESS[interview_id] = {
            "current_question": 1,
            "questions_completed": [],
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "status": "in-progress"
        }
    
    return {
        "id": interview_id,
        "template_id": template["id"],
        "status": DEMO_PROGRESS[interview_id]["status"],
        "progress_data": {
            "current_question": DEMO_PROGRESS[interview_id]["current_question"],
            "questions_completed": DEMO_PROGRESS[interview_id]["questions_completed"]
        },
        "started_at": DEMO_PROGRESS[interview_id]["started_at"],
        "completed_at": DEMO_PROGRESS[interview_id]["completed_at"],
        "template": template
    }

@router.get("/turn-credentials", response_model=Dict[str, Any])
def get_demo_turn_credentials() -> Any:
    """
    Get TURN server credentials for WebRTC in demo mode
    """
    try:
        # Create a guest username for the demo
        username = f"demo-user-{secrets.token_hex(4)}"
        
        # Use the same credential generation as the main app but with the demo username
        return credential_service.generate_turn_credentials(username=username)
    except Exception as e:
        logger.error(f"Error generating demo TURN credentials: {str(e)}")
        
        # Provide fallback TURN credentials that can work in many scenarios
        # This is not ideal but allows the demo to function when Twilio is unavailable
        logger.info("Using fallback TURN credentials for demo")
        current_time = int(time.time())
        expiration = current_time + 86400  # 24 hours
        
        return {
            "username": username,
            "ttl": 86400,
            "expiration": expiration,
            "ice_servers": [
                {
                    "urls": [
                        "stun:stun.l.google.com:19302",
                        "stun:stun1.l.google.com:19302",
                        "stun:stun2.l.google.com:19302"
                    ]
                }
            ]
        }

@router.get("/interviews/{case_type}/questions/{question_number}/token", response_model=Dict[str, Any])
def get_demo_question_token(
    case_type: str = Path(..., description="Demo case type: market-entry, profitability, or merger"),
    question_number: int = Path(..., ge=1, le=4, description="Question number (1-4)"),
    ttl: int = Query(3600, ge=300, le=7200, description="Token time-to-live in seconds")
) -> Any:
    """
    Generate a token for a specific demo interview question
    """
    if case_type not in DEMO_TEMPLATES:
        raise HTTPException(
            status_code=404,
            detail=f"Demo interview not found. Available options: {', '.join(DEMO_TEMPLATES.keys())}"
        )
    
    template = DEMO_TEMPLATES[case_type]
    interview_id = DEMO_INTERVIEWS[case_type]
    
    # Initialize progress tracking if not exists
    if interview_id not in DEMO_PROGRESS:
        DEMO_PROGRESS[interview_id] = {
            "current_question": 1,
            "questions_completed": [],
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "status": "in-progress"
        }
    
    # Check if the interview is in progress
    if DEMO_PROGRESS[interview_id]["status"] != "in-progress":
        raise HTTPException(
            status_code=400,
            detail="Demo interview is not in progress"
        )
    
    # Check if the requested question is available
    current_question = DEMO_PROGRESS[interview_id]["current_question"]
    if question_number > current_question:
        raise HTTPException(
            status_code=400,
            detail="Cannot access future questions. Complete the current question first."
        )
    
    # Get the specific question
    try:
        question = template["questions"][question_number - 1]
    except IndexError:
        raise HTTPException(
            status_code=404,
            detail=f"Question number {question_number} not found"
        )
    
    # Build customized instructions for this specific demo question
    total_questions = len(template['questions'])
    instructions = f"""You are an interviewer for a {template['case_type']} case interview about {template['company']} in the {template['industry']} industry.

CASE CONTEXT: {template['description_long']}

QUESTION {question_number}/{total_questions}: {question['title']}
{question['prompt']}

INTERVIEW GUIDELINES:
• Guide the candidate professionally through this question
• Provide hints only when the candidate is stuck
• Let the candidate work through the problem independently
• Give constructive feedback on their approach
"""
    
    # Get the OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OpenAI API key not found in environment variables")
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured"
        )
    
    # Try to generate ephemeral key through the credential service first
    try:
        ephemeral_key = credential_service.generate_openai_ephemeral_key(
            instructions=instructions,
            ttl=ttl,
            voice="alloy"  # Using a consistent voice for demos
        )
        
        # Add custom metadata
        session_token = {
            "id": f"demo_sess_{interview_id}_{question_number}",
            "interviewId": str(interview_id),
            "userId": "demo-user",
            "questionNumber": question_number,
            "expiresAt": datetime.fromtimestamp(int(time.time()) + ttl).isoformat(),
            "ttl": ttl,
            "instructions": instructions,
            "realtimeSession": ephemeral_key
        }
        
        return session_token
        
    except Exception as e:
        logger.error(f"Error using credential service for ephemeral key: {str(e)}")
        logger.info("Trying direct OpenAI API call for ephemeral key")
        
        # Direct implementation of OpenAI realtime API call
        try:
            import requests
            
            url = "https://api.openai.com/v1/realtime/sessions"
            headers = {
                "Authorization": f"Bearer {openai_api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare the request payload
            payload = {
                "model": "gpt-4o-mini-realtime-preview",
                "modalities": ["audio", "text"],
                "instructions": instructions,
                "voice": "alloy",
                "temperature": 0.8,
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "max_response_output_tokens": "inf",
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 200
                }
            }
            
            # Make the API call
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            # Check for success
            if response.status_code in [200, 201]:
                ephemeral_key = response.json()
                
                # Return success with ephemeral key
                return {
                    "id": f"demo_sess_{interview_id}_{question_number}",
                    "interviewId": str(interview_id),
                    "userId": "demo-user",
                    "questionNumber": question_number,
                    "expiresAt": datetime.fromtimestamp(int(time.time()) + ttl).isoformat(),
                    "ttl": ttl,
                    "instructions": instructions,
                    "realtimeSession": ephemeral_key
                }
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                raise Exception(f"OpenAI API error: {response.status_code}")
                
        except Exception as api_error:
            logger.error(f"Direct OpenAI API call failed: {str(api_error)}")
            # Continue to use fallback below
        
        # Last resort fallback with direct API key
        token = secrets.token_hex(32)
        expiration = datetime.utcnow() + timedelta(seconds=ttl)
        expiration_timestamp = int(expiration.timestamp())
        
        return {
            "id": f"demo_sess_{interview_id}_{question_number}",
            "apiKey": openai_api_key,
            "instructions": instructions,
            "interviewId": str(interview_id),
            "userId": "demo-user",
            "questionNumber": question_number,
            "expiresAt": expiration.isoformat(),
            "ttl": ttl,
            "client_secret": {
                "value": token,
                "expires_at": expiration_timestamp
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating demo question token: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate session token"
        )

class DemoQuestionComplete(BaseModel):
    case_type: str
    question_number: int

@router.post("/interviews/complete-question", response_model=Dict[str, Any])
def complete_demo_question(body: DemoQuestionComplete = Body(...)) -> Any:
    """
    Mark a demo question as complete and advance to the next question
    """
    case_type = body.case_type
    question_number = body.question_number
    
    if case_type not in DEMO_TEMPLATES:
        raise HTTPException(
            status_code=404,
            detail=f"Demo interview not found. Available options: {', '.join(DEMO_TEMPLATES.keys())}"
        )
    
    interview_id = DEMO_INTERVIEWS[case_type]
    
    # Initialize progress tracking if not exists
    if interview_id not in DEMO_PROGRESS:
        DEMO_PROGRESS[interview_id] = {
            "current_question": 1,
            "questions_completed": [],
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "status": "in-progress"
        }
    
    progress_data = DEMO_PROGRESS[interview_id]
    
    # Check if interview is in progress
    if progress_data["status"] != "in-progress":
        raise HTTPException(
            status_code=400,
            detail="Demo interview is not in progress"
        )
    
    # Validate that we're completing the current question
    if question_number != progress_data["current_question"]:
        raise HTTPException(
            status_code=400,
            detail="Can only complete the current question"
        )
    
    # Mark the question as completed
    if question_number not in progress_data["questions_completed"]:
        progress_data["questions_completed"].append(question_number)
    
    # Advance to next question
    next_question = question_number + 1
    progress_data["current_question"] = next_question if next_question <= 4 else 4
    
    # Check if all questions are completed
    if len(progress_data["questions_completed"]) >= 4 and all(q in progress_data["questions_completed"] for q in range(1, 5)):
        progress_data["status"] = "completed"
        progress_data["completed_at"] = datetime.utcnow().isoformat()
    
    # Save progress
    DEMO_PROGRESS[interview_id] = progress_data
    
    template = DEMO_TEMPLATES[case_type]
    
    # Return the updated interview
    return {
        "id": interview_id,
        "template_id": template["id"],
        "status": progress_data["status"],
        "progress_data": {
            "current_question": progress_data["current_question"],
            "questions_completed": progress_data["questions_completed"]
        },
        "started_at": progress_data["started_at"],
        "completed_at": progress_data["completed_at"],
        "template": template
    }

@router.post("/reset/{case_type}", response_model=Dict[str, Any])
def reset_demo_interview(case_type: str = Path(..., description="Demo case type to reset")) -> Any:
    """
    Reset a demo interview's progress
    """
    if case_type not in DEMO_TEMPLATES:
        raise HTTPException(
            status_code=404,
            detail=f"Demo interview not found. Available options: {', '.join(DEMO_TEMPLATES.keys())}"
        )
    
    interview_id = DEMO_INTERVIEWS[case_type]
    
    # Reset progress data
    DEMO_PROGRESS[interview_id] = {
        "current_question": 1,
        "questions_completed": [],
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "status": "in-progress"
    }
    
    template = DEMO_TEMPLATES[case_type]
    
    return {
        "id": interview_id,
        "template_id": template["id"],
        "status": "in-progress",
        "progress_data": {
            "current_question": 1,
            "questions_completed": []
        },
        "started_at": DEMO_PROGRESS[interview_id]["started_at"],
        "completed_at": None,
        "message": f"Demo interview {case_type} has been reset"
    }

@router.get("/direct-token/{case_type}/{question_number}", response_model=Dict[str, Any])
def get_direct_token(
    case_type: str = Path(..., description="Demo case type: market-entry, profitability, or merger"),
    question_number: int = Path(..., ge=1, le=4, description="Question number (1-4)"),
    ttl: int = Query(3600, ge=300, le=7200, description="Token time-to-live in seconds")
) -> Any:
    """
    Generate a direct OpenAI token with minimal processing - designed for frontend compatibility
    """
    logger.info(f"Direct token requested for case_type={case_type}, question={question_number}, ttl={ttl}")
    
    # Special handling for "442" and any invalid case types - map them to "market-entry"
    if case_type not in DEMO_TEMPLATES:
        logger.warning(f"Invalid case type '{case_type}' requested, falling back to 'market-entry'")
        case_type = "market-entry"
    
    template = DEMO_TEMPLATES[case_type]
    interview_id = DEMO_INTERVIEWS[case_type]
    
    # Get the specific question (with bounds checking)
    question_index = max(0, min(question_number - 1, len(template["questions"]) - 1))
    question = template["questions"][question_index]
    logger.info(f"Using question: {question['title']}")
    
    # Build customized instructions for this specific demo question
    total_questions = len(template['questions'])
    instructions = f"""You are an interviewer for a {template['case_type']} case interview about {template['company']} in the {template['industry']} industry.

CASE CONTEXT: {template['description_long']}

QUESTION {question_number}/{total_questions}: {question['title']}
{question['prompt']}

INTERVIEW GUIDELINES:
• Guide the candidate professionally through this question
• Provide hints only when the candidate is stuck
• Let the candidate work through the problem independently
• Give constructive feedback on their approach
"""
    
    # Get the OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OpenAI API key not found in environment variables")
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured"
        )
    
    # Direct implementation of OpenAI realtime API call
    try:
        import requests
        
        url = "https://api.openai.com/v1/realtime/sessions"
        headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare the request payload
        payload = {
            "model": "gpt-4o-mini-realtime-preview",
            "modalities": ["audio", "text"],
            "instructions": instructions,
            "voice": "alloy",
            "temperature": 0.8,
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "max_response_output_tokens": "inf",
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 200
            }
        }
        
        # Make the API call
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        # Check for success
        if response.status_code in [200, 201]:
            session_data = response.json()
            
            # Create a token object that matches what the frontend expects
            token = session_data.get("client_secret", {}).get("value")
            if not token:
                logger.error(f"Unable to extract token from response: {session_data}")
                raise HTTPException(
                    status_code=500,
                    detail="Invalid response format from OpenAI"
                )
            
            # Return a simplified response with just the token
            return {
                "token": token,
                "expires_at": session_data.get("client_secret", {}).get("expires_at")
            }
        else:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"OpenAI API error: {response.text}"
            )
            
    except Exception as e:
        logger.error(f"Error generating OpenAI token: {str(e)}")
        
        # Last resort fallback with direct API key
        logger.info("Using fallback token method")
        token = secrets.token_hex(32)
        expiration = int((datetime.utcnow() + timedelta(seconds=ttl)).timestamp())
        
        return {
            "token": token,
            "expires_at": expiration
        } 