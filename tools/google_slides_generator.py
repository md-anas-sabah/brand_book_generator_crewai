"""
Google Slides Brand Book Generator
Creates web-editable presentations using Google Slides API
"""

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path
import json

class GoogleSlidesBrandBookGenerator:
    """Generate brand books using Google Slides API for live web editing"""
    
    # Scopes required for Google Slides API
    SCOPES = ['https://www.googleapis.com/auth/presentations']
    
    def __init__(self):
        self.service = None
        self.presentation_id = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Slides API"""
        creds = None
        
        # Token.pickle stores the user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('slides', 'v1', credentials=creds)
        print("✅ Authenticated with Google Slides API")
    
    def create_presentation(self, title):
        """Create a new Google Slides presentation"""
        presentation = {'title': title}
        presentation_response = self.service.presentations().create(body=presentation).execute()
        self.presentation_id = presentation_response['presentationId']
        
        # Get the presentation URL
        presentation_url = f"https://docs.google.com/presentation/d/{self.presentation_id}/edit"
        
        print(f"📊 Created presentation: {title}")
        print(f"🌐 Live edit URL: {presentation_url}")
        return self.presentation_id, presentation_url
    
    def _hex_to_rgb_normalized(self, hex_color):
        """Convert hex to normalized RGB (0-1 range)"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        try:
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            return tuple(c/255.0 for c in rgb)  # Normalize to 0-1 range
        except:
            return (0.18, 0.52, 0.67)  # Default blue
    
    def add_title_slide(self, company_name, identity_data):
        """Add professional title slide"""
        palette = identity_data.get("palette", {})
        primary_color = palette.get("primary", "#2E86AB")
        
        requests = [
            # Create slide
            {
                'createSlide': {
                    'objectId': 'title_slide',
                    'insertionIndex': 1,
                    'slideLayoutReference': {
                        'predefinedLayout': 'BLANK'
                    }
                }
            },
            # Add background
            {
                'updatePageProperties': {
                    'objectId': 'title_slide',
                    'pageProperties': {
                        'pageBackgroundFill': {
                            'solidFill': {
                                'color': {
                                    'rgbColor': {
                                        'red': self._hex_to_rgb_normalized(primary_color)[0],
                                        'green': self._hex_to_rgb_normalized(primary_color)[1],
                                        'blue': self._hex_to_rgb_normalized(primary_color)[2]
                                    }
                                }
                            }
                        }
                    },
                    'fields': 'pageBackgroundFill'
                }
            },
            # Add company name text box
            {
                'createShape': {
                    'objectId': 'title_text',
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                        'pageObjectId': 'title_slide',
                        'size': {
                            'height': {'magnitude': 100, 'unit': 'PT'},
                            'width': {'magnitude': 600, 'unit': 'PT'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': 50,
                            'translateY': 200,
                            'unit': 'PT'
                        }
                    }
                }
            },
            # Add subtitle text box
            {
                'createShape': {
                    'objectId': 'subtitle_text',
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                        'pageObjectId': 'title_slide',
                        'size': {
                            'height': {'magnitude': 50, 'unit': 'PT'},
                            'width': {'magnitude': 400, 'unit': 'PT'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': 150,
                            'translateY': 320,
                            'unit': 'PT'
                        }
                    }
                }
            }
        ]
        
        # Execute slide creation
        self.service.presentations().batchUpdate(
            presentationId=self.presentation_id,
            body={'requests': requests}
        ).execute()
        
        # Add text content
        text_requests = [
            # Company name text
            {
                'insertText': {
                    'objectId': 'title_text',
                    'text': company_name,
                    'insertionIndex': 0
                }
            },
            # Subtitle text
            {
                'insertText': {
                    'objectId': 'subtitle_text',
                    'text': 'Brand Book',
                    'insertionIndex': 0
                }
            },
            # Style company name
            {
                'updateTextStyle': {
                    'objectId': 'title_text',
                    'style': {
                        'fontSize': {'magnitude': 48, 'unit': 'PT'},
                        'bold': True,
                        'foregroundColor': {
                            'opaqueColor': {
                                'rgbColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}
                            }
                        }
                    },
                    'fields': 'fontSize,bold,foregroundColor'
                }
            },
            # Style subtitle
            {
                'updateTextStyle': {
                    'objectId': 'subtitle_text',
                    'style': {
                        'fontSize': {'magnitude': 24, 'unit': 'PT'},
                        'foregroundColor': {
                            'opaqueColor': {
                                'rgbColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}
                            }
                        }
                    },
                    'fields': 'fontSize,foregroundColor'
                }
            }
        ]
        
        self.service.presentations().batchUpdate(
            presentationId=self.presentation_id,
            body={'requests': text_requests}
        ).execute()
        
        print("📄 Added title slide")
    
    def add_content_slide(self, title, content, slide_id):
        """Add a content slide with title and body text"""
        requests = [
            # Create slide
            {
                'createSlide': {
                    'objectId': slide_id,
                    'slideLayoutReference': {
                        'predefinedLayout': 'TITLE_AND_BODY'
                    }
                }
            }
        ]
        
        self.service.presentations().batchUpdate(
            presentationId=self.presentation_id,
            body={'requests': requests}
        ).execute()
        
        # Get slide objects to add text
        presentation = self.service.presentations().get(presentationId=self.presentation_id).execute()
        slides = presentation.get('slides', [])
        
        # Find the slide we just created
        current_slide = None
        for slide in slides:
            if slide['objectId'] == slide_id:
                current_slide = slide
                break
        
        if current_slide:
            page_elements = current_slide.get('pageElements', [])
            title_shape_id = None
            body_shape_id = None
            
            # Find title and body shapes
            for element in page_elements:
                if 'shape' in element:
                    shape = element['shape']
                    if shape.get('placeholder', {}).get('type') == 'TITLE':
                        title_shape_id = element['objectId']
                    elif shape.get('placeholder', {}).get('type') == 'BODY':
                        body_shape_id = element['objectId']
            
            # Add text to shapes
            text_requests = []
            if title_shape_id:
                text_requests.append({
                    'insertText': {
                        'objectId': title_shape_id,
                        'text': title,
                        'insertionIndex': 0
                    }
                })
            
            if body_shape_id:
                text_requests.append({
                    'insertText': {
                        'objectId': body_shape_id,
                        'text': content,
                        'insertionIndex': 0
                    }
                })
            
            if text_requests:
                self.service.presentations().batchUpdate(
                    presentationId=self.presentation_id,
                    body={'requests': text_requests}
                ).execute()
        
        print(f"📄 Added content slide: {title}")
    
    def add_color_palette_slide(self, palette, identity_data):
        """Add color palette slide with actual color swatches"""
        slide_id = 'color_palette_slide'
        
        # Create blank slide
        requests = [
            {
                'createSlide': {
                    'objectId': slide_id,
                    'slideLayoutReference': {
                        'predefinedLayout': 'BLANK'
                    }
                }
            },
            # Add title
            {
                'createShape': {
                    'objectId': 'palette_title',
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                        'pageObjectId': slide_id,
                        'size': {
                            'height': {'magnitude': 60, 'unit': 'PT'},
                            'width': {'magnitude': 400, 'unit': 'PT'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': 200,
                            'translateY': 50,
                            'unit': 'PT'
                        }
                    }
                }
            }
        ]
        
        # Add color swatches
        x_start = 100
        y_position = 150
        swatch_width = 120
        spacing = 140
        
        for i, (color_name, hex_code) in enumerate(palette.items()):
            if isinstance(hex_code, list):
                hex_code = hex_code[0] if hex_code else "#CCCCCC"
            
            swatch_id = f'color_swatch_{i}'
            label_id = f'color_label_{i}'
            
            rgb_color = self._hex_to_rgb_normalized(hex_code)
            
            # Color swatch rectangle
            requests.extend([
                {
                    'createShape': {
                        'objectId': swatch_id,
                        'shapeType': 'RECTANGLE',
                        'elementProperties': {
                            'pageObjectId': slide_id,
                            'size': {
                                'height': {'magnitude': 80, 'unit': 'PT'},
                                'width': {'magnitude': swatch_width, 'unit': 'PT'}
                            },
                            'transform': {
                                'scaleX': 1,
                                'scaleY': 1,
                                'translateX': x_start + i * spacing,
                                'translateY': y_position,
                                'unit': 'PT'
                            }
                        }
                    }
                },
                # Color the swatch
                {
                    'updateShapeProperties': {
                        'objectId': swatch_id,
                        'shapeProperties': {
                            'shapeBackgroundFill': {
                                'solidFill': {
                                    'color': {
                                        'rgbColor': {
                                            'red': rgb_color[0],
                                            'green': rgb_color[1],
                                            'blue': rgb_color[2]
                                        }
                                    }
                                }
                            }
                        },
                        'fields': 'shapeBackgroundFill'
                    }
                },
                # Color label
                {
                    'createShape': {
                        'objectId': label_id,
                        'shapeType': 'TEXT_BOX',
                        'elementProperties': {
                            'pageObjectId': slide_id,
                            'size': {
                                'height': {'magnitude': 40, 'unit': 'PT'},
                                'width': {'magnitude': swatch_width, 'unit': 'PT'}
                            },
                            'transform': {
                                'scaleX': 1,
                                'scaleY': 1,
                                'translateX': x_start + i * spacing,
                                'translateY': y_position + 90,
                                'unit': 'PT'
                            }
                        }
                    }
                }
            ])
        
        # Execute all requests
        self.service.presentations().batchUpdate(
            presentationId=self.presentation_id,
            body={'requests': requests}
        ).execute()
        
        # Add text content
        text_requests = [
            {
                'insertText': {
                    'objectId': 'palette_title',
                    'text': 'Color Palette',
                    'insertionIndex': 0
                }
            },
            {
                'updateTextStyle': {
                    'objectId': 'palette_title',
                    'style': {
                        'fontSize': {'magnitude': 32, 'unit': 'PT'},
                        'bold': True
                    },
                    'fields': 'fontSize,bold'
                }
            }
        ]
        
        # Add labels for each color
        for i, (color_name, hex_code) in enumerate(palette.items()):
            if isinstance(hex_code, list):
                hex_code = hex_code[0] if hex_code else "#CCCCCC"
            
            label_id = f'color_label_{i}'
            text_requests.extend([
                {
                    'insertText': {
                        'objectId': label_id,
                        'text': f"{color_name.title()}\\n{hex_code}",
                        'insertionIndex': 0
                    }
                },
                {
                    'updateTextStyle': {
                        'objectId': label_id,
                        'style': {
                            'fontSize': {'magnitude': 12, 'unit': 'PT'},
                        },
                        'fields': 'fontSize'
                    }
                }
            ])
        
        self.service.presentations().batchUpdate(
            presentationId=self.presentation_id,
            body={'requests': text_requests}
        ).execute()
        
        print("🎨 Added color palette slide")
    
    def create_brand_book(self, company_name, identity_data, literature_data, brand_essence=None):
        """Create complete brand book in Google Slides"""
        
        # Create presentation
        presentation_id, presentation_url = self.create_presentation(f"{company_name} - Brand Book")
        
        # Add title slide
        self.add_title_slide(company_name, identity_data)
        
        # Add company profile
        if brand_essence and brand_essence.get("company_profile"):
            profile = brand_essence["company_profile"]
            content = f"""Company: {profile.get('name', company_name)}
Industry: {profile.get('industry', 'N/A')}
Target Audience: {profile.get('target_audience', 'N/A')}

Core Values:
{chr(10).join(['• ' + value for value in profile.get('core_values', [])])}"""
            self.add_content_slide("Company Profile", content, "company_profile")
        
        # Add color palette with visual swatches
        if identity_data.get("palette"):
            self.add_color_palette_slide(identity_data["palette"], identity_data)
        
        # Add brand story
        if literature_data.get("brand_story"):
            self.add_content_slide("Brand Story & Mission", literature_data["brand_story"], "brand_story")
        
        # Add voice & tone
        if literature_data.get("voice_tone"):
            self.add_content_slide("Brand Voice & Tone", literature_data["voice_tone"], "voice_tone")
        
        print(f"🎉 Brand book created successfully!")
        print(f"🌐 Edit live at: {presentation_url}")
        return presentation_id, presentation_url

