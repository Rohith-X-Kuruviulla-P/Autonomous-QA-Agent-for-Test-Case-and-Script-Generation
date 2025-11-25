# E-Shop Product Specifications

## 1. Cart Functionality
- Users can add items to the cart using the "Add to Cart" buttons.
- The cart summary must update the total price immediately upon addition.

## 2. Discount Logic
- **Code:** `SAVE15`
    - **Effect:** Applies a **15% discount** to the item subtotal (shipping is not discounted).
    - **Invalid Codes:** Entering any other code should display an error: "Invalid Coupon Code".

## 3. Shipping Rules
- **Standard Shipping:**
    - Cost: **$0.00** (Free).
    - Delivery: 5-7 Business Days.
- **Express Shipping:**
    - Cost: **$10.00**.
    - Delivery: 1-2 Business Days.
    - Behavior: Selecting this option must immediately add $10 to the Total Price.

## 4. User Data Validation
- **Full Name:** Required field. Cannot be empty.
- **Email:** Required field. Must contain valid email formatting ("@" and ".").
- **Payment Method:** One method must be selected (Credit Card is default).

## 5. Successful Transaction
- If all data is valid, clicking "Pay Now" should hide the form and display the text: **"Payment Successful!"**.