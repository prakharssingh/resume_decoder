from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import inch
from io import BytesIO

app = Flask(__name__)

# Ensure upload and generated_resumes directories exist
os.makedirs('uploads', exist_ok=True)
os.makedirs(os.path.join('static', 'generated_resumes'), exist_ok=True)

@app.route('/')
def builder_index():
    return render_template('builder.html')

@app.route('/preview', methods=['POST'])
def preview_resume():
    # Get form data
    resume_data = request.json
    
    # Generate HTML for the resume preview
    resume_html = render_template('resume_template.html', resume=resume_data)
    
    return jsonify({'html': resume_html})

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf_resume():
    # Get form data
    resume_data = request.json
    
    # Create a PDF in memory
    buffer = BytesIO()
    
    # Create the PDF document with reduced margins (0.5 inch instead of 1 inch/72 points)
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                           rightMargin=30, leftMargin=30,  # Reduced from 36 to 30 points
                           topMargin=25, bottomMargin=25)  # Reduced from 36 to 30 points
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Name', 
                             fontName='Helvetica-Bold', 
                             fontSize=24,
                             alignment=1,  # Center alignment
                             spaceAfter=16))  # Increased from 6 to 12 points for more space
    styles.add(ParagraphStyle(name='Heading', 
                             fontName='Helvetica', 
                             fontSize=14, 
                             spaceAfter=6,
                             spaceBefore=12))
    styles.add(ParagraphStyle(name='ResumeNormal', 
                             fontName='Helvetica', 
                             fontSize=10, 
                             spaceAfter=6))
    styles.add(ParagraphStyle(name='Contact', 
                             fontName='Helvetica', 
                             fontSize=10, 
                             alignment=1,  # Center alignment
                             spaceAfter=12))
    
    # Helper function to format dates (Jan 2025 format)
    def format_date(date_str):
        if not date_str:
            return ""
        try:
            # Try to parse the date string
            date_parts = date_str.split('-')
            if len(date_parts) >= 2:
                # Convert month number to abbreviated month name
                month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                month = int(date_parts[1])
                year = date_parts[0]
                if 1 <= month <= 12:
                    return f"{month_names[month-1]} {year}"
            return date_str  # Return original if parsing fails
        except:
            return date_str  # Return original if any error occurs
    
    # Add bio data
    if 'bioData' in resume_data:
        bio = resume_data['bioData']
        
        # Add centered name
        elements.append(Paragraph(bio.get('name', ''), styles['Name']))
        
        # Create a single line with all contact information centered
        contact_parts = []
        
        # Add social links first
        if bio.get('github'):
            contact_parts.append(f"<a href='{bio.get('github')}' underline='1'>GitHub</a>")
        if bio.get('linkedin'):
            contact_parts.append(f"<a href='{bio.get('linkedin')}' underline='1'>LinkedIn</a>")
        if bio.get('portfolio'):
            contact_parts.append(f"<a href='{bio.get('portfolio')}' underline='1'>Portfolio</a>")
            
        # Add contact info
        if bio.get('email'):
            email = bio.get('email')
            contact_parts.append(f"<a href='mailto:{email}' underline='1'>{email}</a>")
        if bio.get('phone'):
            contact_parts.append(bio.get('phone'))
        if bio.get('location'):
            contact_parts.append(bio.get('location'))
        
        # Join all parts with separator and add to document
        if contact_parts:
            elements.append(Paragraph(' | '.join(contact_parts), styles['Contact']))
        
        # Summary/Objective
        if bio.get('summary'):
            elements.append(Paragraph('Professional Summary', styles['Heading']))
            # Add horizontal line right after the heading
            elements.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=0, spaceAfter=8))
            elements.append(Paragraph(bio.get('summary', ''), styles['ResumeNormal']))
    
    # Add skills with proficiency
    if 'skills' in resume_data and resume_data['skills']:
        elements.append(Paragraph('Skills', styles['Heading']))
        # Add horizontal line right after the heading
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=0, spaceAfter=8))
        
        # Format skills with proficiency in brackets if available
        skill_parts = []
        for skill in resume_data['skills']:
            if skill.get('name'):
                skill_text = skill.get('name')
                # Add proficiency in brackets if it exists
                if skill.get('level') and skill.get('level').strip():
                    skill_text += f" ({skill.get('level')})"
                skill_parts.append(skill_text)
        
        # Create a flowing list of skills with bullet points
        if skill_parts:
            from reportlab.platypus import Flowable
            from reportlab.lib.enums import TA_LEFT
            
            # Create a custom flowable for horizontal skills with bullets
            class HorizontalBulletList(Flowable):
                def __init__(self, items, style, bullet_char='•', gap=15, width=None):
                    self.items = items
                    self.style = style
                    self.bullet_char = bullet_char
                    self.gap = gap  # Gap between items
                    self.width = width
                    self.height = 0
                    self.item_widths = []
                    
                def wrap(self, avail_width, avail_height):
                    # Store available width for later use
                    if self.width is None:
                        self.width = avail_width
                    
                    # Calculate item widths including bullets
                    from reportlab.pdfbase.pdfmetrics import stringWidth
                    
                    self.item_widths = []
                    for item in self.items:
                        # Width of bullet + space + item
                        bullet_width = stringWidth(self.bullet_char + ' ', self.style.fontName, self.style.fontSize)
                        item_width = stringWidth(item, self.style.fontName, self.style.fontSize)
                        self.item_widths.append(bullet_width + item_width + self.gap)
                    
                    # Calculate layout (which items go on which line)
                    self.layout = []
                    current_line = []
                    current_width = 0
                    
                    for i, item_width in enumerate(self.item_widths):
                        # If adding this item exceeds available width, start a new line
                        if current_width + item_width > self.width and current_line:
                            self.layout.append(current_line)
                            current_line = [i]
                            current_width = item_width
                        else:
                            current_line.append(i)
                            current_width += item_width
                    
                    # Add the last line if not empty
                    if current_line:
                        self.layout.append(current_line)
                    
                    # Calculate height based on number of lines
                    line_height = self.style.fontSize * 1.2  # Approximate line height
                    self.height = len(self.layout) * line_height
                    
                    return (self.width, self.height)
                
                def draw(self):
                    # Draw the items according to the calculated layout
                    from reportlab.pdfbase.pdfmetrics import stringWidth
                    
                    # Set up text object for drawing
                    canvas = self.canv
                    canvas.saveState()
                    
                    # Set font according to style
                    canvas.setFont(self.style.fontName, self.style.fontSize)
                    
                    # Draw each line
                    y = self.height  # Start from top
                    line_height = self.style.fontSize * 1.2
                    
                    for line in self.layout:
                        y -= line_height
                        x = 0
                        
                        for item_idx in line:
                            # Draw bullet
                            canvas.drawString(x, y, self.bullet_char + ' ')
                            
                            # Calculate position after bullet
                            bullet_width = stringWidth(self.bullet_char + ' ', self.style.fontName, self.style.fontSize)
                            
                            # Draw item text
                            canvas.drawString(x + bullet_width, y, self.items[item_idx])
                            
                            # Move x position for next item
                            x += self.item_widths[item_idx]
                    
                    canvas.restoreState()
            
            # Create the custom horizontal bullet list
            skill_style = ParagraphStyle(
                'SkillStyle', 
                parent=styles['ResumeNormal'],
                alignment=TA_LEFT
            )
            
            # Add the custom flowable to elements
            skill_list = HorizontalBulletList(
                items=skill_parts,
                style=skill_style,
                bullet_char='•',
                gap=20  # Adjust gap between skills for ample spacing
            )
            
            elements.append(skill_list)
    
    # Add work experience with aligned dates
    if 'experience' in resume_data and resume_data['experience']:
        elements.append(Paragraph('Work Experience', styles['Heading']))
        # Add horizontal line right after the heading
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=0, spaceAfter=8))
        
        for job in resume_data['experience']:
            job_title = job.get('title', '')
            company = job.get('company', '')
            
            # Format dates in Jan 2025 format
            start_date = format_date(job.get('startDate', ''))
            
            # Handle current job vs end date
            if job.get('current'):
                date_range = f"{start_date} - Present"
            else:
                end_date = format_date(job.get('endDate', ''))
                date_range = f"{start_date} - {end_date}"
            
            # Create a table for company and location (first line)
            # Company name in bold (not italics)
            company_text = f"<b>{company}</b>"
            
            # Handle remote work vs location
            location_text = ""
            if job.get('remote'):
                location_text = "Remote"
            elif job.get('location'):
                location_text = f"{job.get('location')}"
            
            company_location_data = [[
                Paragraph(company_text, styles['ResumeNormal']),
                Paragraph(location_text, ParagraphStyle('RightAlign', parent=styles['ResumeNormal'], alignment=2))
            ]]
            
            company_location_table = Table(company_location_data, colWidths=[doc.width * 0.75, doc.width * 0.25])
            company_location_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (0, 0), 6),  # Add left padding
                ('RIGHTPADDING', (-1, 0), (-1, 0), 6),  # Add right padding
                ('TOPPADDING', (0, 0), (-1, 0), 0),  # Keep top padding at 0
                ('BOTTOMPADDING', (0, 0), (-1, 0), 2),  # Small bottom padding
            ]))
            
            elements.append(company_location_table)
            
            # Create a table for job title and duration (second line)
            # Job title and duration in italics (not bold)
            job_header_left = f"<i>{job_title}</i>"
            job_header_right = f"<i>{date_range}</i>"
            
            job_header_data = [[
                Paragraph(job_header_left, styles['ResumeNormal']),
                Paragraph(job_header_right, ParagraphStyle('RightAlign', parent=styles['ResumeNormal'], alignment=2))
            ]]
            
            # Use exact document width with no padding to align with margins
            job_header_table = Table(job_header_data, colWidths=[doc.width * 0.75, doc.width * 0.25])
            job_header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (0, 0), 6),  # Add left padding
                ('RIGHTPADDING', (-1, 0), (-1, 0), 6),  # Add right padding
                ('TOPPADDING', (0, 0), (-1, 0), 0),  # Keep top padding at 0
                ('BOTTOMPADDING', (0, 0), (-1, 0), 4),  # Bottom padding
            ]))
            
            elements.append(job_header_table)
            
            # Handle description with or without bullet points
            if job.get('description'):
                description = job.get('description', '')
                # Check if description has line breaks
                if '\n' in description:
                    # Split by line breaks and add bullet points
                    lines = description.strip().split('\n')
                    for line in lines:
                        if line.strip():  # Skip empty lines
                            elements.append(Paragraph(f"• {line.strip()}", styles['ResumeNormal']))
                else:
                    # No line breaks, display as regular paragraph
                    elements.append(Paragraph(description, styles['ResumeNormal']))
    
    # Add education with aligned dates and reordered GPA/coursework
    if 'education' in resume_data and resume_data['education']:
        elements.append(Paragraph('Education', styles['Heading']))
        # Add horizontal line right after the heading
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=0, spaceAfter=8))
        
        for edu in resume_data['education']:
            degree = edu.get('degree', '')
            institution = edu.get('institution', '')
            
            # Format dates in Jan 2025 format
            start_date = format_date(edu.get('startDate', ''))
            end_date = format_date(edu.get('endDate', ''))
            date_range = f"{start_date} - {end_date}"
            
            # Create a table for institution and location (first line)
            # Institution name in bold (not italics)
            institution_text = f"<b>{institution}</b>"
            
            # Handle location if available
            location_text = ""
            if edu.get('location'):
                location_text = f"{edu.get('location')}"
            
            institution_location_data = [[
                Paragraph(institution_text, styles['ResumeNormal']),
                Paragraph(location_text, ParagraphStyle('RightAlign', parent=styles['ResumeNormal'], alignment=2))
            ]]
            
            institution_location_table = Table(institution_location_data, colWidths=[doc.width * 0.75, doc.width * 0.25])
            institution_location_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (0, 0), 6),  # Add left padding
                ('RIGHTPADDING', (-1, 0), (-1, 0), 6),  # Add right padding
                ('TOPPADDING', (0, 0), (-1, 0), 0),  # Keep top padding at 0
                ('BOTTOMPADDING', (0, 0), (-1, 0), 2),  # Small bottom padding
            ]))
            
            elements.append(institution_location_table)
            
            # Create a table for degree and duration (second line)
            # Degree and duration in italics (not bold)
            degree_text = f"<i>{degree}</i>"
            date_range_text = f"<i>{date_range}</i>"
            
            degree_date_data = [[
                Paragraph(degree_text, styles['ResumeNormal']),
                Paragraph(date_range_text, ParagraphStyle('RightAlign', parent=styles['ResumeNormal'], alignment=2))
            ]]
            
            # Use exact document width with no padding to align with margins
            degree_date_table = Table(degree_date_data, colWidths=[doc.width * 0.75, doc.width * 0.25])
            degree_date_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (0, 0), 6),  # Add left padding
                ('RIGHTPADDING', (-1, 0), (-1, 0), 6),  # Add right padding
                ('TOPPADDING', (0, 0), (-1, 0), 0),  # Keep top padding at 0
                ('BOTTOMPADDING', (0, 0), (-1, 0), 4),  # Bottom padding
            ]))
            
            elements.append(degree_date_table)
            
            # GPA first, then coursework (reversed order)
            if edu.get('gpa'):
                elements.append(Paragraph(f"<b>GPA:</b> {edu.get('gpa', '')}", styles['ResumeNormal']))
            
            if edu.get('coursework'):
                elements.append(Paragraph(f"<b>Coursework:</b> {edu.get('coursework', '')}", styles['ResumeNormal']))
    
    # Add projects
    if 'projects' in resume_data and resume_data['projects']:
        elements.append(Paragraph('Projects', styles['Heading']))
        # Add horizontal line right after the heading
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=0, spaceAfter=8))
        
        for project in resume_data['projects']:
            project_name = project.get('name', '')
            project_link = project.get('link', '')
            
            # Create a table for project name and link (first line)
            project_name_text = f"<b>{project_name}</b>"
            
            # Handle project link
            link_text = ""
            if project_link:
                link_text = f"<a href='{project_link}'><u>Visit</u></a>"
            
            project_header_data = [[
                Paragraph(project_name_text, styles['ResumeNormal']),
                Paragraph(link_text, ParagraphStyle('RightAlign', parent=styles['ResumeNormal'], alignment=2))
            ]]
            
            project_header_table = Table(project_header_data, colWidths=[doc.width * 0.75, doc.width * 0.25])
            project_header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (0, 0), 6),  # Add left padding
                ('RIGHTPADDING', (-1, 0), (-1, 0), 6),  # Add right padding
                ('TOPPADDING', (0, 0), (-1, 0), 0),  # Keep top padding at 0
                ('BOTTOMPADDING', (0, 0), (-1, 0), 4),  # Bottom padding
            ]))
            
            elements.append(project_header_table)
            
            # Handle description with or without bullet points
            if project.get('description'):
                description = project.get('description', '')
                # Check if description has line breaks
                if '\n' in description:
                    # Split by line breaks and add bullet points
                    lines = description.strip().split('\n')
                    for line in lines:
                        if line.strip():  # Skip empty lines
                            elements.append(Paragraph(f"• {line.strip()}", styles['ResumeNormal']))
                else:
                    # No line breaks, display as regular paragraph
                    elements.append(Paragraph(description, styles['ResumeNormal']))
    
    # Add achievements
    if 'achievements' in resume_data and resume_data['achievements']:
        elements.append(Paragraph('Achievements', styles['Heading']))
        # Add horizontal line right after the heading
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=0, spaceAfter=8))
        
        for achievement in resume_data['achievements']:
            # Handle description with or without bullet points
            if achievement.get('description'):
                description = achievement.get('description', '')
                # Check if description has line breaks
                if '\n' in description:
                    # Split by line breaks and add bullet points
                    lines = description.strip().split('\n')
                    for line in lines:
                        if line.strip():  # Skip empty lines
                            elements.append(Paragraph(f"• {line.strip()}", styles['ResumeNormal']))
                else:
                    # No line breaks, display as regular paragraph
                    elements.append(Paragraph(description, styles['ResumeNormal']))
    
    # Generate a unique filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"resume_{timestamp}.pdf"
    output_path = os.path.join('static', 'generated_resumes', filename)
    
    # Build the PDF
    doc.build(elements)
    
    # Save the PDF to a file
    with open(output_path, 'wb') as f:
        f.write(buffer.getvalue())
    
    # Return success response with file path
    return jsonify({
        'success': True,
        'filename': filename,
        'path': output_path,  # Change this from output_path_url to output_path
    })

