"""
Notification manager for MapLeads
Handles email and webhook notifications for new businesses
"""

import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from datetime import datetime

class NotificationManager:
    def __init__(self, config: Dict):
        """Initialize notification manager with config"""
        self.config = config.get('notifications', {})
        self.email_config = self.config.get('email', {})
        self.webhook_config = self.config.get('webhook', {})
        self.filters = self.config.get('filters', {})
    
    def send_notifications(self, new_businesses: List[Dict]):
        """Send notifications for new businesses"""
        if not new_businesses:
            return
        
        # Apply filters
        filtered_businesses = self._apply_filters(new_businesses)
        
        if not filtered_businesses:
            print("No businesses passed notification filters")
            return
        
        # Send email notification
        if self.email_config.get('enabled'):
            self._send_email_notification(filtered_businesses)
        
        # Send webhook notification
        if self.webhook_config.get('enabled'):
            self._send_webhook_notification(filtered_businesses)
    
    def _apply_filters(self, businesses: List[Dict]) -> List[Dict]:
        """Apply notification filters to businesses"""
        filtered = []
        
        for business in businesses:
            # Check website filter
            if self.filters.get('only_with_website') and not business.get('website'):
                continue
            
            # Check reviews filters
            reviews = business.get('reviews', '')
            has_reviews = reviews.lower() != 'no reviews' and reviews != ''
            
            if self.filters.get('only_with_reviews') and not has_reviews:
                continue
            
            if self.filters.get('only_without_reviews') and has_reviews:
                continue
            
            # Check rating filter
            min_rating = self.filters.get('min_rating')
            if min_rating and business.get('rating'):
                if business['rating'] < min_rating:
                    continue
            
            filtered.append(business)
        
        return filtered
    
    def _send_email_notification(self, businesses: List[Dict]):
        """Send email notification"""
        try:
            # Create email content
            subject = f"MapLeads: {len(businesses)} New Businesses Found"
            
            # Create HTML email
            html_content = self._create_email_html(businesses)
            
            # Setup email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_config['email']
            msg['To'] = ', '.join(self.email_config['recipients'])
            
            # Attach HTML
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['email'], self.email_config['password'])
                server.send_message(msg)
            
            print(f"✉️ Email notification sent to {len(self.email_config['recipients'])} recipients")
            
        except Exception as e:
            print(f"Failed to send email notification: {e}")
    
    def _create_email_html(self, businesses: List[Dict]) -> str:
        """Create HTML content for email"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .business {{ border: 1px solid #ddd; margin: 10px; padding: 15px; border-radius: 5px; }}
                .business h3 {{ color: #333; margin-top: 0; }}
                .info {{ margin: 5px 0; }}
                .label {{ font-weight: bold; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>MapLeads Alert</h2>
                <p>{len(businesses)} New Businesses Discovered</p>
            </div>
            <div style="padding: 20px;">
                <p>The following new businesses were found in your monitored areas:</p>
        """
        
        for business in businesses[:20]:  # Limit to 20 in email
            html += f"""
                <div class="business">
                    <h3>{business.get('name', 'Unknown')}</h3>
                    <div class="info"><span class="label">Phone:</span> {business.get('phone', 'N/A')}</div>
                    <div class="info"><span class="label">Category:</span> {business.get('category', 'N/A')}</div>
                    <div class="info"><span class="label">Location:</span> {business.get('city', 'Unknown')}, {business.get('state', 'Unknown')}</div>
                    <div class="info"><span class="label">Reviews:</span> {business.get('reviews', 'No reviews')}</div>
                    {f'<div class="info"><span class="label">Website:</span> <a href="{business["website"]}">{business["website"]}</a></div>' if business.get('website') else ''}
                </div>
            """
        
        if len(businesses) > 20:
            html += f"<p><i>... and {len(businesses) - 20} more businesses</i></p>"
        
        html += """
            </div>
            <div style="text-align: center; padding: 20px; color: #666;">
                <p>This is an automated notification from MapLeads</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _send_webhook_notification(self, businesses: List[Dict]):
        """Send webhook notification"""
        try:
            # Prepare webhook data
            webhook_data = {
                'timestamp': datetime.now().isoformat(),
                'count': len(businesses),
                'businesses': businesses
            }
            
            # Send webhook
            headers = self.webhook_config.get('headers', {})
            headers['Content-Type'] = 'application/json'
            
            response = requests.post(
                self.webhook_config['url'],
                json=webhook_data,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            print(f"🔗 Webhook notification sent successfully")
            
        except Exception as e:
            print(f"Failed to send webhook notification: {e}")
