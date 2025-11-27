"""
Africa's Talking Service Integration
SMS, USSD, Voice, and Airtime services for lead generation and outreach.
"""

import os
import requests
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class AfricasTalkingService:
    """
    Integration with Africa's Talking API for SMS, USSD, Voice, and Airtime.
    """
    
    def __init__(self):
        self.username = os.getenv('AFRICASTALKING_USERNAME')
        self.api_key = os.getenv('AFRICASTALKING_API_KEY')
        self.sandbox = os.getenv('AFRICASTALKING_SANDBOX', 'true').lower() == 'true'
        
        if not self.username or not self.api_key:
            logger.warning("Africa's Talking credentials not configured")
            self.enabled = False
        else:
            self.enabled = True
            self.base_url = "https://api.sandbox.africastalking.com" if self.sandbox else "https://api.africastalking.com"
    
    def send_sms(self, phone_numbers: List[str], message: str, sender_id: Optional[str] = None) -> Dict:
        """
        Send SMS to phone numbers.
        
        Args:
            phone_numbers: List of phone numbers (with country code, e.g., +254712345678)
            message: SMS message text (max 160 characters for single SMS)
            sender_id: Optional sender ID (must be approved)
        
        Returns:
            Dict with send status
        """
        if not self.enabled:
            return {'success': False, 'error': "Africa's Talking not configured"}
        
        url = f"{self.base_url}/version1/messaging"
        
        headers = {
            'ApiKey': self.api_key,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        # Format phone numbers (ensure + prefix)
        formatted_numbers = []
        for number in phone_numbers:
            # Remove spaces and ensure + prefix
            number = number.replace(' ', '').replace('-', '')
            if not number.startswith('+'):
                # Try to add country code if missing
                if number.startswith('0'):
                    # Kenyan number - add +254
                    number = '+254' + number[1:]
                else:
                    number = '+' + number
            formatted_numbers.append(number)
        
        data = {
            'username': self.username,
            'to': ','.join(formatted_numbers),
            'message': message
        }
        
        if sender_id:
            data['from'] = sender_id
        
        try:
            response = requests.post(url, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            return {
                'success': True,
                'message': 'SMS sent successfully',
                'recipients': result.get('SMSMessageData', {}).get('Recipients', []),
                'cost': result.get('SMSMessageData', {}).get('cost', '0')
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending SMS: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_lead_notification_sms(self, phone: str, lead_summary: Dict) -> Dict:
        """
        Send SMS notification when leads are generated.
        
        Args:
            phone: Phone number with country code
            lead_summary: Summary of generated leads
        """
        total_leads = lead_summary.get('total', 0)
        premium_leads = lead_summary.get('premium', 0)
        high_leads = lead_summary.get('high', 0)
        
        message = f"""LeadGen AI: Generated {total_leads} leads!
Premium: {premium_leads} | High: {high_leads}
View: {lead_summary.get('dashboard_url', 'your-dashboard')}"""
        
        return self.send_sms([phone], message)
    
    def send_lead_details_sms(self, phone: str, company_name: str, contact_email: str, website: str) -> Dict:
        """
        Send detailed lead information via SMS.
        """
        # Truncate for SMS length
        company_name = company_name[:30] if len(company_name) > 30 else company_name
        message = f"""New Lead: {company_name}
Email: {contact_email}
Web: {website[:30]}
- LeadGen AI"""
        
        return self.send_sms([phone], message)
    
    def initiate_voice_call(self, phone_number: str, message: str) -> Dict:
        """
        Initiate a voice call with text-to-speech.
        
        Args:
            phone_number: Phone number with country code
            message: Text to convert to speech
        
        Returns:
            Dict with call status
        """
        if not self.enabled:
            return {'success': False, 'error': "Africa's Talking not configured"}
        
        url = f"{self.base_url}/voice/call"
        
        headers = {
            'ApiKey': self.api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Format phone number
        phone_number = phone_number.replace(' ', '').replace('-', '')
        if not phone_number.startswith('+'):
            if phone_number.startswith('0'):
                phone_number = '+254' + phone_number[1:]
            else:
                phone_number = '+' + phone_number
        
        data = {
            'username': self.username,
            'to': phone_number,
            'from': self.username,  # Or use approved caller ID
            'message': message
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            return {
                'success': True,
                'message': 'Voice call initiated',
                'data': response.json()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error initiating voice call: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_airtime(self, phone_number: str, amount: str, currency: str = 'KES') -> Dict:
        """
        Send airtime to a phone number (for rewards/incentives).
        
        Args:
            phone_number: Phone number with country code
            amount: Amount to send (e.g., "100")
            currency: Currency code (KES, UGX, TZS, etc.)
        """
        if not self.enabled:
            return {'success': False, 'error': "Africa's Talking not configured"}
        
        url = f"{self.base_url}/version1/airtime/send"
        
        headers = {
            'ApiKey': self.api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Format phone number
        phone_number = phone_number.replace(' ', '').replace('-', '')
        if not phone_number.startswith('+'):
            if phone_number.startswith('0'):
                phone_number = '+254' + phone_number[1:]
            else:
                phone_number = '+' + phone_number
        
        data = {
            'username': self.username,
            'recipients': [{
                'phoneNumber': phone_number,
                'amount': f"{currency} {amount}"
            }]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            return {
                'success': True,
                'message': 'Airtime sent successfully',
                'data': result
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending airtime: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_ussd_menu(self, phone_number: str, menu_text: str) -> Dict:
        """
        Create USSD menu for lead requests.
        
        Args:
            phone_number: Phone number to send USSD to
            menu_text: USSD menu text
        """
        if not self.enabled:
            return {'success': False, 'error': "Africa's Talking not configured"}
        
        # USSD is typically handled via callback URLs
        # This is a placeholder for USSD integration
        return {
            'success': True,
            'message': 'USSD menu created (requires callback URL setup)',
            'note': 'USSD requires callback URL configuration in Africa\'s Talking dashboard'
        }


def get_africastalking_service() -> Optional[AfricasTalkingService]:
    """Get Africa's Talking service instance if configured"""
    try:
        service = AfricasTalkingService()
        if service.enabled:
            return service
        return None
    except Exception as e:
        logger.warning(f"Africa's Talking service not available: {str(e)}")
        return None