# Setup instructions for users
def setup_google_slides_api():
    """Instructions for setting up Google Slides API"""
    instructions = """
    📋 GOOGLE SLIDES API SETUP INSTRUCTIONS:

    1. Go to Google Cloud Console: https://console.cloud.google.com/
    2. Create a new project or select existing project
    3. Enable the Google Slides API:
       - Go to "APIs & Services" > "Library"
       - Search for "Google Slides API"
       - Click "Enable"
    
    4. Create credentials:
       - Go to "APIs & Services" > "Credentials" 
       - Click "Create Credentials" > "OAuth client ID"
       - Choose "Desktop application"
       - Download the JSON file
       - Rename it to "credentials.json" and place in your project directory
    
    5. Install required packages:
       pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
    
    6. Run the script - it will open a browser for authentication on first run
    
    🔐 Your presentations will be created in your Google Drive and can be edited by anyone with the link!
    """
    print(instructions)

# Example usage
if __name__ == "__main__":
    # Print setup instructions
    setup_google_slides_api()
    
    # Example data
    identity_data = {
        "palette": {"primary": "#2E86AB", "secondary": "#A23B72", "accent": "#F18F01"}
    }
    literature_data = {
        "brand_story": "We revolutionize technology through innovative design and human-centered solutions.",
        "voice_tone": "Professional, innovative, approachable, and trustworthy."
    }
    brand_essence = {
        "company_profile": {
            "name": "TechForward Inc",
            "industry": "Technology",
            "target_audience": "Progressive businesses seeking digital transformation",
            "core_values": ["Innovation", "Simplicity", "Excellence", "Trust"]
        }
    }
    
    # Uncomment to create presentation (after setting up credentials)
    # generator = GoogleSlidesBrandBookGenerator()
    # presentation_id, url = generator.create_brand_book("TechForward Inc", identity_data, literature_data, brand_essence)