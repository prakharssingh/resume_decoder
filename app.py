from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import string
import os
import docx2txt
from pdfminer.high_level import extract_text
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.secret_key = 'jsklajfifivifi2454435'

# ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER']) #if not then make it

# download nltk data
nltk.download('punkt')
nltk.download('stopwords')

# job roles and skills
jobRoles = {
    'Frontend Engineer': [
        'React', 'Vue.js', 'Angular', 'Svelte', 'Next.js', 'JavaScript', 'TypeScript', 'HTML', 'HTML5', 
        'CSS', 'CSS3', 'Tailwind CSS', 'Sass', 'Responsive Design', 'UI/UX Design', 'Web Accessibility', 
        'REST APIs', 'GraphQL', 'Performance Optimization', 'Cross-Browser Compatibility', 'Webpack', 'Vite', 
        'Jest', 'Cypress', 'Testing', 'Git', 'Agile Methodologies'
    ],
    'Backend Engineer': [
        'Python', 'Java', 'Node.js', 'Go', 'Ruby', 'PHP', 'C#', 'REST APIs', 'GraphQL', 'Microservices', 
        'SQL', 'NoSQL', 'MongoDB', 'PostgreSQL', 'MySQL', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 
        'Data Structures', 'Algorithms', 'System Design', 'Scalability', 'Authentication', 'Authorization', 
        'Caching', 'Message Queues', 'Redis', 'RabbitMQ', 'CI/CD', 'Unit Testing', 'Testing'
    ],
    'Fullstack Developer': [
        'React', 'Vue.js', 'Node.js', 'Express.js', 'Django', 'Spring Boot', 'JavaScript', 'TypeScript', 
        'Python', 'Java', 'HTML', 'CSS', 'REST APIs', 'GraphQL', 'SQL', 'NoSQL', 'MongoDB', 'PostgreSQL', 
        'Microservices', 'Responsive Design', 'UI/UX', 'Performance Optimization', 'Docker', 'AWS', 
        'System Architecture', 'Jest', 'Mocha', 'Testing', 'Git', 'Agile Methodologies'
    ],
    'Software Engineer': [
        'Python', 'Java', 'C++', 'C#', 'JavaScript', 'Go', 'Data Structures', 'Algorithms', 
        'Object-Oriented Programming', 'Functional Programming', 'System Design', 'SQL', 
        'Design Patterns', 'Cloud Computing', 'AWS', 'Azure', 'Linux', 'CI/CD', 'Unit Testing', 
        'Integration Testing', 'Testing', 'SDLC', 'Agile', 'Scrum', 'Git', 'Documentation'
    ],
    'Cybersecurity Engineer': [
        'Network Security', 'Penetration Testing', 'Ethical Hacking', 'Cryptography', 'Cloud Security', 
        'AWS Security', 'Azure Security', 'Incident Response', 'Vulnerability Assessment', 'Firewalls', 
        'SIEM', 'Splunk', 'Wireshark', 'Identity Management', 'OAuth', 'Zero Trust', 'Compliance', 
        'GDPR', 'ISO 27001', 'Python', 'PowerShell', 'Scripting', 'Linux'
    ],
    'Blockchain Engineer': [
        'Solidity', 'Rust', 'Go', 'Ethereum', 'Hyperledger', 'Smart Contracts', 'Cryptography', 
        'Distributed Systems', 'Consensus Algorithms', 'Web3.js', 'Truffle', 'Hardhat', 'IPFS', 
        'Decentralized Applications', 'Blockchain Security', 'Tokenomics', 'JavaScript', 'Node.js', 
        'Testing', 'Git'
    ],
    'DevOps Engineer': [
        'Docker', 'Kubernetes', 'Terraform', 'Ansible', 'Jenkins', 'GitLab CI', 'AWS', 'Azure', 'GCP', 
        'Infrastructure as Code', 'CI/CD', 'Monitoring', 'Prometheus', 'Grafana', 'ELK Stack', 
        'CloudFormation', 'Python', 'Bash', 'Scripting', 'Linux', 'Networking', 'Security', 
        'System Administration', 'Automation'
    ],
    'Mobile App Developer': [
        'Swift', 'Kotlin', 'Dart', 'Flutter', 'React Native', 'iOS Development', 'Android Development', 
        'Java', 'Xcode', 'Android Studio', 'REST APIs', 'GraphQL', 'Firebase', 'Push Notifications', 
        'UI/UX Design', 'Mobile Testing', 'Cross-Platform Development', 'Performance Optimization', 
        'App Store Deployment', 'Git', 'Agile'
    ],
    'Database Administrator': [
        'SQL', 'Oracle', 'MySQL', 'PostgreSQL', 'MongoDB', 'Database Design', 'Data Modeling', 
        'Performance Tuning', 'Backup and Recovery', 'High Availability', 'Replication', 
        'Data Security', 'Cloud Databases', 'AWS RDS', 'Azure SQL', 'ETL Processes', 'Python', 
        'PowerShell', 'Scripting', 'Linux', 'Windows Server'
    ],
    'Data Analyst': [
        'Python', 'R', 'SQL', 'Tableau', 'Power BI', 'Data Visualization', 'Statistical Analysis', 
        'Data Cleaning', 'Pandas', 'NumPy', 'Excel', 'ETL', 'Data Warehousing', 'Business Intelligence', 
        'A/B Testing', 'Reporting', 'Dashboard Development'
    ],
    'Data Scientist': [
        'Python', 'R', 'SQL', 'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 
        'Scikit-Learn', 'Pandas', 'NumPy', 'NLP', 'Time Series Analysis', 'Statistical Modeling', 
        'Data Visualization', 'Tableau', 'Power BI', 'Big Data', 'Hadoop', 'Spark', 'Cloud Computing', 
        'AWS'
    ],
    'Data Engineer': [
        'Python', 'Java', 'Scala', 'SQL', 'NoSQL', 'Hadoop', 'Spark', 'Kafka', 'Airflow', 
        'ETL Pipelines', 'Data Warehousing', 'Snowflake', 'Redshift', 'BigQuery', 'Data Modeling', 
        'Database Optimization', 'Streaming Data', 'AWS', 'Azure', 'GCP'
    ],
    'Business Analyst': [
        'SQL', 'Tableau', 'Power BI', 'Requirements Gathering', 'Process Modeling', 'BPMN', 'UML', 
        'Data Analysis', 'Business Process Improvement', 'Stakeholder Management', 'Agile', 'Scrum', 
        'JIRA', 'Confluence', 'Excel', 'Change Management', 'Documentation'
    ],
    'Machine Learning Engineer': [
        'Python', 'TensorFlow', 'PyTorch', 'Scikit-Learn', 'Machine Learning', 'Deep Learning', 
        'Computer Vision', 'NLP', 'Reinforcement Learning', 'Data Preprocessing', 'Feature Engineering', 
        'Model Deployment', 'MLOps', 'AWS SageMaker', 'Docker', 'Kubernetes', 'Statistical Analysis'
    ],
    'Cloud Architect': [
        'AWS', 'Azure', 'GCP', 'Cloud Architecture', 'Serverless', 'Lambda', 'Kubernetes', 
        'Terraform', 'Cloud Security', 'High Availability', 'Disaster Recovery', 'Cost Optimization', 
        'Networking', 'VPN', 'Load Balancing', 'Microservices', 'DevOps'
    ],
    'UI/UX Designer': [
        'Figma', 'Sketch', 'Adobe XD', 'Wireframing', 'Prototyping', 'User Research', 
        'Usability Testing', 'Interaction Design', 'Visual Design', 'Design Systems', 
        'User-Centered Design', 'Accessibility', 'HTML', 'CSS', 'JavaScript'
    ],
    'Product Manager': [
        'Product Lifecycle Management', 'Roadmapping', 'User Stories', 'Prioritization', 
        'Market Research', 'Analytics', 'A/B Testing', 'KPI Tracking', 'Stakeholder Management', 
        'Agile', 'Scrum', 'JIRA', 'Confluence'
    ],
    'Game Developer': [
        'Unity', 'Unreal Engine', 'C#', 'C++', 'Game Design', '3D Modeling', 'Animation', 
        'Physics Simulation', 'Multiplayer Networking', 'Shader Programming', 'VR/AR', 
        'Performance Optimization', 'Testing', 'Git'
    ],
    'AI Engineer': [
        'Python', 'TensorFlow', 'PyTorch', 'Keras', 'Machine Learning', 'Deep Learning', 
        'NLP', 'Computer Vision', 'Generative AI', 'Reinforcement Learning', 'Data Preprocessing', 
        'Feature Engineering', 'Model Deployment', 'MLOps', 'AWS', 'Azure', 'GCP', 'Big Data', 
        'Spark', 'Docker', 'Kubernetes'
    ],
    'SDET': [
        'Selenium', 'Cypress', 'Appium', 'Test Automation', 'API Testing', 'Performance Testing', 
        'Load Testing', 'JUnit', 'TestNG', 'JMeter', 'Python', 'Java', 'JavaScript', 'SQL', 
        'Test Case Design', 'Quality Assurance', 'CI/CD', 'Jenkins', 'Docker', 'Git', 
        'Agile', 'Scrum', 'Bug Tracking', 'JIRA'
    ]
}

