// Run when page loads
initialize();

async function initialize() {
  // Get the session ID from URL
  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  const sessionId = urlParams.get('session_id');

  // If no session ID, show error
  if (!sessionId) {
    showError();
    return;
  }

  try {
    // Ask server for session status
    const response = await fetch(`/session-status?session_id=${sessionId}`);
    
    if (!response.ok) {
      showError();
      return;
    }

    const session = await response.json();

    // Hide loading
    document.getElementById('loading').classList.add('hidden');

    // Check status and show appropriate message
    if (session.status === 'complete') {
      // Show success UI
      document.getElementById('success').classList.remove('hidden');
      document.getElementById('customer-email').textContent = session.customer_email;

      // Fire Meta Pixel: StartTrial
      // This is the most important conversion event — someone just started their free trial.
      // Meta uses this to find more people likely to subscribe.
      if (typeof fbq !== 'undefined') {
        fbq('track', 'StartTrial', {
          value: 59.99,       // The value of the subscription if they convert after trial
          currency: 'CAD',
          predicted_ltv: 59.99,
          content_name: 'Jetsetter Economy',
        });
      }

    } else {
      // Payment failed or canceled
      showError();
    }
  } catch (error) {
    console.error('Error checking payment status:', error);
    showError();
  }
}

function showError() {
  document.getElementById('loading').classList.add('hidden');
  document.getElementById('success').classList.add('hidden');
  document.getElementById('error').classList.remove('hidden');
}
