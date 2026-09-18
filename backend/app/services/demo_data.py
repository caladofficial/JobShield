import random
from datetime import datetime, timedelta
from typing import List
from app.services.source_adapters import NormalizedJob
from app.models import Source, SourceStatus


DEMO_COMPANIES = [
    {"name": "TechCorp Solutions", "domain": "techcorp.com", "location": "Bangalore"},
    {"name": "DataFlow Inc", "domain": "dataflow.io", "location": "Hyderabad"},
    {"name": "CloudNine Systems", "domain": "cloudnine.tech", "location": "Pune"},
    {"name": "AI Ventures", "domain": "aiventures.ai", "location": "Mumbai"},
    {"name": "DevStack Labs", "domain": "devstack.dev", "location": "Delhi NCR"},
    {"name": "ByteBridge", "domain": "bytebridge.co", "location": "Chennai"},
    {"name": "QuantumSoft", "domain": "quantumsoft.in", "location": "Kolkata"},
    {"name": "NextGen Technologies", "domain": "nextgen.tech", "location": "Ahmedabad"},
    {"name": "ScaleUp Solutions", "domain": "scaleup.solutions", "location": "Gurgaon"},
    {"name": "InnovateLabs", "domain": "innovatelabs.io", "location": "Noida"},
]

DEMO_TITLES = [
    "Software Engineer",
    "Senior Software Engineer",
    "Backend Developer",
    "Full Stack Developer",
    "Frontend Developer",
    "DevOps Engineer",
    "Data Scientist",
    "Machine Learning Engineer",
    "Product Manager",
    "QA Engineer",
    "Site Reliability Engineer",
    "Security Engineer",
    "Mobile Developer",
    "Engineering Manager",
    "Technical Lead",
]

DEMO_LOCATIONS = [
    "Bangalore, Karnataka",
    "Hyderabad, Telangana",
    "Pune, Maharashtra",
    "Mumbai, Maharashtra",
    "Delhi NCR",
    "Chennai, Tamil Nadu",
    "Kolkata, West Bengal",
    "Gurgaon, Haryana",
    "Noida, Uttar Pradesh",
    "Ahmedabad, Gujarat",
    "Remote",
]

DEMO_EMPLOYMENT_TYPES = [
    "Full-time",
    "Contract",
    "Internship",
    "Part-time",
]

DEMO_SKILLS = [
    "Python", "JavaScript", "TypeScript", "React", "Node.js", "Go", "Java",
    "Python", "AWS", "Docker", "Kubernetes", "PostgreSQL", "MongoDB",
    "Redis", "GraphQL", "REST APIs", "Microservices", "CI/CD", "Terraform",
]

DEMO_DESCRIPTIONS = [
    """We are looking for a passionate {title} to join our growing team at {company}. 

Responsibilities:
• Design and develop scalable software solutions
• Collaborate with cross-functional teams
• Write clean, maintainable code
• Participate in code reviews
• Contribute to architecture decisions

Requirements:
• 3+ years of experience in software development
• Strong problem-solving skills
• Experience with {skill1}, {skill2}, {skill3}
• Bachelor's degree in Computer Science or equivalent
• Excellent communication skills

Benefits:
• Competitive salary and equity
• Health insurance
• Flexible working hours
• Learning and development budget
• Modern equipment""",

    """Join {company} as a {title} and help us build the future of technology.

What you'll do:
• Build and maintain high-performance applications
• Work with modern tech stack including {skill1}, {skill2}
• Mentor junior developers
• Drive technical excellence

Who you are:
• {experience} years of relevant experience
• Deep understanding of {skill1} and {skill3}
• Experience with cloud platforms (AWS/GCP/Azure)
• Strong debugging and optimization skills

We offer:
• {salary} per annum
• Stock options
• Remote-first culture
• Annual conference budget
• 25 days vacation""",

    """{company} is seeking a talented {title} to join our innovative team.

Role overview:
• Develop new features for our core platform
• Optimize existing systems for scale
• Collaborate with product and design teams
• Ensure code quality through testing and reviews

Required qualifications:
• Proven experience with {skill1}, {skill2}, {skill3}
• {experience}+ years in software engineering
• Strong computer science fundamentals
• Experience with agile methodologies

Nice to have:
• Open source contributions
• Experience with {skill4}
• Previous startup experience

Compensation: {salary} + benefits""",
]

DEMO_RECRUITERS = [
    {"name": "Priya Sharma", "email": "priya.sharma@techcorp.com"},
    {"name": "Rahul Verma", "email": "rahul.verma@dataflow.io"},
    {"name": "Anita Desai", "email": "anita.desai@cloudnine.tech"},
    {"name": "Vikram Singh", "email": "vikram.singh@aiventures.ai"},
    {"name": "Neha Patel", "email": "neha.patel@devstack.dev"},
    {"name": "Arjun Reddy", "email": "arjun.reddy@bytebridge.co"},
    {"name": "Kavya Nair", "email": "kavya.nair@quantumsoft.in"},
    {"name": "Rohit Gupta", "email": "rohit.gupta@nextgen.tech"},
    {"name": "Sneha Agarwal", "email": "sneha.agarwal@scaleup.solutions"},
    {"name": "Mohit Jain", "email": "mohit.jain@innovatelabs.io"},
]


