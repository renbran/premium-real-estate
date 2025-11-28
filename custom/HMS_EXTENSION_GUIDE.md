# HMS Extension Modules - Complete Setup Guide

## 🏥 Basic HMS Extension: Billing & Appointments

This setup extends your Basic Hospital Management System with two powerful modules:

### 📊 **HMS Billing Management** (`hms_billing`)
Advanced billing and payment management system

#### Key Features:
- **Advanced Billing System**
  - Detailed billing with line items
  - Tax calculations and discounts
  - Multi-currency support
  - Invoice integration

- **Payment Management**
  - Multiple payment methods (Cash, Card, Check, Bank Transfer)
  - Payment tracking and reconciliation
  - Automatic accounting entries
  - Payment history

- **Insurance Management**
  - Insurance claim processing
  - Coverage verification
  - Claim status tracking
  - Automatic insurance calculations

- **Financial Reporting**
  - Revenue analytics
  - Outstanding balances
  - Payment reports
  - Insurance claim reports

#### Core Models:
- `medical.billing` - Main billing records
- `medical.billing.line` - Billing line items
- `medical.payment` - Payment tracking
- `medical.insurance.claim` - Insurance claims
- `res.partner` (extended) - Patient billing information

---

### 📅 **HMS Advanced Appointments** (`hms_appointments`)
Enhanced appointment scheduling and management system

#### Key Features:
- **Advanced Scheduling**
  - Time slot management
  - Doctor availability tracking
  - Appointment conflict detection
  - Recurring appointments

- **Enhanced Workflow**
  - Patient arrival tracking
  - Appointment status management
  - No-show tracking
  - Follow-up scheduling

- **Calendar Integration**
  - Calendar event creation
  - Reminder notifications
  - Multi-location support
  - Room and equipment management

- **Patient Experience**
  - Online booking capability
  - Appointment confirmations
  - Reminder system
  - Waiting list management

#### Core Models:
- `medical.appointment` (extended) - Enhanced appointments
- `medical.appointment.slot` - Time slot management
- `medical.doctor.schedule` - Doctor availability
- `medical.room` - Room management
- `medical.equipment` - Equipment tracking

---

## 🚀 Installation Instructions

### Prerequisites:
- Odoo 18.0 installed
- Basic HMS module installed and working
- Required dependencies: `account`, `sale`, `purchase`, `calendar`, `website`, `mail`

### Installation Steps:

1. **Copy Module Folders**
   ```bash
   # Copy both modules to your Odoo addons directory
   cp -r hms_billing /path/to/odoo/addons/
   cp -r hms_appointments /path/to/odoo/addons/
   ```

2. **Update Apps List**
   - Go to Odoo Settings → Apps
   - Click "Update Apps List"

3. **Install Modules**
   - Search for "HMS Billing Management"
   - Click Install
   - Search for "HMS Advanced Appointments"
   - Click Install

4. **Configure Users**
   - Go to Settings → Users & Companies → Users
   - Assign appropriate groups:
     - HMS Billing User/Manager
     - Basic HMS groups

---

## 📋 Usage Guide

### Billing Management:

1. **Create Medical Bills**
   - Go to HMS Billing → Billing → Medical Billing
   - Click Create
   - Select patient and add billing items
   - Set payment terms and due dates

2. **Process Payments**
   - Go to HMS Billing → Billing → Payments
   - Record payments against bills
   - Track payment methods and status

3. **Manage Insurance Claims**
   - Go to HMS Billing → Billing → Insurance Claims
   - Create claims from bills
   - Track claim status and payments

### Appointment Management:

1. **Enhanced Appointment Booking**
   - Go to Medical → Appointments
   - Use advanced appointment form
   - Select time slots and appointment types
   - Set up recurring appointments

2. **Manage Doctor Schedules**
   - Configure doctor availability
   - Set up time slots automatically
   - Manage room assignments

3. **Track Appointment Workflow**
   - Mark patient arrival
   - Start appointments
   - Record diagnosis and treatment
   - Schedule follow-ups

---

## 🔧 Configuration

### Billing Configuration:
- Set up payment methods
- Configure tax rates
- Set up journals for accounting
- Define billing sequences

### Appointment Configuration:
- Configure appointment types
- Set up rooms and equipment
- Define time slot templates
- Configure reminder settings

---

## 📈 Benefits

### For Hospital Administration:
- **Improved Financial Control**
  - Better revenue tracking
  - Automated billing processes
  - Insurance claim management
  - Payment reconciliation

- **Enhanced Scheduling**
  - Efficient appointment management
  - Reduced conflicts and overlaps
  - Better resource utilization
  - Improved patient experience

### For Medical Staff:
- **Streamlined Workflow**
  - Integrated patient records
  - Automated appointment tracking
  - Enhanced patient history
  - Better treatment planning

### For Patients:
- **Better Service**
  - Clear billing information
  - Easy appointment booking
  - Reminder notifications
  - Transparent payment process

---

## 🔗 Integration Points

### With Basic HMS:
- **Patient Records**: Seamlessly linked to billing and appointments
- **Doctor Management**: Extended with scheduling and availability
- **Insurance**: Enhanced with claim processing
- **Appointments**: Upgraded with advanced features

### With Odoo Core:
- **Accounting**: Full integration with invoices and payments
- **Calendar**: Appointment calendar integration
- **Website**: Online appointment booking capability
- **Mail**: Automated notifications and reminders

---

## 📊 Reporting Features

### Billing Reports:
- Revenue by period
- Outstanding balances
- Payment analysis
- Insurance claim reports

### Appointment Reports:
- Appointment statistics
- Doctor utilization
- No-show analysis
- Patient flow reports

---

## 🛠️ Customization Options

Both modules are designed for easy customization:
- Add new appointment types
- Customize billing workflows
- Add custom fields
- Create additional reports
- Integrate with external systems

---

## 📞 Support & Maintenance

### Regular Maintenance:
- Update appointment schedules
- Reconcile payments
- Process insurance claims
- Generate regular reports

### Troubleshooting:
- Check module dependencies
- Verify user permissions
- Review configuration settings
- Check log files for errors

---

## 🎯 Next Steps

After installation, you can:
1. Train staff on new features
2. Import existing data
3. Configure automated workflows
4. Set up reporting schedules
5. Customize for specific needs

---

**Your Basic HMS is now a comprehensive Hospital Management System with advanced billing and appointment management capabilities!**