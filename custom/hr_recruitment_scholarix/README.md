# SCHOLARIX HR Recruitment Enhancement

## Overview

This Odoo 18 module enhances the standard HR Recruitment functionality with automated email sending when applicants reach the "Contract Proposal" stage. It features a professional, responsive email template with SCHOLARIX branding and complete training period offer details.

## Features

### 🎯 Core Functionality
- **Automatic Email Trigger**: Sends training period offer email when applicant stage changes to "Contract Proposal"
- **Manual Email Sending**: Custom buttons to send and preview emails from applicant form
- **Email Composer Wizard**: Advanced email customization interface
- **Stage Configuration**: Mark recruitment stages as contract proposal triggers

### 📧 Professional Email Template
- **SCHOLARIX Branding**: Circuit-style logo and brand colors (#0c1e3d, #1e3a8a, #4fc3f7)
- **Responsive Design**: Mobile-optimized layout with clamp() CSS functions
- **Dynamic Content**: Populates candidate and job information automatically
- **Training Details**: 12-day program, AED 60/day compensation, terms & conditions
- **Action Buttons**: Direct links for offer acceptance and HR contact
- **Professional Layout**: Gradient backgrounds, proper typography, structured sections

### 🎨 Design Elements
- **Mobile-First**: Responsive design works on all devices
- **Professional Typography**: Inter font family with proper hierarchy
- **Color Scheme**: SCHOLARIX brand colors with professional gradients
- **Interactive Elements**: Hover effects and call-to-action buttons
- **Print-Ready**: Optimized for both screen and print viewing

## Installation

1. **Copy Module**: Place the `hr_recruitment_scholarix` folder in your Odoo addons directory
2. **Update Apps List**: Go to Settings > Apps > Update Apps List
3. **Install Module**: Search for "SCHOLARIX HR Recruitment Enhancement" and install
4. **Dependencies**: Requires `hr_recruitment`, `mail`, and `portal` modules

## Configuration

### 1. Stage Setup
- Navigate to **Recruitment > Configuration > Stages**
- Create or edit a stage named "Contract Proposal"
- Check the "Contract Proposal Stage" field to enable automatic email sending

### 2. Email Template
- The training period offer template is automatically installed
- Customize the template via **Settings > Technical > Email Templates**
- Template ID: `hr_recruitment_training_period_offer`

### 3. Company Information
- Ensure company details are properly configured for email headers
- Update contact information in the template if needed

## Usage

### Automatic Email Sending
1. **Stage Change**: When an applicant's stage changes to "Contract Proposal", the email is automatically sent
2. **Notification**: A message is posted on the applicant's chatter confirming email delivery
3. **Error Handling**: Failed email attempts are logged with error details

### Manual Email Actions
1. **Send Email Button**: 
   - Opens the email composer wizard
   - Pre-fills template content with applicant data
   - Allows customization before sending

2. **Preview Email Button**:
   - Opens email preview in new window
   - Shows exactly how the candidate will see the email
   - Includes responsive design preview

### Email Composer Wizard
- **Template Selection**: Choose from available email templates
- **Content Customization**: Edit subject and body content
- **Recipient Management**: Set To, CC, and BCC recipients
- **Preview Function**: Review email before sending
- **Send Action**: Deliver email and log the activity

## Email Template Features

### Header Section
- **Company Branding**: SCHOLARIX Global Consultants logo and information
- **Urgent Notice**: Red banner emphasizing response deadline
- **Date & Address**: Formatted recipient information

### Content Sections
1. **Training Details**: Duration, compensation, working hours, position
2. **Terms & Conditions**: 7 key points covering the training program
3. **Training Program**: Overview of learning objectives
4. **Required Documents**: List of documents needed for first day
5. **Action Buttons**: Accept offer and contact HR links
6. **Contact Information**: Company details and contact methods
7. **Acceptance Form**: Signature section for candidate response

### Technical Specifications
- **Responsive Tables**: Works on mobile and desktop
- **CSS Clamp**: Scalable typography for all screen sizes
- **Gradient Backgrounds**: Professional SCHOLARIX brand styling
- **Email Client Compatibility**: Tested with major email providers
- **Accessibility**: Proper contrast ratios and semantic HTML

## Customization

### Template Modification
```xml
<!-- Example: Modify training duration -->
<div>Duration: 15 working days</div> <!-- Changed from 12 days -->
```

### Brand Colors
```css
/* SCHOLARIX Color Variables */
--scholarix-primary: #0080FF;
--scholarix-accent: #00FFFF;
--scholarix-dark: #1B365D;
```

### Stage Configuration
```python
# Add custom stage logic
@api.model
def create(self, vals):
    stage = super().create(vals)
    if 'final offer' in stage.name.lower():
        stage.is_contract_proposal = True
    return stage
```

## Troubleshooting

### Common Issues

1. **Email Not Sending**
   - Check email server configuration
   - Verify applicant has valid email address
   - Review Odoo mail logs for errors

2. **Template Not Loading**
   - Ensure module is properly installed
   - Check template exists in Email Templates
   - Verify template ID in code matches data file

3. **Styling Issues**
   - Clear browser cache
   - Check email client compatibility
   - Review CSS for mobile responsiveness

4. **Stage Not Triggering**
   - Verify stage has "Contract Proposal" in name
   - Check `is_contract_proposal` field is set to True
   - Review stage configuration

### Debug Mode
Enable developer mode to:
- Access technical email template editor
- View detailed error logs
- Test email generation manually
- Debug template rendering issues

## Development

### File Structure
```
hr_recruitment_scholarix/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── hr_applicant.py
│   └── hr_recruitment_stage.py
├── wizard/
│   ├── __init__.py
│   └── email_composer.py
├── views/
│   ├── hr_applicant_views.xml
│   └── email_composer_views.xml
├── data/
│   ├── mail_templates.xml
│   └── recruitment_stages.xml
├── security/
│   └── ir.model.access.csv
└── static/src/js/
    └── applicant_form.js
```

### Key Methods
- `_send_contract_proposal_email()`: Automatic email sending
- `action_send_contract_email()`: Manual email composer
- `action_preview_contract_email()`: Email preview function

### API Integration
The module integrates with:
- Odoo Mail System
- HR Recruitment Module
- Portal Module (for responsive design)
- JavaScript Framework (for UI enhancements)

## Support

For technical support or customization requests:
- **Email**: info@scholarix.com
- **Company**: SCHOLARIX Global Consultants
- **Location**: Dubai, United Arab Emirates

## License

This module is licensed under LGPL-3. See LICENSE file for details.

## Version History

- **v18.0.1.0.0**: Initial release with complete functionality
  - Automatic email sending on stage change
  - Professional responsive email template
  - Email composer wizard
  - Stage configuration options
  - SCHOLARIX branding and design

---

**SCHOLARIX Global Consultants** - Professional Educational Technology Solutions