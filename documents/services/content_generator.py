# documents/services/content_generator.py
import os
import tempfile
from django.conf import settings
from .wps_automation import WPSAutomation
from .ai_integration import DeepSeekIntegration

class ContentGenerator:
    def __init__(self):
        self.wps_auto = WPSAutomation()
        self.ai_service = DeepSeekIntegration()
    
    def generate_academic_paper(self, topic, requirements, user):
        """Generate complete academic paper"""
        try:
            # Step 1: Generate content with AI
            content = self.ai_service.generate_academic_content(topic, requirements)
            
            # Step 2: Create WPS document
            output_filename = f"academic_paper_{user.id}_{int(os.times().elapsed)}.docx"
            output_path = os.path.join(settings.MEDIA_ROOT, 'documents', output_filename)
            
            # Initialize WPS and create document
            if not self.wps_auto.initialize_wps():
                raise Exception("Failed to initialize WPS Office")
            
            self.wps_auto.create_document()
            
            # Step 3: Apply document styles
            self.wps_auto.apply_document_styles()
            
            # Step 4: Insert content with proper formatting
            self._insert_formatted_content(content, requirements)
            
            # Step 5: Save document
            self.wps_auto.save_document(output_path)
            
            # Step 6: Clean up
            self.wps_auto.close()
            
            return output_path, content
            
        except Exception as e:
            # Ensure cleanup on error
            try:
                self.wps_auto.close()
            except:
                pass
            raise e
    
    def generate_business_report(self, topic, requirements, user):
        """Generate complete business report"""
        try:
            # Step 1: Generate content with AI
            content = self.ai_service.generate_business_content(topic, requirements)
            
            # Step 2: Create WPS document
            output_filename = f"business_report_{user.id}_{int(os.times().elapsed)}.docx"
            output_path = os.path.join(settings.MEDIA_ROOT, 'documents', output_filename)
            
            # Initialize WPS and create document
            if not self.wps_auto.initialize_wps():
                raise Exception("Failed to initialize WPS Office")
            
            self.wps_auto.create_document()
            
            # Step 3: Apply document styles
            self.wps_auto.apply_document_styles()
            
            # Step 4: Insert content with proper formatting
            self._insert_formatted_content(content, requirements)
            
            # Step 5: Save document
            self.wps_auto.save_document(output_path)
            
            # Step 6: Clean up
            self.wps_auto.close()
            
            return output_path, content
            
        except Exception as e:
            # Ensure cleanup on error
            try:
                self.wps_auto.close()
            except:
                pass
            raise e
    
    def _insert_formatted_content(self, content, requirements):
        """Insert content with proper formatting"""
        # Split content by sections
        sections = self._parse_content_sections(content)
        
        for section in sections:
            if section['is_heading']:
                # Insert as heading
                level = self._get_heading_level(section['title'])
                self.wps_auto.insert_heading(section['title'], level)
            else:
                # Insert as normal content
                self.wps_auto.insert_content(section['content'])
    
    def _parse_content_sections(self, content):
        """Parse content into sections"""
        sections = []
        lines = content.split('\n')
        
        current_section = {'title': '', 'content': '', 'is_heading': False}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a heading (contains numbers or specific keywords)
            if (any(keyword in line for keyword in ['摘要', '引言', '结论', '参考文献', 
                                                  'Abstract', 'Introduction', 'Conclusion', 'References']) and
                len(line) < 100):  # Likely a heading
                
                # Save previous section
                if current_section['content']:
                    sections.append(current_section.copy())
                
                # Start new section
                current_section = {
                    'title': line,
                    'content': '',
                    'is_heading': True
                }
            else:
                # Add to current section content
                current_section['content'] += line + '\n'
                current_section['is_heading'] = False
        
        # Add the last section
        if current_section['content']:
            sections.append(current_section)
        
        return sections
    
    def _get_heading_level(self, title):
        """Determine heading level based on title content"""
        if any(keyword in title for keyword in ['摘要', 'Abstract', '引言', 'Introduction', '结论', 'Conclusion']):
            return 1
        elif any(keyword in title for keyword in ['文献综述', '研究方法', '研究结果', '讨论', 
                                                'Literature Review', 'Methodology', 'Findings', 'Discussion']):
            return 2
        else:
            return 3