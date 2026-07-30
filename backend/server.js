// Load environment variables from .env file
require('dotenv').config();

// Import the tools we need
const express = require('express');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

// Create our web server
const app = express();

// Tell the server to serve files from the 'public' folder
app.use(express.static('public'));

// Parse JSON data from requests
app.use(express.json());

// ENDPOINT 1: Create a checkout session
// This runs when someone visits the checkout page
app.post('/create-checkout-session', async (req, res) => {
  try {
    // Create a Stripe checkout session
    const session = await stripe.checkout.sessions.create({
      ui_mode: 'embedded', // Embeds the form on your page
      line_items: [
        {
          price: process.env.PRICE_ID, // Your product price ID
          quantity: 1,
        },
      ],
      mode: 'subscription', // For recurring payments
      return_url: `http://localhost:4242/return.html?session_id={CHECKOUT_SESSION_ID}`,
    });

    // Send back the client secret so the frontend can show the form
    res.send({ clientSecret: session.client_secret });
  } catch (error) {
    console.error('Error creating checkout session:', error);
    res.status(500).send({ error: error.message });
  }
});

// ENDPOINT 2: Check payment status
// This runs on the return page to see if payment succeeded
app.get('/session-status', async (req, res) => {
  try {
    const session = await stripe.checkout.sessions.retrieve(req.query.session_id);

    res.send({
      status: session.status,
      customer_email: session.customer_details.email
    });
  } catch (error) {
    console.error('Error retrieving session:', error);
    res.status(500).send({ error: error.message });
  }
});

// Start the server on port 4242
const PORT = 4242;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`Visit http://localhost:${PORT}/checkout.html to test!`);
});