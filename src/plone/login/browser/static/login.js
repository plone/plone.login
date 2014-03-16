// Functions used by login pages

jQuery(function ($) {

  function cookiesEnabled() {
    // Test whether cookies are enabled by attempting to set a cookie and then change its value
    // set test cookie
    var c = "areYourCookiesEnabled=0";
    document.cookie = c;
    var dc = document.cookie;
    // cookie not set?  fail
    if (dc.indexOf(c) == -1) return 0;
    // change test cookie
    c = "areYourCookiesEnabled=1";
    document.cookie = c;
    dc = document.cookie;
    // cookie not changed?  fail
    if (dc.indexOf(c) == -1) return 0;
    // delete cookie
    document.cookie = "areYourCookiesEnabled=; expires=Thu, 01-Jan-70 00:00:01 GMT";
    return 1;
  }

  function setLoginVars(user_name_id, alt_user_name_id, password_id, empty_password_id, js_enabled_id, cookies_enabled_id) {
    // Indicate that javascript is enabled, set cookie status, copy username and password length info to
    // alternative variables since these vars are removed from the request by zope's authentication mechanism.
    if (js_enabled_id) {
      el = $(js_enabled_id);
      if (el) { el.value = 1; }
    }
    if (cookies_enabled_id) {
      el = $(cookies_enabled_id);
      // Do a fresh cookies enabled test every time we press the login button
      //   so that we are up to date in case the user enables cookies after seeing
      //   the cookies message.
      if (el) { el.value = cookiesEnabled(); }
    }
    if (user_name_id && alt_user_name_id) {
      user_name = $(user_name_id)
      alt_user_name = $(alt_user_name_id)
      if (user_name && alt_user_name) {
         alt_user_name.value = user_name.value;
      }
    }
    if (password_id && empty_password_id) {
      password = $(password_id)
      empty_password = $(empty_password_id)
      if (password && empty_password) {
         if (password.value.length==0) {
            empty_password.value = '1';
         } else {
            empty_password.value = '0';
         }
      }
    }
    return 1;
  }

  function showCookieMessage(msg_id) {
    // Show the element with the given id if cookies are not enabled
    msg = $(msg_id)
    if (msg) {
       if (cookiesEnabled()) {
          msg.hide();
       } else {
          msg.show();
       }
    }
  }

  function showEnableCookiesMessage() {
    // Show the element with the id 'enable_cookies_message' if cookies are not enabled
    showCookieMessage('enable_cookies_message')
  }
  // Call showEnableCookiesMessage after the page loads
  $(showEnableCookiesMessage);
});
