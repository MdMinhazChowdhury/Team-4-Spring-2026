function test(name, fn) {
  try {
    fn();
    console.log("PASS:", name);
  } catch (e) {
    console.error("FAIL:", name, e.message);
  }
}

function section(title) {
  console.log("");
  console.log("=== " + title + " ===");
}

// ---------------- MAIN PAGE FRONTEND TESTS ----------------
function runMainPageTests() {
  section("Running Main Page Frontend Tests");

  // SUNNY DAY
  test("Sunny day: showTab switches to transaction tab", () => {
    if (typeof showTab !== "function") {
      throw new Error("showTab is not defined");
    }

    showTab("transaction-area");

    const active = document.querySelector(".tab-content.active");
    if (!active) {
      throw new Error("No active tab found");
    }

    if (active.id !== "transaction-area") {
      throw new Error("Expected transaction-area to be active");
    }
  });

  // RAINY DAY
  test("Rainy day: invalid tab id causes failure", () => {
    let threw = false;

    try {
      showTab("not-a-real-tab");
    } catch (e) {
      threw = true;
    }

    if (!threw) {
      throw new Error("Expected invalid tab id to fail");
    }
  });

  // BOUNDARY / LIMIT
  test("Boundary: repeated tab switching leaves exactly one active tab", () => {
    showTab("dashboard-area");
    showTab("calendar-area");
    showTab("subscription-area");
    showTab("transaction-area");
    showTab("savings-goals-area");

    const activeTabs = document.querySelectorAll(".tab-content.active");
    if (activeTabs.length !== 1) {
      throw new Error("Expected exactly one active tab, found " + activeTabs.length);
    }
  });

  // Extra frontend checks
  test("Main page structure: sidebar buttons exist", () => {
    const buttons = document.querySelectorAll(".nav-link");
    if (buttons.length < 5) {
      throw new Error("Not all nav buttons found");
    }
  });

  test("Main page structure: all tab sections exist", () => {
    [
      "dashboard-area",
      "transaction-area",
      "subscription-area",
      "savings-goals-area",
      "calendar-area"
    ].forEach(id => {
      if (!document.getElementById(id)) {
        throw new Error(id + " missing");
      }
    });
  });

  test("Main page structure: transaction inputs exist", () => {
    if (!document.querySelector(".tran-amount input")) {
      throw new Error("Amount input missing");
    }
    if (!document.querySelector(".tran-date input")) {
      throw new Error("Date input missing");
    }
    if (!document.querySelector(".tran-description input")) {
      throw new Error("Description input missing");
    }
    if (!document.querySelector(".tran-category select")) {
      throw new Error("Category select missing");
    }
  });

  test("Main page structure: savings goal inputs exist", () => {
    if (!document.querySelector(".goal-name input")) {
      throw new Error("Goal name input missing");
    }
    if (!document.querySelector(".current-savings input")) {
      throw new Error("Current savings input missing");
    }
    if (!document.querySelector(".target-amount input")) {
      throw new Error("Target amount input missing");
    }
    if (!document.querySelector(".target-deadline input")) {
      throw new Error("Target deadline input missing");
    }
  });

  test("Main page boundary: amount field accepts 0", () => {
    const amountInput = document.querySelector(".tran-amount input");
    amountInput.value = "0";

    if (amountInput.value !== "0") {
      throw new Error("Amount input did not accept 0");
    }
  });

  test("Main page boundary: 1-character goal name is accepted by input", () => {
    const goalInput = document.querySelector(".goal-name input");
    goalInput.value = "A";

    if (goalInput.value !== "A") {
      throw new Error("Goal name input did not accept 1 character");
    }
  });

  console.log("=== Main Page Frontend Tests Complete ===");
}

// ---------------- LOGIN PAGE FRONTEND TESTS ----------------
function runLoginPageTests() {
  section("Running Login Page Frontend Tests");

  // SUNNY DAY
  test("Sunny day: username and password inputs accept valid values", () => {
    const username = document.querySelector('input[placeholder="username"]');
    const password = document.querySelector('input[placeholder="password"]');

    if (!username || !password) {
      throw new Error("Login inputs missing");
    }

    username.value = "testuser";
    password.value = "mypassword123";

    if (username.value !== "testuser") {
      throw new Error("Username input failed");
    }

    if (password.value !== "mypassword123") {
      throw new Error("Password input failed");
    }
  });

  // RAINY DAY
  test("Rainy day: username and password fields are marked required", () => {
    const username = document.querySelector('input[placeholder="username"]');
    const password = document.querySelector('input[placeholder="password"]');

    if (!username) {
      throw new Error("Username input missing");
    }
    if (!password) {
      throw new Error("Password input missing");
    }

    if (!username.hasAttribute("required")) {
      throw new Error("Username is not marked required");
    }

    if (!password.hasAttribute("required")) {
      throw new Error("Password is not marked required");
    }
  });

  // BOUNDARY / LIMIT
  test("Boundary: 1-character username and special-character password are accepted by input", () => {
    const username = document.querySelector('input[placeholder="username"]');
    const password = document.querySelector('input[placeholder="password"]');

    username.value = "a";
    password.value = "!@#123";

    if (username.value !== "a") {
      throw new Error("1-character username not accepted");
    }

    if (password.value !== "!@#123") {
      throw new Error("Special-character password not accepted");
    }
  });

  // Extra frontend checks
  test("Login page structure: form exists", () => {
    if (!document.querySelector("form")) {
      throw new Error("Form missing");
    }
  });

  test("Login page structure: Google button exists", () => {
    if (!document.querySelector(".button-box button")) {
      throw new Error("Google button missing");
    }
  });

  test("Login page structure: sign in button exists", () => {
    if (!document.querySelector(".btn")) {
      throw new Error("Sign in button missing");
    }
  });

  test("Login page structure: sign up link exists", () => {
    if (!document.querySelector(".register-link a")) {
      throw new Error("Sign up link missing");
    }
  });

  console.log("=== Login Page Frontend Tests Complete ===");
}

// ---------------- PAGE DETECTION ----------------
window.addEventListener("DOMContentLoaded", () => {
  const isMainPage =
    document.getElementById("dashboard-area") &&
    document.getElementById("transaction-area");

  const isLoginPage =
    document.querySelector("form") &&
    document.querySelector('input[placeholder="username"]') &&
    document.querySelector('input[placeholder="password"]');

  if (isMainPage) {
    runMainPageTests();
  } else if (isLoginPage) {
    runLoginPageTests();
  } else {
    console.log("No matching frontend test suite for this page.");
  }
});