# course recommendations
courseRecommendations = {
    'Frontend Engineer': ['HTML & CSS (Coursera)', 'React.js (Udemy)', 'JavaScript Basics (freeCodeCamp)'],
    'Backend Engineer': ['Python for Backend (Udemy)', 'Node.js (Udemy)', 'Database Design (edX)'],
    'Fullstack Developer': ['Full Stack Web Development (Coursera)', 'MERN Stack (Udemy)', 'Git Essentials (Pluralsight)'],
    'Software Engineer': ['Data Structures & Algorithms (Coursera)', 'Software Engineering 101 (edX)', 'Python Programming (Udemy)'],
    'Cybersecurity Engineer': ['Cybersecurity Fundamentals (Coursera)', 'Ethical Hacking (Udemy)', 'Network Security (edX)'],
    'Blockchain Engineer': ['Blockchain Basics (Coursera)', 'Solidity Programming (Udemy)', 'Applied Cryptography (Coursera)'],
    'DevOps Engineer': ['DevOps Essentials (Coursera)', 'AWS Certified DevOps (Udemy)', 'CI/CD with Jenkins (LinkedIn Learning)'],
    'Mobile App Developer': ['Android Development with Kotlin (Udemy)', 'iOS Development with Swift (Coursera)', 'React Native (Udemy)'],
    'Database Administrator': ['SQL Mastery (Udemy)', 'Oracle Database Admin (Udemy)', 'Database Management (Coursera)'],
    'Data Analyst': ['Data Analysis with Python (Coursera)', 'Tableau for Data Analysts (Udemy)', 'Excel Skills for Data Analytics (Coursera)'],
    'Data Scientist': ['Machine Learning (Coursera)', 'Data Science with Python (Udemy)', 'Statistics for Data Science (Coursera)'],
    'Data Engineer': ['Big Data with Hadoop (Coursera)', 'Data Engineering on AWS (Udemy)', 'Apache Kafka (Pluralsight)'],
    'Business Analyst': ['Business Analysis and Process Management (Coursera)', 'SQL for Business Analysts (Udemy)', 'Master Power BI (LinkedIn Learning)'],
    'Machine Learning Engineer': ['Deep Learning (Coursera)', 'TensorFlow Developer (Udemy)', 'Math for ML (Coursera)'],
    'Cloud Architect': ['AWS Solutions Architect (Udemy)', 'Azure Fundamentals (Microsoft Learn)', 'Cloud Security (Coursera)'],
    'UI/UX Designer': ['UI/UX Design Fundamentals (Coursera)', 'Figma Megacourse (Udemy)', 'User Research Methods (Interaction Design)'],
    'Product Manager': ['Product Management Essentials (Coursera)', 'Agile Product Management (Udemy)', 'Product Analytics (Udemy)'],
    'Game Developer': ['Unity Game Development (Udemy)', 'C# Programming for Unity (Coursera)', '3D Modelling (Coursera)'],
    'AI Engineer': ['AI Programming with Python (Udemy)', 'AI Engineering (Coursera)', 'Neural Networks and Deep Learning (Coursera)'],
    'SDET': ['Test Automation with Selenium (Udemy)', 'API Testing (Coursera)', 'Test Management (Coursera)']
}

