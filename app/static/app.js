(function () {
  var SPECIAL = /[!@#$%^&*()_+\-=[\]{}|;:'",.<>/?`~"\\]/;

  function policyOk(value) {
    return value.length >= 10 && SPECIAL.test(value);
  }

  var form = document.getElementById("login-form");
  if (!form) return;

  var passwordInput = form.querySelector('input[name="password"]');

  function markInvalid(input, invalid) {
    if (invalid) input.classList.add("invalid");
    else input.classList.remove("invalid");
  }

  passwordInput.addEventListener("input", function () {
    markInvalid(passwordInput, passwordInput.value.length > 0 && !policyOk(passwordInput.value));
  });

  form.addEventListener("submit", function (e) {
    if (!policyOk(passwordInput.value)) {
      e.preventDefault();
      markInvalid(passwordInput, true);
      var msg =
        passwordInput.getAttribute("data-policy-msg") ||
        "Revisa la contraseña según la política indicada.";
      alert(msg);
    }
  });

  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/static/sw.js").catch(function () {});
  }
})();
