## Module <whatsapp_product_inquiry>
#### 09.10.2024
#### Version 18.0.1.0.0
#### ADD
- Initial commit for Whatsapp Product Inquiry In Website

#### 29.05.2025
#### Version 18.0.1.0.0
#### Update
- Updated the whatsapp_product_inquiry controller function to URL-encode the 
message using quote_plus() to prevent newline-related redirect errors in
Werkzeug 3.0.1.
