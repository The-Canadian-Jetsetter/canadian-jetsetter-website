// Import Stripe
import Stripe from 'stripe';

// Main Worker export
export default {
  async fetch(request, env, ctx) {
    // Initialize Stripe with secret key from environment
    const stripe = new Stripe(env.STRIPE_SECRET_KEY);
    
    // Get the URL path
    const url = new URL(request.url);
    const path = url.pathname;

    // CORS headers for API requests
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    // Handle OPTIONS requests (CORS preflight)
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    // ENDPOINT 1: Create checkout session
    if (path === '/create-checkout-session' && request.method === 'POST') {
      try {
        const session = await stripe.checkout.sessions.create({
          ui_mode: 'embedded',
          line_items: [
            {
              price: env.PRICE_ID,
              quantity: 1,
            },
          ],
          mode: 'subscription',
          subscription_data: {
            trial_period_days: 7,
          },
          automatic_tax: {
            enabled: true,
          },
          return_url: `${url.origin}/return.html?session_id={CHECKOUT_SESSION_ID}`,
        });

        return new Response(
          JSON.stringify({ clientSecret: session.client_secret }),
          {
            headers: {
              'Content-Type': 'application/json',
              ...corsHeaders,
            },
          }
        );
      } catch (error) {
        console.error('Error creating checkout session:', error);
        return new Response(
          JSON.stringify({ error: error.message }),
          {
            status: 500,
            headers: {
              'Content-Type': 'application/json',
              ...corsHeaders,
            },
          }
        );
      }
    }

    // ENDPOINT 2: Stripe webhook handler
    if (path === '/webhook' && request.method === 'POST') {
      try {
        // Get the raw body and signature header
        const body = await request.text();
        const signature = request.headers.get('stripe-signature');

        // Verify webhook signature
        let event;
        try {
          event = await stripe.webhooks.constructEventAsync(
            body,
            signature,
            env.STRIPE_WEBHOOK_SECRET
          );
        } catch (err) {
          console.error('Webhook signature verification failed:', err.message);
          return new Response(`Webhook Error: ${err.message}`, { status: 400 });
        }

        // Handle invoice.payment_succeeded event
        if (event.type === 'invoice.payment_succeeded') {
          const invoice = event.data.object;

          // Only send Purchase event for real charges after trial (not the initial $0 trial start)
          if (invoice.billing_reason === 'subscription_cycle') {
            // Check if this invoice contains our Economy plan price ID
            const hasEconomyPlan = invoice.lines.data.some(
              (line) => line.price && line.price.id === env.PRICE_ID
            );

            // Only track Economy plan purchases, ignore Premium
            if (!hasEconomyPlan) {
              return new Response(JSON.stringify({ received: true }), {
                headers: { 'Content-Type': 'application/json' },
              });
            }

            const customerEmail = invoice.customer_email;

            // Hash email for Meta CAPI (SHA-256)
            const emailHash = await hashEmail(customerEmail);

            // Send Purchase event to Meta Conversions API
            const metaPayload = {
              data: [
                {
                  event_name: 'Purchase',
                  event_time: Math.floor(Date.now() / 1000),
                  action_source: 'website',
                  user_data: {
                    em: [emailHash],
                  },
                  custom_data: {
                    currency: 'CAD',
                    value: 59.99,
                  },
                },
              ],
            };

            const metaResponse = await fetch(
              `https://graph.facebook.com/v18.0/1050064854097732/events?access_token=${env.META_CAPI_TOKEN}`,
              {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(metaPayload),
              }
            );

            if (!metaResponse.ok) {
              console.error('Meta CAPI error:', await metaResponse.text());
            }
          }
        }

        // Return 200 to acknowledge receipt
        return new Response(JSON.stringify({ received: true }), {
          headers: { 'Content-Type': 'application/json' },
        });
      } catch (error) {
        console.error('Webhook error:', error);
        return new Response(`Webhook Error: ${error.message}`, { status: 500 });
      }
    }

    // ENDPOINT 3: Check session status
    if (path === '/session-status' && request.method === 'GET') {
      try {
        const sessionId = url.searchParams.get('session_id');
        const session = await stripe.checkout.sessions.retrieve(sessionId);

        return new Response(
          JSON.stringify({
            status: session.status,
            customer_email: session.customer_details.email,
          }),
          {
            headers: {
              'Content-Type': 'application/json',
              ...corsHeaders,
            },
          }
        );
      } catch (error) {
        console.error('Error retrieving session:', error);
        return new Response(
          JSON.stringify({ error: error.message }),
          {
            status: 500,
            headers: {
              'Content-Type': 'application/json',
              ...corsHeaders,
            },
          }
        );
      }
    }

    // Serve static files from the public directory
    return env.ASSETS.fetch(request);
  },
};

// Helper function to hash email for Meta CAPI (SHA-256, lowercase, trimmed)
async function hashEmail(email) {
  const normalized = email.toLowerCase().trim();
  const encoder = new TextEncoder();
  const data = encoder.encode(normalized);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
}