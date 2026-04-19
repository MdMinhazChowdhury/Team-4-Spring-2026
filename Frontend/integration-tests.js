function integrationTest(name, fn) {
  try {
    fn();
    console.log("INTEGRATION PASS:", name);
  } catch (e) {
    console.error("INTEGRATION FAIL:", name, e.message);
  }
}

function integrationSection(title) {
  console.log("");
  console.log("=== " + title + " ===");
}

function runMainPageIntegrationTests() {
  integrationSection("Running Main Page Integration Tests");

  integrationTest("Navigation buttons map to real tab sections", () => {
    const buttons = document.querySelectorAll(".nav-link");
    if (buttons.length < 5) {
      throw new Error("Expected at least 5 nav buttons");
    }

    buttons.forEach((btn) => {
      const onclickValue = btn.getAttribute("onclick");
      if (!onclickValue) {
        throw new Error("A nav button is missing onclick");
      }

      const match = onclickValue.match(/showTab\('(.+?)'\)/);
      if (!match) {
        throw new Error("Could not read tab target from onclick: " + onclickValue);
      }

      const targetId = match[1];
      if (!document.getElementById(targetId)) {
        throw new Error("Target section not found for " + targetId);
      }
    });
  });

  integrationTest("showTab integrates with all real tab sections", () => {
    if (typeof showTab !== "function") {
      throw new Error("showTab is not defined");
    }

    const tabIds = [
      "dashboard-area",
      "transaction-area",
      "subscription-area",
      "savings-goals-area",
      "calendar-area"
    ];

    tabIds.forEach((id) => {
      showTab(id);
      const active = document.querySelector(".tab-content.active");
      if (!active) {
        throw new Error("No active tab after switching to " + id);
      }
      if (active.id !== id) {
        throw new Error("Expected active tab " + id + " but got " + active.id);
      }
    });
  });

  integrationTest("Only one tab remains active after repeated switching", () => {
    showTab("dashboard-area");
    showTab("calendar-area");
    showTab("transaction-area");
    showTab("subscription-area");

    const activeTabs = document.querySelectorAll(".tab-content.active");
    if (activeTabs.length !== 1) {
      throw new Error("Expected 1 active tab, found " + activeTabs.length);
    }
  });

  integrationTest("Calendar container exists and FullCalendar library loaded", () => {
    const calendarEl = document.getElementById("calendar");
    if (!calendarEl) {
      throw new Error("Calendar container missing");
    }

    if (typeof FullCalendar === "undefined") {
      throw new Error("FullCalendar library not loaded");
    }
  });

  integrationTest("Calendar render integration produced content inside calendar container", () => {
    const calendarEl = document.getElementById("calendar");
    if (!calendarEl) {
      throw new Error("Calendar container missing");
    }

    const hasRenderedContent = calendarEl.children.length > 0 || calendarEl.innerHTML.trim().length > 0;
    if (!hasRenderedContent) {
      throw new Error("Calendar did not render any visible content");
    }
  });

  integrationTest("Dashboard cards and recent transaction area exist together", () => {
    if (!document.querySelector(".total-balance")) {
      throw new Error("Total balance card missing");
    }
    if (!document.querySelector(".monthly-income")) {
      throw new Error("Monthly income card missing");
    }
    if (!document.querySelector(".monthly-expenses")) {
      throw new Error("Monthly expenses card missing");
    }
    if (!document.querySelector(".net-savings")) {
      throw new Error("Net savings card missing");
    }
    if (!document.querySelector(".recent-transaction")) {
      throw new Error("Recent transaction section missing");
    }
  });

  integrationTest("Transaction form fields and buttons work together on same page", () => {
    const amount = document.querySelector(".tran-amount input");
    const date = document.querySelector(".tran-date input");
    const description = document.querySelector(".tran-description input");
    const category = document.querySelector(".tran-category select");
    const submit = document.querySelector("#transaction-area .submit");
    const cancel = document.querySelector("#transaction-area .cancel");

    if (!amount || !date || !description || !category || !submit || !cancel) {
      throw new Error("Transaction form pieces are not all present");
    }

    amount.value = "25.50";
    date.value = "2026-04-19";
    description.value = "Test Transaction";
    category.value = "Food";

    if (amount.value !== "25.50") throw new Error("Amount value not retained");
    if (date.value !== "2026-04-19") throw new Error("Date value not retained");
    if (description.value !== "Test Transaction") throw new Error("Description value not retained");
    if (category.value !== "Food") throw new Error("Category value not retained");
  });

  integrationTest("Savings goal form fields work together on same page", () => {
    const goalName = document.querySelector(".goal-name input");
    const currentSavings = document.querySelector(".current-savings input");
    const targetAmount = document.querySelector(".target-amount input");
    const deadline = document.querySelector(".target-deadline input");
    const submit = document.querySelector("#savings-goals-area .submit");
    const cancel = document.querySelector("#savings-goals-area .cancel");

    if (!goalName || !currentSavings || !targetAmount || !deadline || !submit || !cancel) {
      throw new Error("Savings goal form pieces are not all present");
    }

    goalName.value = "Trip";
    currentSavings.value = "100";
    targetAmount.value = "500";
    deadline.value = "2026-12-31";

    if (goalName.value !== "Trip") throw new Error("Goal name not retained");
    if (currentSavings.value !== "100") throw new Error("Current savings not retained");
    if (targetAmount.value !== "500") throw new Error("Target amount not retained");
    if (deadline.value !== "2026-12-31") throw new Error("Deadline not retained");
  });

  integrationTest("Subscription page and calendar renewal area both exist", () => {
    if (!document.getElementById("subscription-area")) {
      throw new Error("Subscription area missing");
    }
    if (!document.querySelector(".active-sub")) {
      throw new Error("Active subscriptions block missing");
    }
    if (!document.querySelector(".cal-right")) {
      throw new Error("Upcoming renewals panel missing");
    }
  });

  integrationTest("Rainy day: invalid tab target currently throws error", () => {
    let threw = false;
    try {
      showTab("not-a-real-tab");
    } catch (e) {
      threw = true;
    }

    if (!threw) {
      throw new Error("Expected invalid tab to throw, but it did not");
    }
  });

  console.log("=== Main Page Integration Tests Complete ===");
}

