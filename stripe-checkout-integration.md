# Stripe Checkout Integration Guide

This guide explains how to implement Stripe Checkout in your frontend application.

## Overview

Stripe Checkout provides a pre-built, Stripe-hosted payment page that lets you securely collect payment information. With the backend changes in place, you can now:

1. Redirect users to a Stripe Checkout page
2. Let Stripe handle payment collection
3. Get redirected back to your site after payment

## Implementation Steps

### 1. Create a Checkout Button Component

```jsx
import React from 'react';
import axios from 'axios';

function CheckoutButton({ priceId }) {
  const handleCheckout = async () => {
    try {
      // Call your backend endpoint
      const response = await axios.post('/api/v1/subscriptions/create-checkout-session', {
        price_id: priceId
      });
      
      // Redirect to Stripe Checkout
      window.location.href = response.data.checkout_url;
    } catch (error) {
      console.error('Error creating checkout session:', error);
      // Handle errors appropriately
    }
  };

  return (
    <button 
      onClick={handleCheckout}
      className="checkout-button"
    >
      Subscribe Now
    </button>
  );
}

export default CheckoutButton;
```

### 2. Create Success and Cancel Pages

Create pages that users will be redirected to after completing or canceling checkout:

```jsx
// pages/checkout/success.jsx
export default function SuccessPage() {
  return (
    <div className="success-page">
      <h1>Payment Successful!</h1>
      <p>Thank you for your subscription.</p>
      <a href="/dashboard">Go to Dashboard</a>
    </div>
  );
}

// pages/checkout/cancel.jsx
export default function CancelPage() {
  return (
    <div className="cancel-page">
      <h1>Payment Canceled</h1>
      <p>Your payment was canceled. No charges were made.</p>
      <a href="/pricing">Return to Pricing</a>
    </div>
  );
}
```

### 3. Customize the Checkout Experience

You can customize the checkout experience by passing additional options to the backend:

```jsx
const response = await axios.post('/api/v1/subscriptions/create-checkout-session', {
  price_id: priceId,
  success_url: `${window.location.origin}/checkout/success?session_id={CHECKOUT_SESSION_ID}`,
  cancel_url: `${window.location.origin}/checkout/cancel`
});
```

### 4. Verify Subscription Status

After a successful checkout, you may want to verify the user's subscription status:

```jsx
import { useEffect, useState } from 'react';
import axios from 'axios';

function SubscriptionStatus() {
  const [status, setStatus] = useState('loading');
  
  useEffect(() => {
    const checkSubscription = async () => {
      try {
        const response = await axios.get('/api/v1/subscriptions/');
        if (response.data && response.data.length > 0) {
          setStatus(response.data[0].status);
        } else {
          setStatus('none');
        }
      } catch (error) {
        console.error('Error checking subscription:', error);
        setStatus('error');
      }
    };
    
    checkSubscription();
  }, []);
  
  if (status === 'loading') return <p>Loading...</p>;
  if (status === 'none') return <p>No active subscription</p>;
  if (status === 'error') return <p>Error loading subscription</p>;
  
  return <p>Your subscription status: {status}</p>;
}
```

## Testing

1. Use Stripe's test cards for testing (e.g., `4242 4242 4242 4242` for successful payments)
2. Set your Stripe account to test mode when developing
3. Verify that webhooks are being received and processed correctly

## Additional Resources

- [Stripe Checkout Documentation](https://stripe.com/docs/checkout)
- [Testing Stripe Payments](https://stripe.com/docs/testing)
- [Handling Webhook Events](https://stripe.com/docs/webhooks)

## Troubleshooting

- Check browser console for errors
- Verify API responses in the Network tab
- Ensure your Stripe keys are correctly configured
- Check webhook logs in the Stripe Dashboard 