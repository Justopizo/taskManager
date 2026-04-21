(function () {
    const root = document.documentElement;
    const storageKey = "taskmanager-theme";

    function setTheme(theme, persist = true) {
        root.setAttribute("data-bs-theme", theme);
        if (persist) {
            localStorage.setItem(storageKey, theme);
        }
        document.querySelectorAll("[data-theme-toggle]").forEach((toggle) => {
            const icon = toggle.querySelector("i");
            if (!icon) {
                return;
            }
            icon.className = theme === "dark" ? "bi bi-sunrise" : "bi bi-moon-stars";
        });
    }

    function preferredTheme() {
        const saved = localStorage.getItem(storageKey);
        if (saved === "dark" || saved === "light") {
            return saved;
        }
        return "dark";
    }

    function initTheme() {
        const theme = preferredTheme();
        setTheme(theme, false);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initTheme);
    } else {
        initTheme();
    }

    document.querySelectorAll("[data-theme-toggle]").forEach((toggle) => {
        toggle.addEventListener("click", () => {
            const next = root.getAttribute("data-bs-theme") === "dark" ? "light" : "dark";
            setTheme(next);
        });
    });
})();
