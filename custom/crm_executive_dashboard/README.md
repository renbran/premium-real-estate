# CRM Executive Dashboard - Odoo 17

A comprehensive CRM dashboard providing advanced analytics and executive-level insights for Odoo 17.

## Features

### 📊 Executive Analytics
- **Real-time KPIs**: Track leads, opportunities, revenue, and conversion rates
- **Performance Metrics**: Monitor team performance and individual achievements
- **Pipeline Analysis**: Visual representation of sales pipeline by stages
- **Revenue Forecasting**: Expected revenue calculations and trends

### 📈 Advanced Visualizations
- **Interactive Charts**: Built with Chart.js 4.4.0 for modern, responsive charts
- **12-Month Trends**: Historical performance analysis
- **Team Comparison**: Side-by-side team performance metrics
- **Source Analytics**: Lead acquisition channel analysis

### 🎯 Business Intelligence
- **Customer Acquisition**: Track new customer metrics
- **Conversion Analytics**: Detailed conversion rate analysis
- **Overdue Management**: Automatic identification of overdue opportunities
- **Top Performers**: Recognition and tracking of high-performing team members

### 🔧 Technical Features
- **Odoo 17 Native**: Built with OWL framework for optimal performance
- **Mobile Responsive**: Works seamlessly on all devices
- **Real-time Updates**: Auto-refresh functionality with configurable intervals
- **Export Capabilities**: Excel and CSV export options
- **Dark Mode Support**: Automatic dark mode detection
- **Accessibility**: WCAG compliant design

## Installation

1. Copy the module to your Odoo addons directory:
   ```bash
   cp -r crm_executive_dashboard /path/to/odoo/addons/
   ```

2. Restart your Odoo server:
   ```bash
   sudo systemctl restart odoo
   ```

3. Update the apps list:
   - Go to **Apps → Update Apps List**

4. Install the module:
   - Search for "CRM Executive Dashboard"
   - Click **Install**

## Configuration

### Initial Setup

1. Navigate to **CRM Executive → Dashboard Settings**
2. Create or modify dashboard configurations
3. Set default date ranges and team filters
4. Configure auto-refresh settings

### Security Groups

The module includes two security groups:
- **CRM Executive Dashboard User**: Can view dashboards
- **CRM Executive Dashboard Manager**: Can manage configurations and export data

### System Parameters

Configure system-wide settings:
- `crm_executive_dashboard.auto_refresh`: Enable/disable auto-refresh
- `crm_executive_dashboard.refresh_interval`: Refresh interval in minutes
- `crm_executive_dashboard.default_period`: Default time period
- `crm_executive_dashboard.show_forecasts`: Show/hide forecasting charts
- `crm_executive_dashboard.currency_format`: Currency display format

## Usage

### Main Dashboard

1. Go to **CRM Executive → Executive Dashboard**
2. Use date range filters to analyze specific periods
3. Select teams to focus on specific groups
4. Click on charts for detailed drill-down views

### Data Export

1. Click the **Export** button in the dashboard header
2. Choose Excel or CSV format
3. File will be downloaded automatically

### Mobile Access

The dashboard is fully responsive and can be accessed on mobile devices with full functionality.

## Technical Architecture

### Backend Components

- **Models**: `crm.executive.dashboard` with comprehensive analytics methods
- **Controllers**: RESTful API endpoints for data retrieval
- **Security**: Role-based access control with record rules

### Frontend Components

- **OWL Components**: Modern JavaScript framework integration
- **Chart.js Integration**: Advanced charting capabilities
- **SCSS Styling**: Modern, responsive design system
- **Asset Management**: Optimized resource loading

### Database Optimization

- **Efficient Queries**: Optimized SQL queries for large datasets
- **Caching Strategy**: Intelligent data caching for performance
- **Index Usage**: Proper database indexing for speed

## API Endpoints

### Dashboard Data
```javascript
POST /crm/dashboard/data
{
    "date_from": "2024-01-01",
    "date_to": "2024-12-31", 
    "team_ids": [1, 2, 3]
}
```

### Overdue Opportunities
```javascript
POST /crm/dashboard/overdue
{
    "team_ids": [1, 2, 3]
}
```

### Top Performers
```javascript
POST /crm/dashboard/performers
{
    "date_from": "2024-01-01",
    "date_to": "2024-12-31",
    "limit": 5
}
```

### Export Data
```javascript
GET /crm/dashboard/export?date_from=2024-01-01&date_to=2024-12-31&format=xlsx
```

## Customization

### Adding Custom KPIs

1. Extend the `get_dashboard_data` method in `models/crm_dashboard.py`
2. Add new KPI calculations
3. Update the frontend template to display new metrics

### Custom Chart Types

1. Modify the chart rendering methods in the JavaScript component
2. Add new Chart.js configurations
3. Update the SCSS styles as needed

### Additional Filters

1. Add new fields to the dashboard model
2. Update the search view and filters
3. Modify the data retrieval methods

## Performance Optimization

### Large Datasets

- Use date range filters to limit data scope
- Implement pagination for large result sets
- Consider database indexing on frequently queried fields

### Memory Management

- Charts are automatically destroyed when component unmounts
- Auto-refresh timers are properly cleaned up
- Efficient state management with OWL

## Troubleshooting

### Common Issues

**Dashboard not loading:**
- Check browser console for JavaScript errors
- Verify Chart.js is loaded properly
- Ensure user has proper permissions

**Charts not rendering:**
- Check if Chart.js CDN is accessible
- Verify canvas elements are present in DOM
- Check for JavaScript conflicts

**Performance issues:**
- Reduce date range for analysis
- Limit team selection
- Disable auto-refresh if not needed

**Export not working:**
- Verify user has manager permissions
- Check server logs for errors
- Ensure xlsxwriter is installed for Excel exports

### Debug Mode

Enable debug mode in Odoo to see detailed error messages and performance metrics.

## Compatibility

### Odoo Versions
- **Odoo 17.0 Community**: ✅ Fully Supported
- **Odoo 17.0 Enterprise**: ✅ Fully Supported
- **Odoo 16.0**: ❌ Not Compatible (OWL framework differences)

### Browser Support
- **Chrome 90+**: ✅ Fully Supported
- **Firefox 88+**: ✅ Fully Supported  
- **Safari 14+**: ✅ Fully Supported
- **Edge 90+**: ✅ Fully Supported

### Dependencies
- **Chart.js**: 4.4.0 (loaded from CDN)
- **FontAwesome**: Icons included
- **Bootstrap**: Odoo's built-in Bootstrap

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This module is licensed under the LGPL-3 license. See LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact: support@yourcompany.com
- Documentation: https://www.yourcompany.com/docs

## Changelog

### Version 17.0.1.0.0 (Initial Release)
- ✅ Executive KPI dashboard
- ✅ Advanced analytics and charts
- ✅ Mobile responsive design
- ✅ Export functionality
- ✅ Real-time updates
- ✅ Team performance tracking
- ✅ Pipeline analysis
- ✅ Customer acquisition metrics

## Credits

Developed with ❤️ for the Odoo community.

**Technologies Used:**
- Odoo 17 OWL Framework
- Chart.js 4.4.0
- SCSS/CSS3
- Python 3.10+
- PostgreSQL

**Icons:** FontAwesome
**Charts:** Chart.js
**Framework:** Odoo 17
