# E-Shop Checkout Page - Product Specifications

## 1. Discount Logic
The checkout system supports specific coupon codes that modify the final total price.
- **Code: SAVE15**: Applies a **15% discount** to the subtotal.
- **Code: WELCOME10**: Applies a flat **$10 discount** to the subtotal.
- **Invalid Codes**: If a user enters a code not listed above, the system must display an error message: "Invalid coupon code".
- **Stacking**: Only one discount code can be applied per order.

## 2. Shipping Methods
Users can select between two shipping options:
- **Standard Shipping**: Cost is **$0.00** (Free). Estimated delivery is 5-7 business days.
- **Express Shipping**: Cost is **$10.00**. Estimated delivery is 1-2 business days.
- **Default**: Standard Shipping should be selected by default when the page loads.

## 3. Form Validation Rules
To ensure data integrity, the following validation rules apply to the User Details form:
- **Full Name**: Required field. Cannot be empty.
- **Email Address**: Required field. Must contain an "@" symbol and a domain (e.g., ".com").
- **Credit Card**: If "Credit Card" is selected as the payment method, the input must be exactly 16 digits.

## 4. UI/UX Guidelines
- The "Pay Now" button must remain disabled until all required fields are filled.
- Upon successful payment, the user should see a success message: "Payment Successful!".
- Error messages for validation failures must be displayed in **red text**.