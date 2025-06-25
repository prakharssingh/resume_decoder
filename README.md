# Resume Decoder

Resume Decoder is a powerful web application that helps analyze, parse, and create professional resumes. It combines resume parsing capabilities with a modern resume builder, making it a comprehensive tool for both job seekers and recruiters.

![image](https://github.com/user-attachments/assets/9dd13f07-ff3a-4c75-ab02-d0dd99a46218)
![image](https://github.com/user-attachments/assets/81e5c521-7d17-4f7e-ad42-ab8bd2088e47)
![image](https://github.com/user-attachments/assets/d069cecf-6c2f-42a8-99ac-60fd0367fa5c)
![image](https://github.com/user-attachments/assets/e3db43f8-068d-4911-9c4c-d4fc166b4ce6)

## Features
### Resume Analysis
- Extracts key information from uploaded resumes
- Parses important details like:
  - Personal Information
  - Education History
  - Skills
  - Work Experience
- Provides skill matching against various job roles
- Offers course recommendations based on career paths
- Supports multiple job roles with specific skill requirements
- Intelligent skill extraction and matching
- Bulk resume processing capabilities
### Resume Builder
- Interactive resume creation interface
- Professional PDF generation
- Customizable sections:
  - Bio Data
  - Professional Summary
  - Skills with proficiency levels
  - Education
  - Work Experience
  - Projects
- Real-time preview functionality
- Clean, professional PDF output with proper formatting
## Technology Stack
### Backend
- Flask (Python web framework)
- Libraries:
  - docx2txt - For DOCX file parsing
  - pdfminer.six - For PDF text extraction
  - nltk - For natural language processing
  - scikit-learn - For text analysis and matching
  - reportlab - For PDF generation
### Frontend
- HTML/CSS
- JavaScript
## Installation
1. Clone the repository
2. Install the required dependencies mentioned in requirements.txt
```
pip install -r requirements.txt
```
3. Install NLTK data
```
import nltk
nltk.download('punkt')
nltk.download('stopwords')

```
## Project Structure
```
├── .gitignore
├── app.py
├── builder.py
├── requirements.txt
├── static/         
│   ├── builder.css
│   ├── styles.css      
└── templates/        
    ├── ats_score.html
    ├── builder.html  
    ├── bulk.html     
    ├── bulk_results.html 
    ├── bulk_results_role.html
    ├── courses.html        
    ├── index.html          
    ├── job_roles.html      
    ├── results.html        
    ├── resume_template.html
    └── skills.html         
```
## Usage
1. Start the Flask server:
```
python app.py
```
2. Access the application through your web browser
3. Upload resumes for analysis or use the resume builder to create new resumes
