(function () {
    const root = document.documentElement;
    const storageKey = "taskmanager-theme";

    function setTheme(theme) {
        root.setAttribute("data-bs-theme", theme);
        localStorage.setItem(storageKey, theme);
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
        return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }

    document.addEventListener("DOMContentLoaded", () => {
        setTheme(preferredTheme());
        document.querySelectorAll("[data-theme-toggle]").forEach((toggle) => {
            toggle.addEventListener("click", () => {
                const next = root.getAttribute("data-bs-theme") === "dark" ? "light" : "dark";
                setTheme(next);
            });
        });
    });
})();