function runLoginPageIntegrationTests() {
  integrationSection("Running Login Page Integration Tests");

  integrationTest("Login form pieces exist together", () => {
    const form = document.querySelector("form");
    const googleBtn = document.querySelector(".button-box button");
    const username = document.querySelector('input[placeholder="username"]');
    const password = document.querySelector('input[placeholder="password"]');
    const signIn = document.querySelector(".btn");
    const signUpLink = document.querySelector(".register-link a");

    if (!form) throw new Error("Form missing");
    if (!googleBtn) throw new Error("Google button missing");
    if (!username) throw new Error("Username input missing");
    if (!password) throw new Error("Password input missing");
    if (!signIn) throw new Error("Sign in button missing");
    if (!signUpLink) throw new Error("Sign up link missing");
  });

  integrationTest("Username and password fields integrate with form state", () => {
    const username = document.querySelector('input[placeholder="username"]');
    const password = document.querySelector('input[placeholder="password"]');

    username.value = "student1";
    password.value = "pass123";

    if (username.value !== "student1") {
      throw new Error("Username value not retained");
    }
    if (password.value !== "pass123") {
      throw new Error("Password value not retained");
    }
  });

  integrationTest("Required validation flags are present on login inputs", () => {
    const username = document.querySelector('input[placeholder="username"]');
    const password = document.querySelector('input[placeholder="password"]');

    if (!username.hasAttribute("required")) {
      throw new Error("Username is not marked required");
    }
    if (!password.hasAttribute("required")) {
      throw new Error("Password is not marked required");
    }
  });

  integrationTest("Boundary: short username and special-character password are accepted by inputs", () => {
    const username = document.querySelector('input[placeholder="username"]');
    const password = document.querySelector('input[placeholder="password"]');

    username.value = "a";
    password.value = "!@#123";

    if (username.value !== "a") {
      throw new Error("Short username not retained");
    }
    if (password.value !== "!@#123") {
      throw new Error("Special-character password not retained");
    }
  });

  console.log("=== Login Page Integration Tests Complete ===");
}

window.addEventListener("DOMContentLoaded", () => {
  const isMainPage =
    document.getElementById("dashboard-area") &&
    document.getElementById("transaction-area");

  const isLoginPage =
    document.querySelector("form") &&
    document.querySelector('input[placeholder="username"]') &&
    document.querySelector('input[placeholder="password"]');

  if (isMainPage) {
    runMainPageIntegrationTests();
  } else if (isLoginPage) {
    runLoginPageIntegrationTests();
  } else {
    console.log("No matching integration test suite for this page.");
  }
});