def generate_demo_jobs(count: int = 50) -> List[NormalizedJob]:
    jobs = []
    
    for i in range(count):
        company = random.choice(DEMO_COMPANIES)
        title = random.choice(DEMO_TITLES)
        location = random.choice(DEMO_LOCATIONS)
        employment_type = random.choice(DEMO_EMPLOYMENT_TYPES)
        experience = random.randint(1, 10)
        salary_min = random.randint(800000, 3000000)
        salary_max = salary_min + random.randint(500000, 2000000)
        
        skills = random.sample(DEMO_SKILLS, min(4, len(DEMO_SKILLS)))
        
        description_template = random.choice(DEMO_DESCRIPTIONS)
        description = description_template.format(
            title=title,
            company=company["name"],
            skill1=skills[0],
            skill2=skills[1] if len(skills) > 1 else skills[0],
            skill3=skills[2] if len(skills) > 2 else skills[0],
            skill4=skills[3] if len(skills) > 3 else skills[0],
            experience=experience,
            salary=f"₹{salary_min:,} - ₹{salary_max:,}",
        )
        
        recruiter = random.choice(DEMO_RECRUITERS)
        
        # Add some risk signals to some jobs
        risk_signals = ""
        if random.random() < 0.1:  # 10% have risk signals
            risk_signals = random.choice([
                "Registration fee required before joining. Security deposit of ₹50,000.",
                "Pay for training program before starting. Guaranteed placement after training.",
                "WhatsApp only communication. Send Aadhaar and PAN for verification.",
                "Buy laptop from company. ₹75,000 equipment deposit required.",
            ])
            description = risk_signals + "\n\n" + description
        
        posted_date = datetime.now() - timedelta(days=random.randint(0, 30))
        
        job = NormalizedJob(
            source="demo",
            source_job_id=f"demo-{i+1:04d}",
            source_url=f"https://demo.jobshield.app/jobs/demo-{i+1:04d}",
            title=title,
            company_name=company["name"],
            description=description,
            location=location,
            employment_type=employment_type,
            salary={
                "min": salary_min,
                "max": salary_max,
                "currency": "INR",
            },
            posted_at=posted_date,
            expires_at=posted_date + timedelta(days=random.randint(30, 90)),
            recruiter_name=recruiter["name"],
            emails=[
                {"value": f"hr@{company['domain']}", "type": "email"},
                {"value": recruiter["email"], "type": "email"},
            ],
            phone_numbers=[
                {"value": f"+91 {random.randint(70000, 99999)} {random.randint(10000, 99999)}", "type": "phone"},
            ],
            apply_url=f"https://{company['domain']}/careers/apply/{i+1:04d}",
            raw_source_metadata={
                "demo": True,
                "generated_at": datetime.now().isoformat(),
            },
        )
        jobs.append(job)
    
    return jobs


def create_demo_sources() -> List[Source]:
    return [
        Source(
            name="demo",
            display_name="Demo Data",
            description="Synthetic job data for demonstration purposes",
            adapter_class="ManualURLAdapter",
            base_url="https://demo.jobshield.app",
            requires_authorization=False,
            is_active=True,
            rate_limit_per_minute=1000,
            config_schema={},
        ),
        Source(
            name="greenhouse",
            display_name="Greenhouse",
            description="Greenhouse ATS integration",
            adapter_class="GreenhouseAdapter",
            base_url="https://boards-api.greenhouse.io",
            requires_authorization=True,
            is_active=True,
            rate_limit_per_minute=60,
            config_schema={
                "type": "object",
                "properties": {
                    "board_token": {"type": "string", "description": "Greenhouse board token"},
                },
                "required": ["board_token"],
            },
        ),
        Source(
            name="lever",
            display_name="Lever",
            description="Lever ATS integration",
            adapter_class="LeverAdapter",
            base_url="https://api.lever.co",
            requires_authorization=True,
            is_active=True,
            rate_limit_per_minute=60,
            config_schema={
                "type": "object",
                "properties": {
                    "company": {"type": "string", "description": "Lever company name"},
                },
                "required": ["company"],
            },
        ),
        Source(
            name="rss",
            display_name="RSS Feed",
            description="Generic RSS/Atom job feed",
            adapter_class="RSSAdapter",
            base_url="",
            requires_authorization=False,
            is_active=True,
            rate_limit_per_minute=30,
            config_schema={
                "type": "object",
                "properties": {
                    "feed_url": {"type": "string", "format": "uri", "description": "RSS feed URL"},
                },
                "required": ["feed_url"],
            },
        ),
        Source(
            name="manual",
            display_name="Manual URL",
            description="Manually submitted job URLs",
            adapter_class="ManualURLAdapter",
            base_url="",
            requires_authorization=False,
            is_active=True,
            rate_limit_per_minute=100,
            config_schema={},
        ),
    ]