# course links
courseLinks = {
    'Frontend Engineer': [
        'https://www.coursera.org/learn/html-css-javascript-for-web-developers', # HTML & CSS (Coursera)
        'https://www.udemy.com/course/react-the-complete-guide-incl-redux/', # React.js (Udemy)
        'https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/' # JavaScript Basics (freeCodeCamp)
    ],
    'Backend Engineer': [
        'https://www.udemy.com/course/software-developer-masterclass/', # Python for Backend (Udemy)
        'https://www.udemy.com/course/nodejs-the-complete-guide/', # Node.js (Udemy)
        'https://www.edx.org/learn/databases/the-university-of-michigan-database-design-and-basic-sql-in-postgresql' # Database Design (edX)
    ],
    'Fullstack Developer': [
        'https://www.coursera.org/learn/fullstack-web-development', # Full Stack Web Development (Coursera)
        'https://www.udemy.com/course/mern-stack-front-to-back/', # MERN Stack (Udemy)
        'https://www.pluralsight.com/courses/git-fundamentals' # Git Essentials (Pluralsight)
    ],
    'Software Engineer': [
        'https://www.coursera.org/specializations/data-structures-algorithms', # Data Structures & Algorithms (Coursera)
        'https://www.edx.org/learn/software-engineering/university-of-british-columbia-software-engineering-introduction', # Software Engineering 101 (edX)
        'https://www.udemy.com/course/complete-python-bootcamp/' # Python Programming (Udemy)
    ],
    'Cybersecurity Engineer': [
        'https://www.coursera.org/professional-certificates/google-cybersecurity', # Cybersecurity Fundamentals (Coursera)
        'https://www.udemy.com/course/learn-ethical-hacking-from-scratch/', # Ethical Hacking (Udemy)
        'https://www.edx.org/learn/network-security/rochester-institute-of-technology-network-security' # Network Security (edX)
    ],
    'Blockchain Engineer': [
        'https://www.coursera.org/specializations/blockchain', # Blockchain Basics (Coursera)
        'https://www.udemy.com/course/blockchain-developer/', # Solidity Programming (Udemy)
        'https://www.coursera.org/specializations/applied-crypto' # Applied Cryptography (Coursera)
    ],
    'DevOps Engineer': [
        'https://www.coursera.org/specializations/packt-devops-complete-course', # DevOps Essentials (Coursera)
        'https://www.udemy.com/course/aws-certified-devops-engineer-professional-hands-on/', # AWS Certified DevOps (Udemy)
        'https://www.linkedin.com/learning/paths/continuous-integration-continuous-delivery-ci-cd-with-jenkins' # CI/CD with Jenkins (LinkedIn Learning)
    ],
    'Mobile App Developer': [
        'https://www.udemy.com/course/android-kotlin-developer/', # Android Development with Kotlin (Udemy)
        'https://www.coursera.org/specializations/ios-development', # iOS Development with Swift (Coursera)
        'https://www.udemy.com/course/react-native-the-practical-guide/' # React Native (Udemy)
    ],
    'Database Administrator': [
        'https://www.udemy.com/course/the-complete-sql-bootcamp/', # SQL Mastery (Udemy)
        'https://www.udemy.com/course/oracle-dba-course/', # Oracle Database Admin (Udemy)
        'https://www.coursera.org/learn/database-management-with-java-and-sql' # Database Management (Coursera)
    ],
    'Data Analyst': [
        'https://www.coursera.org/specializations/data-analysis-python', # Data Analysis with Python (Coursera)
        'https://www.udemy.com/course/tableau-for-beginners/', # Tableau for Data Analysts (Udemy)
        'https://www.coursera.org/specializations/excel-data-analytics-visualization' # Excel Skills for Data Analytics (Coursera)
    ],
    'Data Scientist': [
        'https://www.coursera.org/specializations/machine-learning-introduction', # Machine Learning (Coursera)
        'https://www.udemy.com/course/python-for-data-science-and-machine-learning-bootcamp/', # Data Science with Python (Udemy)
        'https://www.coursera.org/learn/statistics-for-data-science-python' # Statistics for Data Science (Coursera)
    ],
    'Data Engineer': [
        'https://www.coursera.org/specializations/big-data', # Big Data with Hadoop (Coursera)
        'https://www.udemy.com/course/data-engineering-on-aws/', # Data Engineering on AWS (Udemy)
        'https://www.pluralsight.com/courses/apache-kafka-getting-started' # Apache Kafka (Pluralsight)
    ],
    'Business Analyst': [
        'https://www.coursera.org/projects/business-analysis-process-management', # Business Analysis and Process Management (Coursera)
        'https://www.udemy.com/course/business-and-data-analysis-with-sql/', # SQL for Business Analysts (Udemy)
        'https://www.linkedin.com/learning/paths/master-microsoft-power-bi-15399694' # Master Power BI (LinkedIn Learning)
    ],
    'Machine Learning Engineer': [
        'https://www.coursera.org/specializations/deep-learning', # Deep Learning (Coursera)
        'https://www.udemy.com/course/tensorflow-developer-certificate-machine-learning-zero-to-mastery/', # TensorFlow Developer (Udemy)
        'https://www.coursera.org/specializations/mathematics-machine-learning' # Math for ML (Coursera)
    ],
    'Cloud Architect': [
        'https://www.udemy.com/course/aws-certified-solutions-architect-associate-saa-c03/', # AWS Solutions Architect (Udemy)
        'https://learn.microsoft.com/en-us/training/paths/azure-fundamentals/', # Azure Fundamentals (Microsoft Learn)
        'https://www.coursera.org/specializations/cybersecurity-cloud' # Cloud Security (Coursera)
    ],
    'UI/UX Designer': [
        'https://www.coursera.org/specializations/ui-ux-design', # UI/UX Design Fundamentals (Coursera)
        'https://www.udemy.com/course/beginners-guide-to-prototyping-and-designing-using-figma/', # Figma Megacourse (Udemy)
        'https://www.interaction-design.org/courses/user-research-methods-and-best-practices' # User Research Methods (Interaction Design)
    ],
    'Product Manager': [
        'https://www.coursera.org/specializations/product-management', # Product Management Essentials (Coursera)
        'https://www.udemy.com/course/advanced-agile-product-management/', # Agile Product Management (Udemy)
        'https://www.udemy.com/course/product-analytics-for-product-managers/' # Product Analytics (Udemy)
    ],
    'Game Developer': [
        'https://www.udemy.com/course/unitycourse/', # Unity Game Development (Udemy)
        'https://www.coursera.org/specializations/programming-unity-game-development', # C# Programming for Unity (Coursera)
        'https://www.coursera.org/learn/packt-foundations-of-3d-modelling-in-blender-ugmas' # 3D Modelling (Coursera)
    ],
    'AI Engineer': [
        'https://www.udemy.com/course/the-complete-python-programming-and-generative-ai-bootcamp/', # AI Programming with Python (Udemy)
        'https://www.coursera.org/specializations/ai-engineering', # AI Engineering (Coursera)
        'https://www.coursera.org/learn/neural-networks-deep-learning' # Neural Networks and Deep Learning (Coursera)
    ],
    'SDET': [
        'https://www.udemy.com/course/selenium-webdriver-with-java/', # Test Automation with Selenium (Udemy)
        'https://www.coursera.org/projects/api-testing-using-rest-assured-test-automation-tool', # API Testing (Coursera)
        'https://www.coursera.org/learn/test-management-in-software-testing' # Test Management (Coursera)
    ]
}

