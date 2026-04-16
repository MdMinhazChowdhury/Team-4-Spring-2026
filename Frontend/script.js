function showTab(tabID) {
    document.querySelectorAll('.tab-content').forEach(tab => {tab.classList.remove('active');});

    document.querySelectorAll('.nav-link').forEach(btn => {btn.classList.remove('active')});

    document.getElementById(tabID).classList.add('active');
}