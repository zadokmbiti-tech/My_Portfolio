// Simple shared-secret gate for manage.html — one password for the site
// owner, appropriate for a solo portfolio rather than a full account system.
// Real enforcement happens server-side (backend/main.py's require_admin);
// this file's job is just to collect the password once and attach it to
// every admin request.

(function () {
  const STORAGE_KEY = 'portfolio_admin_secret';

  function getStoredSecret() {
    return sessionStorage.getItem(STORAGE_KEY) || '';
  }

  function askForSecret() {
    const entered = window.prompt('Admin password:');
    if (entered) {
      sessionStorage.setItem(STORAGE_KEY, entered);
    }
    return entered || '';
  }

  // Call at the top of manage.html to make sure a password has been entered
  // before showing the admin UI at all.
  window.requireAdminLogin = function () {
    if (!getStoredSecret()) {
      askForSecret();
    }
  };

  // Drop-in replacement for fetch() for any request hitting a protected
  // /admin/* endpoint. On a 401 it clears the stored password and asks
  // again so the next request has a chance to succeed.
  window.adminFetch = async function (url, options = {}) {
    const secret = getStoredSecret();
    const headers = Object.assign({}, options.headers, {
      'X-Admin-Secret': secret,
      'Content-Type': 'application/json',
    });
    const response = await fetch(url, Object.assign({}, options, { headers }));

    if (response.status === 401) {
      sessionStorage.removeItem(STORAGE_KEY);
      alert('Admin password was incorrect or missing. Please re-enter it.');
    }
    return response;
  };
})();