# text extraction functions 
def extract_text_from_pdf(pdf_path):
    try:
        text = extract_text(pdf_path)
        return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""

def extract_text_from_docx(docx_path):
    txt = docx2txt.process(docx_path)
    if txt:
        return txt.replace('\t', ' ')
    return None

# extraction functions from text mined above
def extract_name_from_resume(s):
    name = None
    
    # Common words to exclude that are often misidentified as names
    exclude_words = [
        'class', 'bachelors', 'bachelor', 'masters', 'master', 'phd', 'doctor', 'university',
        'college', 'institute', 'school', 'academy', 'resume', 'curriculum', 'vitae', 'cv',
        'profile', 'summary', 'objective', 'education', 'experience', 'skills', 'projects',
        'github', 'linkedin', 'contact', 'email', 'phone', 'address', 'references', 'professional',
        'technical', 'software', 'developer', 'engineer', 'analyst', 'manager', 'director',
        'certification', 'certificate', 'degree', 'diploma', 'course', 'program', 'major',
        'minor', 'gpa', 'grade', 'score', 'achievement', 'award', 'honor', 'publication',
        'research', 'project', 'work', 'job', 'position', 'role', 'responsibility', 'duty',
        'task', 'function', 'activity', 'assignment', 'accomplishment', 'success', 'result',
        'outcome', 'impact', 'contribution', 'performance', 'evaluation', 'assessment', 'review'
    ]
    
    # First approach: Look for a name at the beginning of the resume
    lines = s.split('\n')
    first_few_lines = [line.strip() for line in lines[:7] if line.strip() and len(line.strip()) < 40]
    
    for line in first_few_lines:
        # Skip lines with common exclude words
        if any(word.lower() in line.lower() for word in exclude_words):
            continue
            
        # Pattern for names with proper capitalization: First [Middle] Last
        pattern1 = r"^([A-Z][a-z]+)(?:\s+(?:[A-Z]\.?|[A-Z][a-z]+))?\s+([A-Z][a-z]+)$"
        # Pattern for ALL CAPS names: FIRST [MIDDLE] LAST
        pattern2 = r"^([A-Z]{2,})(?:\s+(?:[A-Z]\.?|[A-Z]{2,}))?\s+([A-Z]{2,})$"
        # Pattern for name with middle name spelled out
        pattern3 = r"^([A-Z][a-z]+)\s+([A-Z][a-z]+)\s+([A-Z][a-z]+)$"
        
        match1 = re.match(pattern1, line)
        match2 = re.match(pattern2, line)
        match3 = re.match(pattern3, line)
        
        if match1:
            return line.strip()
        elif match2:
            # Convert ALL CAPS to Title Case for better readability
            name_parts = line.strip().split()
            formatted_name = ' '.join([part.title() for part in name_parts])
            return formatted_name
        elif match3:
            return line.strip()
    
    # Second approach: Look for explicit name labels
    name_patterns = [
        r"(?:Name|NAME|Full Name|FULL NAME)[\s:]+([A-Z][a-z]+(?:\s+[A-Z](?:\.|\s+)[A-Z][a-z]+|\s+[A-Z][a-z]+){1,2})",
        r"(?:Name|NAME|Full Name|FULL NAME)[\s:]+([A-Z]{2,}(?:\s+[A-Z](?:\.|\s+)[A-Z]{2,}|\s+[A-Z]{2,}){1,2})",
        r"(?:Name|NAME|Full Name|FULL NAME)[\s:]+([A-Z][a-z]+\s+[A-Z][a-z]+)"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, s)
        if match:
            potential_name = match.group(1).strip()
            if not any(word.lower() in potential_name.lower() for word in exclude_words):
                # If name is in ALL CAPS, convert to Title Case
                if potential_name.isupper():
                    name_parts = potential_name.split()
                    potential_name = ' '.join([part.title() for part in name_parts])
                return potential_name
    
    return None

