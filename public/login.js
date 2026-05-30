// Customisation de la page de login Chainlit :
//  1. Renomme le champ "Email" en "Identifiant" et le passe en type texte
//     (sinon le navigateur exige un format e-mail et refuse "demo").
//  2. Injecte un message de contact pour les personnes sans identifiants.
// Le script est défensif : il n'agit que sur la page de login (présence d'un
// champ password) et n'injecte le message qu'une seule fois.

(function () {
  var CONTACT_HTML =
    '<div id="demo-contact-note">' +
    "<p><strong>Accès sur demande.</strong></p>" +
    "<p>Cette démo est protégée pour préserver une utilisation maîtrisée. " +
    "Pour obtenir un identifiant et tester l'assistant, contactez-moi :</p>" +
    '<p>✉️ <a href="mailto:gaelmukunde@gmail.com">gaelmukunde@gmail.com</a><br>' +
    '🔗 <a href="https://www.linkedin.com/in/gaelmukunde/" target="_blank" rel="noopener">linkedin.com/in/gaelmukunde</a></p>' +
    "</div>";

  function customizeLogin() {
    // N'agir que sur la page de login (un champ password y est présent).
    var passwordInput = document.querySelector('input[type="password"]');
    if (!passwordInput) return;

    // 1. Relabel + retype du champ identifiant.
    var idInput = document.querySelector(
      'input[name="email"], input#email, input[type="email"]'
    );
    if (idInput && idInput.getAttribute("data-relabeled") !== "1") {
      idInput.setAttribute("type", "text");
      idInput.setAttribute("placeholder", "Identifiant");
      idInput.setAttribute("data-relabeled", "1");
      // Relabel le <label> associé s'il existe.
      var container = idInput.closest("div");
      var label = container ? container.querySelector("label") : null;
      if (!label) label = document.querySelector('label[for="email"]');
      if (label) label.textContent = "Identifiant";
    }

    // 2. Injection du message de contact (une seule fois).
    if (!document.getElementById("demo-contact-note")) {
      var form = passwordInput.closest("form") || document.querySelector("form");
      if (form && form.parentNode) {
        var wrapper = document.createElement("div");
        wrapper.innerHTML = CONTACT_HTML;
        form.parentNode.insertBefore(wrapper.firstChild, form.nextSibling);
      }
    }
  }

  // La page de login est rendue côté client : on poll jusqu'à ce qu'elle soit là,
  // puis on arrête après un délai raisonnable.
  var interval = setInterval(customizeLogin, 400);
  setTimeout(function () {
    clearInterval(interval);
  }, 30000);
})();
