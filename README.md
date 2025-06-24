# Resume Decoder
Resume Decoder is a powerful web application that helps analyze, parse, and create professional resumes. It combines resume parsing capabilities with a modern resume builder, making it a comprehensive tool for both job seekers and recruiters.

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
│   └── temp.css           
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
## Features in Detail
### Resume Analysis
- Supports multiple job roles with specific skill requirements
- Intelligent skill extraction and matching
- Course recommendations based on career paths
- Bulk resume processing capabilities
### Resume Builder
- Clean and professional PDF output
- Customizable sections and formatting
- Real-time preview before final generation
- Social media links integration (GitHub, LinkedIn, Portfolio)
- Professional formatting with proper spacing and typography