def extract_contact_number_from_resume(s):
    contact_number = None
    pattern = r"(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)[-\.\s]*\d{3}[-\.\s]??\d{4}|\d{5}[-\.\s]??\d{4})"
    match = re.search(pattern, s)
    if match:
        contact_number = match.group()
    return contact_number

def extract_email_from_resume(s):
    email = None
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    match = re.search(pattern, s)
    if match:
        email = match.group()
    return email

def extract_education_from_resume(s):
    education = []
    
    # First, identify the education section
    edu_section = re.search(r'(?:Education|EDUCATION)(.*?)(?:Experience|EXPERIENCE|Skills|SKILLS|Projects|PROJECTS|Work|WORK|$)', s, re.DOTALL | re.IGNORECASE)
    
    if not edu_section:
        return education  # No education section found
    
    # Extract just the education section text
    edu_text = edu_section.group(1)
    
    # Degree patterns - only include higher education patterns
    degree_patterns = [
        r"\b(?:B\.?A\.?|Bachelor\'?s?\s+of\s+Arts)\b",
        r"\b(?:B\.?S\.?C\.?|B\.?Sc\.?|B\.?S\.?|Bachelor\'?s?\s+of\s+Science)\b",
        r"\b(?:B\.?E\.?|Bachelor\'?s?\s+of\s+Engineering)\b",
        r"\b(?:B\.?Tech\.?|B\-Tech|Bachelor\'?s?\s+of\s+Technology)\b",  # Added B-Tech format
        r"\b(?:B\.?C\.?A\.?|Bachelor\'?s?\s+of\s+Computer\s+Applications)\b",
        r"\b(?:M\.?C\.?A\.?|Master\'?s?\s+of\s+Computer\s+Applications)\b",
        r"\b(?:B\.?B\.?A\.?|Bachelor\'?s?\s+of\s+Business\s+Administration)\b",
        r"\b(?:M\.?B\.?A\.?|Master\'?s?\s+of\s+Business\s+Administration)\b",
        r"\b(?:M\.?A\.?|Master\'?s?\s+of\s+Arts)\b",
        r"\b(?:M\.?S\.?C\.?|M\.?Sc\.?|Master\'?s?\s+of\s+Science)\b",
        r"\b(?:M\.?S\.?|Master\'?s?\s+of\s+Science)\b",
        r"\b(?:M\.?Tech\.?|M\-Tech|Master\'?s?\s+of\s+Technology)\b",  # Also added M-Tech format
        r"\b(?:Ph\.?D\.?|Doctor\s+of\s+Philosophy)\b",
        r"\b(?:Diploma)\b"
    ]

    # Match degree without field of study
    combined_pattern = r"(?i)({})".format("|".join(degree_patterns))
    
    matches = re.findall(combined_pattern, edu_text)
    
    for match in matches:
        degree = match.strip()
        if degree:
            # Keep the original degree name
            education.append(degree)
    
    # If no matches found with the above pattern, try a more general approach
    if not education:
        # Look for specific degree patterns in the education section
        degree_patterns = [
            r"Bachelor\'?s?\s+of\s+([A-Za-z\s]+)",
            r"Master\'?s?\s+of\s+([A-Za-z\s]+)",
            r"Ph\.?D\.?\s+(?:in|of)?\s+([A-Za-z\s]+)"
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, edu_text, re.IGNORECASE)
            for match in matches:
                if match:
                    field = match.strip()
                    degree_type = re.search(r"(Bachelor|Master|Ph\.?D\.?)", pattern, re.IGNORECASE).group(1)
                    education.append(f"{degree_type} of {field}")
    
    return list(set(education))



