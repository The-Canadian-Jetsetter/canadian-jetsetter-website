// Initialize Stripe with your publishable key
const stripe = Stripe('pk_live_51NktEhCHpFsG9XUZkJWGLpyiehfXdUOE48RbixDHGwvkOPp1PZ2szmjFuDDJsolpV3DVMtj6usRDPOoL3ZXDrACQ00sIqJCJ5n');

// Run this when the page loads
initialize();

async function initialize() {
  // Clear any loading placeholder
  document.getElementById('checkout').innerHTML = '';

  // Function to get the client secret from our server
  const fetchClientSecret = async () => {
    const response = await fetch("/create-checkout-session", {
      method: "POST",
    });
    const { clientSecret } = await response.json();
    return clientSecret;
  };

  // Initialize the embedded checkout
  const checkout = await stripe.initEmbeddedCheckout({
    fetchClientSecret,
  });

  // Mount the checkout form
  checkout.mount('#checkout');

  // Fire Meta Pixel: InitiateCheckout
  // This tells Meta the user has reached the checkout form and it loaded successfully
  if (typeof fbq !== 'undefined') {
    fbq('track', 'InitiateCheckout', {
      value: 59.99,
      currency: 'CAD',
      num_items: 1,
      content_name: 'Jetsetter Economy',
    });
  }
}
