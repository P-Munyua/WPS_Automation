# documents/services/wps_automation.py
import os
import pythoncom
from django.conf import settings
from django.utils import timezone

class WPSAutomation:
    def __init__(self):
        self.wps_app = None
        self.doc = None
        self.initialized = False
    
    def initialize_wps(self):
        """Initialize WPS Application"""
        try:
            pythoncom.CoInitialize()
            import win32com.client
            self.wps_app = win32com.client.Dispatch("KWPS.Application")
            self.wps_app.Visible = False  # Run in background
            self.initialized = True
            return True
        except Exception as e:
            print(f"WPS Initialization Error: {e}")
            return False
    
    def create_document(self, template_path=None):
        """Create new document with optional template"""
        if not self.initialized:
            if not self.initialize_wps():
                raise Exception("Failed to initialize WPS")
        
        try:
            if template_path and os.path.exists(template_path):
                self.doc = self.wps_app.Documents.Add(template_path)
            else:
                self.doc = self.wps_app.Documents.Add()
            return True
        except Exception as e:
            raise Exception(f"Failed to create document: {e}")
    
    def insert_content(self, content, style="Normal"):
        """Insert content into document with specified style"""
        try:
            # Select the end of document
            self.doc.Range().InsertAfter(content)
            
            # Apply style if needed
            if style != "Normal":
                # Get the last paragraph and apply style
                paragraphs = self.doc.Paragraphs
                if paragraphs.Count > 0:
                    last_paragraph = paragraphs(paragraphs.Count)
                    try:
                        last_paragraph.Style = style
                    except:
                        pass  # Style might not exist
            
            return True
        except Exception as e:
            raise Exception(f"Failed to insert content: {e}")
    
    def insert_heading(self, text, level=1):
        """Insert heading with specified level"""
        try:
            # Add heading
            self.insert_content(f"\n{text}\n")
            
            # Apply heading style
            paragraphs = self.doc.Paragraphs
            if paragraphs.Count > 0:
                heading_paragraph = paragraphs(paragraphs.Count - 1)
                try:
                    if level == 1:
                        heading_paragraph.Style = "Heading 1"
                    elif level == 2:
                        heading_paragraph.Style = "Heading 2"
                    elif level == 3:
                        heading_paragraph.Style = "Heading 3"
                except:
                    # If heading styles don't exist, make it bold and larger
                    heading_paragraph.Range.Font.Bold = True
                    heading_paragraph.Range.Font.Size = 16 - (level * 2)
            
            return True
        except Exception as e:
            raise Exception(f"Failed to insert heading: {e}")
    
    def insert_table(self, data, rows, cols):
        """Insert a table with data"""
        try:
            # Add table
            self.insert_content("\n")  # Add space before table
            range_obj = self.doc.Range()
            table = self.doc.Tables.Add(range_obj, rows, cols)
            
            # Populate table data
            for i, row_data in enumerate(data):
                for j, cell_data in enumerate(row_data):
                    if i < rows and j < cols:
                        table.Cell(i + 1, j + 1).Range.Text = str(cell_data)
            
            # Apply table style
            try:
                table.Style = "Grid Table 1 Light"
            except:
                pass  # Table style might not exist
            
            return True
        except Exception as e:
            raise Exception(f"Failed to insert table: {e}")
    
    def apply_document_styles(self):
        """Apply professional document styling"""
        try:
            # Page setup
            page_setup = self.doc.PageSetup
            page_setup.TopMargin = 72  # 1 inch
            page_setup.BottomMargin = 72
            page_setup.LeftMargin = 72
            page_setup.RightMargin = 72
            
            # Set default font
            self.doc.Content.Font.Name = "Times New Roman"
            self.doc.Content.Font.Size = 12
            
            return True
        except Exception as e:
            print(f"Style application warning: {e}")
            return True  # Non-critical, continue
    
    def save_document(self, file_path):
        """Save document to specified path"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save document
            self.doc.SaveAs(file_path)
            return True
        except Exception as e:
            raise Exception(f"Failed to save document: {e}")
    
    def close(self):
        """Clean up WPS application"""
        try:
            if self.doc:
                self.doc.Close(SaveChanges=False)
            if self.wps_app:
                self.wps_app.Quit()
            pythoncom.CoUninitialize()
            self.initialized = False
        except Exception as e:
            print(f"Warning during WPS cleanup: {e}")