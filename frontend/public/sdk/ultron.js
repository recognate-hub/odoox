/**
 * ULTRON Autonomous Payment Recovery - Zero-Code Client Interceptor
 * https://github.com/Mr-Roninx/ULTRON
 */
(function() {
  if (window.__ULTRON_INITIALIZED__) return;
  window.__ULTRON_INITIALIZED__ = true;

  var currentScript = document.currentScript || (function() {
    var scripts = document.getElementsByTagName('script');
    for (var i = 0; i < scripts.length; i++) {
      if (scripts[i].src && scripts[i].src.indexOf('ultron.js') !== -1) {
        return scripts[i];
      }
    }
    return null;
  })();

  var apiKey = currentScript ? currentScript.getAttribute('data-api-key') : (window.__ULTRON_API_KEY__ || null);
  var apiUrl = currentScript ? (currentScript.getAttribute('data-api-url') || currentScript.src.replace(/\/sdk\/ultron\.js.*$/, '')) : (window.__ULTRON_API_URL__ || window.location.origin);

  function reportPaymentFailure(details) {
    if (!apiKey) {
      console.warn('[ULTRON] Cannot report payment failure: data-api-key not provided.');
      return;
    }
    var endpoint = apiUrl.replace(/\/$/, '') + '/v1/events';
    var payload = {
      event_id: 'evt_client_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7),
      source: 'ODOOX_EVENT',
      provider: 'razorpay',
      environment: apiKey.indexOf('ul_live_') === 0 ? 'live' : 'test',
      payment_id: details.payment_id || ('pay_fe_' + Date.now()),
      order_id: details.order_id || null,
      amount_paise: Number(details.amount_paise || details.amount) || 0,
      currency: details.currency || 'INR',
      status: 'failed',
      failure_code: details.error_code || 'BAD_REQUEST_PAYMENT_FAILED',
      failure_description: details.error_description || 'Payment failed on client checkout',
      customer_reference: details.customer_id || details.email || details.contact || 'cust_anonymous',
      customer_email: details.email || null,
      customer_phone: details.contact || null,
      occurred_at: new Date().toISOString(),
      metadata: details.metadata || { url: window.location.href, title: document.title }
    };

    try {
      fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + apiKey
        },
        body: JSON.stringify(payload),
        keepalive: true
      }).then(function(res) {
        if (res.ok) {
          console.log('🛡️ [ULTRON] Payment failure successfully captured and sent to Control Plane.');
        }
      }).catch(function(e) {
        console.warn('⚠️ [ULTRON] Background dispatch error:', e.message);
      });
    } catch(err) {
      // Non-blocking fail-safe: never disrupt merchant checkout flow
    }
  }

  function wrapRazorpay() {
    if (!window.Razorpay || window.Razorpay.__ultron_wrapped__) return;

    var OriginalRazorpay = window.Razorpay;
    function UltronRazorpay(options) {
      options = options || {};
      var instance = new OriginalRazorpay(options);

      if (typeof instance.on === 'function') {
        instance.on('payment.failed', function(response) {
          try {
            var err = response.error || {};
            var meta = err.metadata || {};
            reportPaymentFailure({
              payment_id: meta.payment_id || response.razorpay_payment_id,
              order_id: meta.order_id || options.order_id,
              amount_paise: options.amount,
              currency: options.currency || 'INR',
              error_code: err.code || 'BAD_REQUEST_PAYMENT_FAILED',
              error_description: err.description || err.reason || 'Payment authorization failed',
              error_source: err.source,
              error_step: err.step,
              error_reason: err.reason,
              email: options.prefill ? options.prefill.email : null,
              contact: options.prefill ? options.prefill.contact : null,
              customer_id: options.customer_id,
              metadata: {
                notes: options.notes,
                page_url: window.location.href
              }
            });
          } catch(e) {}
        });
      }

      return instance;
    }

    UltronRazorpay.prototype = OriginalRazorpay.prototype;
    UltronRazorpay.__ultron_wrapped__ = true;
    window.Razorpay = UltronRazorpay;
    console.log('🛡️ [ULTRON] Autonomous Payment Interceptor active on page.');
  }

  if (window.Razorpay) {
    wrapRazorpay();
  } else {
    var checkInterval = setInterval(function() {
      if (window.Razorpay) {
        wrapRazorpay();
        clearInterval(checkInterval);
      }
    }, 200);
    setTimeout(function() { clearInterval(checkInterval); }, 30000);
  }

  window.Ultron = {
    reportFailure: reportPaymentFailure,
    init: function(opts) {
      if (opts && opts.apiKey) apiKey = opts.apiKey;
      if (opts && opts.apiUrl) apiUrl = opts.apiUrl;
      wrapRazorpay();
    }
  };
})();