# def extract_gpa_from_resume(s):
#     gpa = None
#     pattern = r'[0-9]+\.\d?(\d)'
#     match = re.search(pattern, s)
#     if match:
#         gpa = match.group()
#     return gpa
def extract_gpa_from_resume(text):
    patterns = [
        r'(?:GPA|CGPA|Grade\s*Point\s*Average)[\s:]*(\d*\.?\d{1,2})\s*(?:/|out\s*of)\s*(4\.0|10\.0)',
        r'(?:GPA|CGPA|Grade\s*Point\s*Average)[\s:]*(\d*\.?\d{1,2})(?!\s*(?:%|seconds|minutes|hours|years))',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if len(match) == 2:
                gpa = float(match[0])
                scale = match[1]
            else:
                gpa = float(match)
                scale = "4.0" if gpa <= 4.0 else "10.0"
            if scale == "4.0" and 0.0 <= gpa <= 4.0:
                return gpa
            elif scale == "10.0" and 0.0 <= gpa <= 10.0:
                return gpa
    return None

def extract_skills_from_resume(s, skills_list):
    skills = []
    for skill in skills_list:
        pattern = r"\b{}\b".format(re.escape(skill))
        match = re.search(pattern, s, re.IGNORECASE)
        if match:
            skills.append(skill)
    return skills

# ATS score calculation support functions
# def extract_experience_years(text):
#     """Extract years of experience from the resume."""
#     pattern = r"(\d+\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience|\b\d{1,2}\s*(?:years?|yrs?))"
#     matches = re.findall(pattern, text, re.IGNORECASE)
#     if matches:
#         for match in matches:
#             num = re.search(r'\d+', match)
#             if num:
#                 return int(num.group())
#     # to incorporate dates to calculate experience
#     date_pattern = r"(\d{4})\s*[-–—]\s*(\d{4})"
#     date_matches = re.findall(date_pattern, text)
#     if date_matches:
#         total_years = sum(int(end) - int(start) for start, end in date_matches if int(end) > int(start))
#         return total_years
#     return 0  # if no experience then return 0
def extract_experience_years(text):
    """Extract years of experience from the resume more accurately."""
    total_months = 0
    
    # Pattern 1 direct mention of experience 
    exp_pattern = r"(\d+\.?\d*)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp\.?)"
    exp_matches = re.findall(exp_pattern, text, re.IGNORECASE)
    if exp_matches:
        # Use the highest mentioned experience
        return float(max(exp_matches))
    
    # Pattern 2: Look for experience sections with date ranges
    # This pattern captures job titles, internships, and positions followed by dates
    job_sections = re.findall(r'(?:Experience|Work|Employment|Intern|Developer|Engineer|Founder|Participant|Co-Founder)[^\n]*?\n.*?(\w+\s+\d{4})\s*[-–—]\s*(\w+\s+\d{4}|Present|Current|Now)', text, re.DOTALL | re.IGNORECASE)
    
    # If no job sections found with the above pattern, try a more general approach
    if not job_sections:
        # Look for date ranges that appear to be work experiences
        # This pattern captures month-year to month-year formats
        date_pattern = r'(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\s*[-–—]\s*(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4}|Present|Current|Now)'
        month_year_matches = re.findall(date_pattern, text, re.IGNORECASE)
        
        # Also look for simpler month year-year format (e.g., "June 2022-September 2022")
        simple_date_pattern = r'(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\s*[-–—]\s*(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})'
        simple_matches = re.findall(simple_date_pattern, text, re.IGNORECASE)
        
        # Combine all date matches
        all_date_matches = month_year_matches + simple_matches
        
        # Process each date range
        for start_year_str, end_year_str in all_date_matches:
            start_year = int(start_year_str)
            
            if end_year_str.lower() in ['present', 'current', 'now']:
                end_year = 2025  # Current year
            else:
                end_year = int(end_year_str)
            
            # Calculate months between dates
            months = (end_year - start_year) * 12
            if months > 0:
                total_months += months
    
    # If we still don't have any experience, try a more aggressive approach
    if total_months == 0:
        # Look for any date ranges in the format MM/YYYY-MM/YYYY or MM-YYYY to MM-YYYY
        date_pattern = r'(\d{1,2})[/-](\d{4})\s*[-–—]\s*(\d{1,2})[/-](\d{4})'
        date_matches = re.findall(date_pattern, text)
        
        for start_month, start_year, end_month, end_year in date_matches:
            months = (int(end_year) - int(start_year)) * 12 + (int(end_month) - int(start_month))
            if months > 0:
                total_months += months
    
    # As a last resort, look for specific job titles and assume they represent experience
    if total_months == 0:
        job_titles = ['intern', 'developer', 'engineer', 'founder', 'participant', 'co-founder']
        job_count = sum(1 for title in job_titles if re.search(r'\b' + title + r'\b', text, re.IGNORECASE))
        
        # If we found job titles but no dates, assume at least 3 months per position
        if job_count > 0:
            total_months = job_count * 3
    
    # Convert months to years (rounded to 1 decimal place)
    years = round(total_months / 12, 1)
    
    return max(years, 0)

def extract_designation(text):
    """Extract job titles/designations from the resume."""
    pattern = r"(?i)(Engineer|Developer|Analyst|Manager|Administrator|Scientist|Consultant|Specialist|Architect|Lead|Coordinator|Intern)\s*(?:[-–—]\s*\w+)?\b"
    match = re.search(pattern, text)
    return match.group() if match else None

def extract_company_names(text):
    """Extract company names from the resume."""
    pattern = r"(?i)(Inc\.?|LLC|Ltd\.?|Corp\.?|Co\.?|Company|Technologies|Systems|Solutions|Group)\b"
    matches = re.findall(pattern, text)
    return matches if matches else []

# preprocessing and similarity functions 
def preprocess_text(text):
    tokens = word_tokenize(text)
    tokens = [token.lower() for token in tokens]
    tokens = [token for token in tokens if token not in string.punctuation]
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    return tokens

def calculate_similarity(text, keyword_list):
    text_str = ' '.join(text)
    keyword_str = ' '.join(keyword_list)
    try:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([text_str, keyword_str])
        return cosine_similarity(tfidf_matrix)[0, 1]
    except ValueError:
        # Handle empty vocabulary error
        return 0

def calculate_keyword_match(text, keywords):
    text_tokens = preprocess_text(text)
    keyword_match = {}
    for key, values in keywords.items():
        similarity_scores = [calculate_similarity(text_tokens, preprocess_text(keyword)) for keyword in values]
        avg_similarity = sum(similarity_scores) / len(similarity_scores)
        keyword_match[key] = avg_similarity
    top_keys = sorted(keyword_match, key=keyword_match.get, reverse=True)[:5]
    return top_keys

# ATS score calculation function
def calculate_ats_score(text, top_roles, skills_extracted):
    score = 0
    max_score = 100
    recommendations = []

    # keyword matching
    keywords_total = sum(len(jobRoles[role]) for role in top_roles) / len(top_roles)
    keywords_found = len(skills_extracted)
    keyword_score = min((keywords_found / keywords_total) * 40, 40)
    score += keyword_score
    if len(skills_extracted) < 5:
        recommendations.append("Consider adding more skills to showcase your abilities. (Context: Skills)")

    # checking if basic details are in resume
    if extract_name_from_resume(text): score += 5
    else:
        recommendations.append("Add your full name prominently at the top of your resume. (Context: Contact Details)")
    if extract_contact_number_from_resume(text): score += 5
    else:
        recommendations.append("Include a phone number for employers to contact you. (Context: Contact Details)")
    if extract_email_from_resume(text): score += 5
    else:
        recommendations.append("Add a professional email address to your resume. (Context: Contact Details)")
    # education extraction 
    degree = extract_education_from_resume(text)
    if degree:
        score += 15
    else:
        recommendations.append("Consider adding your educational qualifications to the resume. (Context: Degree)")

    # checking experience
    experience = extract_experience_years(text)
    if experience >= 3:
        score += 15
    elif experience >= 1:
        score += 10
    else:
        score += 5
        recommendations.append("Consider adding some full-time or freelance work to gain experience. (Context: Experience)")

    # designation checking
    designation = extract_designation(text)
    if designation:
        score += 10
    else:
        recommendations.append("Add a clear job title to your resume to showcase your current role. (Context: Designation)")

    # comapany name checking
    company_names = extract_company_names(text)
    if company_names:
        score += 5
    else:
        recommendations.append("Add your current or previous employers to your resume. (Context: Company names)")
    # Format and length check (new)
    word_count = len(text.split())
    if word_count < 300:
        score -= 5
        recommendations.append("Your resume appears too short. Aim for 400-600 words for optimal readability. (Context: Resume Length)")
    elif word_count > 1000:
        score -= 5
        recommendations.append("Your resume may be too lengthy. Consider condensing to 1-2 pages. (Context: Resume Length)")
    else :
        score += 5
    # if no issues found
    if not recommendations:
        recommendations.append("Your resume looks great! Good luck with your job search.")

    return {
        'score': round(score, 2),
        'recommendations': recommendations
    }

# skill recommender 
def recommend_skills(text, top_roles):
    if not top_roles:
        return []
    primary_role = top_roles[0]
    relevant_skills = jobRoles.get(primary_role, [])
    extracted_skills = extract_skills_from_resume(text, relevant_skills)
    missing_skills = [skill for skill in relevant_skills if skill not in extracted_skills]
    return missing_skills[:5]

# base data extraction 
def extract_base_data(filepath):
    text = ""
    if filepath.endswith('.pdf'):
        text = extract_text_from_pdf(filepath)
    elif filepath.endswith('.docx'):
        text = extract_text_from_docx(filepath)
    else:
        return None  # Unsupported file format

    # Add this check for blank or unprocessable document
    if not text or text.strip() == "":
        return {'error': 'blank_document'}

    # If text extraction failed for docx (already handled by the check above if text is None)
    # The original check for `if text is None:` can be removed or kept if specific error message for docx processing is desired
    # For simplicity, the `if not text or text.strip() == ""` handles both None and empty strings.

    name = extract_name_from_resume(text)
    contact_number = extract_contact_number_from_resume(text)
    email = extract_email_from_resume(text)
    education = extract_education_from_resume(text)
    gpa = extract_gpa_from_resume(text)
    top_roles = calculate_keyword_match(text, jobRoles)
    skills_extracted = extract_skills_from_resume(text, set().union(*[jobRoles[role] for role in top_roles]))

    return {
        'text': text,
        'name': name,
        'contact_number': contact_number,
        'email': email,
        'education': ', '.join(education) if education else "N/A",
        'gpa': gpa,
        'top_roles': top_roles,
        'skills_extracted': skills_extracted
    }

# routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'resume' not in request.files:
            return redirect(request.url)
        file = request.files['resume']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            data = extract_base_data(filepath)
            if data is None:
                return "Unsupported file format. Please upload a PDF or DOCX file."
            # Check for specific errors
            if 'error' in data:
                if data['error'] == 'blank_document':
                    # Return a script that will show an alert and redirect back to the index page
                    return """
                    <script>
                        alert('You have uploaded a blank document. Please upload a valid resume or create one using the Resume Builder feature.');
                        window.location.href = '/';
                    </script>
                    """
                elif data['error'] == 'processing_error':
                    return """
                    <script>
                        alert('There was an error processing your resume. Please try again with a different file.');
                        window.location.href = '/';
                    </script>
                    """
            
            session['resume_data'] = data  # store in session
            return render_template('results.html', **data)
    return render_template('index.html')

@app.route('/ats_score')
def ats_score():
    if 'resume_data' not in session:
        return redirect(url_for('index'))
    data = session['resume_data']
    ats_result = calculate_ats_score(data['text'], data['top_roles'], data['skills_extracted'])
    data['ats_score'] = ats_result['score']
    data['ats_recommendations'] = ats_result['recommendations']
    return render_template('ats_score.html', **data)

@app.route('/job_roles')
def job_roles():
    if 'resume_data' not in session:
        return redirect(url_for('index'))
    data = session['resume_data']
    return render_template('job_roles.html', **data)

@app.route('/skills')
def skills():
    if 'resume_data' not in session:
        return redirect(url_for('index'))
    data = session['resume_data']
    data['recommended_skills'] = recommend_skills(data['text'], data['top_roles'])
    return render_template('skills.html', **data)

@app.route('/courses')
def courses():
    if 'resume_data' not in session:
        return redirect(url_for('index'))
    data = session['resume_data']
    top_role = data['top_roles'][0]
    data['recommended_courses'] = courseRecommendations[top_role]  # top role courses
    data['course_links'] = courseLinks[top_role]  # top role course links
    return render_template('courses.html', **data)


@app.route('/bulk', methods=['GET', 'POST'])
def bulk_screen():
    if request.method == 'POST':
        if 'resumes' not in request.files:
            return redirect(request.url)
        files = request.files.getlist('resumes')
        job_description = request.form.get('job_description', '')

        if len(files) > 20:
            return "You can upload a maximum of 20 resumes at a time."

        resumes_data = []
        for file in files:
            if file.filename == '':
                continue
            if file:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
                text = extract_text_from_pdf(filepath) if file.filename.endswith('.pdf') else extract_text_from_docx(filepath)
                resumes_data.append({'filename': file.filename, 'text': text})

        # preprocess job description
        job_desc_tokens = preprocess_text(job_description)

        # calculate similarity scores
        for resume in resumes_data:
            resume_tokens = preprocess_text(resume['text'])
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([' '.join(job_desc_tokens), ' '.join(resume_tokens)])
            similarity = cosine_similarity(tfidf_matrix)[0, 1]
            resume['similarity_score'] = similarity

        # sort resumes by similarity score
        sorted_resumes = sorted(resumes_data, key=lambda x: x['similarity_score'], reverse=True)

        return render_template('bulk_results.html', resumes=sorted_resumes, job_description=job_description)

    return render_template('bulk.html', job_roles=jobRoles.keys())

@app.route('/bulk_by_role', methods=['POST'])
def bulk_screen_by_role():
    if 'resumes' not in request.files:
        return redirect(url_for('bulk_screen'))
    
    files = request.files.getlist('resumes')
    job_role = request.form.get('job_role', '')
    
    if job_role not in jobRoles:
        return "Invalid job role selected."
    
    if len(files) > 20:
        return "You can upload a maximum of 20 resumes at a time."
    
    # Get skills for the selected job role
    job_role_skills = jobRoles[job_role]
    job_role_skills_text = ' '.join(job_role_skills)
    
    resumes_data = []
    for file in files:
        if file.filename == '':
            continue
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            text = extract_text_from_pdf(filepath) if file.filename.endswith('.pdf') else extract_text_from_docx(filepath)
            resumes_data.append({'filename': file.filename, 'text': text})
    
    # Preprocess job role skills
    job_role_tokens = preprocess_text(job_role_skills_text)
    
    # Calculate similarity scores
    for resume in resumes_data:
        resume_tokens = preprocess_text(resume['text'])
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([' '.join(job_role_tokens), ' '.join(resume_tokens)])
        similarity = cosine_similarity(tfidf_matrix)[0, 1]
        resume['similarity_score'] = similarity
    
    # Sort resumes by similarity score
    sorted_resumes = sorted(resumes_data, key=lambda x: x['similarity_score'], reverse=True)
    
    return render_template('bulk_results_role.html', 
                          resumes=sorted_resumes, 
                          job_role=job_role, 
                          skills=job_role_skills)

@app.route('/uploads/<filename>')
def serve_resume(filename):
    return send_from_directory('uploads', filename)
# Import builder functions
from builder import builder_index, preview_resume, generate_pdf_resume, save_template

# Register builder routes
@app.route('/builder')
def builder():
    return render_template('builder.html')

@app.route('/preview', methods=['POST'])
def preview():
    return preview_resume()

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    return generate_pdf_resume()

@app.route('/save_template', methods=['POST'])
def save_template():
    return save_resume_template()

@app.route('/run_builder', methods=['GET', 'POST'])
def run_builder():
    # Import the necessary functions from builder.py
    from builder import generate_pdf, preview
    
    if request.method == 'POST':
        # If it's a POST request, it might be for generating PDF or preview
        if request.path.endswith('/preview'):
            return preview()
        else:
            return generate_pdf()
    
    # If it's a GET request, render the builder template
    return render_template('builder.html')

if __name__ == '__main__':
    app.run(debug=True)