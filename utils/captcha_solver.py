import os
import logging
import requests
import base64
from io import BytesIO
from PIL import Image
import time

logger = logging.getLogger(__name__)

class CaptchaSolver:
    """CAPTCHA solving utility with automated and manual options"""
    
    def __init__(self):
        self.api_key = os.getenv('CAPTCHA_API_KEY')
        self.api_url = "http://2captcha.com/in.php"
        self.result_url = "http://2captcha.com/res.php"
        
    def solve_captcha(self, captcha_src):
        """Solve CAPTCHA using automated service or manual input"""
        try:
            # Download CAPTCHA image
            captcha_image = self._download_captcha(captcha_src)
            if not captcha_image:
                return None
            
            # Try automated solving first
            if self.api_key:
                result = self._solve_automated(captcha_image)
                if result:
                    return result
            
            # Fallback to manual solving
            return self._solve_manual(captcha_image)
            
        except Exception as e:
            logger.error(f"Error solving CAPTCHA: {str(e)}")
            return None
    
    def _download_captcha(self, captcha_src):
        """Download CAPTCHA image from URL"""
        try:
            # Handle data URLs
            if captcha_src.startswith('data:image'):
                # Extract base64 data
                header, data = captcha_src.split(',', 1)
                image_data = base64.b64decode(data)
                return Image.open(BytesIO(image_data))
            
            # Handle regular URLs
            response = requests.get(captcha_src, timeout=10)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
            
        except Exception as e:
            logger.error(f"Error downloading CAPTCHA: {str(e)}")
            return None
    
    def _solve_automated(self, captcha_image):
        """Solve CAPTCHA using 2captcha API"""
        try:
            if not self.api_key:
                return None
            
            # Convert image to base64
            buffer = BytesIO()
            captcha_image.save(buffer, format='PNG')
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Submit to 2captcha
            data = {
                'key': self.api_key,
                'method': 'base64',
                'body': image_base64,
                'json': 1
            }
            
            response = requests.post(self.api_url, data=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if result.get('status') == 1:
                request_id = result.get('request')
                
                # Wait for solution
                for _ in range(30):  # Wait up to 30 seconds
                    time.sleep(1)
                    
                    result_response = requests.get(
                        f"{self.result_url}?key={self.api_key}&action=get&id={request_id}&json=1",
                        timeout=10
                    )
                    result_response.raise_for_status()
                    
                    result_data = result_response.json()
                    if result_data.get('status') == 1:
                        return result_data.get('request')
                    elif result_data.get('request') == 'CAPCHA_NOT_READY':
                        continue
                    else:
                        break
            
            logger.warning("Automated CAPTCHA solving failed")
            return None
            
        except Exception as e:
            logger.error(f"Error in automated CAPTCHA solving: {str(e)}")
            return None
    
    def _solve_manual(self, captcha_image):
        """Manual CAPTCHA solving fallback"""
        try:
            # Save CAPTCHA image for manual solving
            captcha_path = os.path.join('static', 'temp', 'captcha.png')
            os.makedirs(os.path.dirname(captcha_path), exist_ok=True)
            captcha_image.save(captcha_path)
            
            logger.info(f"CAPTCHA image saved to {captcha_path}")
            logger.info("Please solve the CAPTCHA manually and enter the text")
            
            # In a real implementation, you might want to:
            # 1. Display the image in the UI
            # 2. Provide an input field for manual entry
            # 3. Wait for user input
            
            # For now, we'll return None to indicate manual solving needed
            return None
            
        except Exception as e:
            logger.error(f"Error in manual CAPTCHA solving: {str(e)}")
            return None
    
    def validate_captcha(self, captcha_text):
        """Validate CAPTCHA text format"""
        if not captcha_text:
            return False
        
        # Basic validation - CAPTCHA should be alphanumeric and 4-8 characters
        if not captcha_text.isalnum() or len(captcha_text) < 4 or len(captcha_text) > 8:
            return False
        
        return True 