@app.route('/serve_resume/<filename>')
def serve_resume(filename):
    return send_file(os.path.join('uploads', filename))

@app.route('/save_template', methods=['POST'])
def save_template():
    # Get form data
    resume_data = request.json
    
    # Create a unique filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"template_{timestamp}.json"
    output_path = os.path.join('static', 'resume_templates', filename)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the template
    try:
        with open(output_path, 'w') as f:
            json.dump(resume_data, f)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'success': True, 'message': 'Template saved successfully'})

@app.route('/load_templates', methods=['GET'])
def load_templates():
    templates_dir = os.path.join('static', 'resume_templates')
    
    # Ensure directory exists
    os.makedirs(templates_dir, exist_ok=True)
    
    templates = []
    for filename in os.listdir(templates_dir):
        if filename.endswith('.json'):
            template_path = os.path.join(templates_dir, filename)
            try:
                with open(template_path, 'r') as f:
                    template_data = json.load(f)
                    templates.append({
                        'id': filename,
                        'name': template_data.get('bioData', {}).get('name', 'Unnamed Template'),
                        'data': template_data
                    })
            except Exception as e:
                print(f"Error loading template {filename}: {e}")
    
    return jsonify({'templates': templates})

if __name__ == '__main__':
    app.run(debug=True, port=5001)