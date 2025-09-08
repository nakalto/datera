function getCsrf() {
  const name = "csrftoken=";                                   // cookie key we’re looking for
  const parts = document.cookie.split(";").map(v => v.trim());  // split "a=1; b=2" into ["a=1","b=2"] and trim spaces
  for (const p of parts)                                        // iterate over all cookies
    if (p.startsWith(name)) return p.slice(name.length);        // if one starts with "csrftoken=", return just the value
  const hidden = document.querySelector('input[name=csrfmiddlewaretoken]'); // fallback: hidden input from {% csrf_token %}
  return hidden ? hidden.value : "";                            // return its value or empty string if missing
}

function toast(message, type) {
  const el = document.getElementById("toast");                  // the toast div in the page
  if (!el) return;                                              // if it doesn’t exist, bail
  el.textContent = message;                                     // set the message text
  el.className = "toast show" + (type === "error" ? " error" : ""); // add classes to show it (and error styling if needed)
  setTimeout(() => {                                            // auto-hide after 3.5s
    el.className = "toast";                                     // remove "show" (and "error") classes
    el.textContent = "";                                        // clear message
  }, 3500);
}

function togglePassword(id, btn) {
  const input = document.getElementById(id);                    // find the password input by id
  if (!input) return;                                           // if not found, bail
  const show = input.type === "password";                       // check current state
  input.type = show ? "text" : "password";                      // flip between text <-> password
  if (btn) btn.textContent = show ? "Hide" : "Show";            // update the button label if provided
}
