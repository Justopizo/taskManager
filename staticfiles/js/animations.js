(function () {
    function getCookie(name) {
        const cookie = document.cookie
            .split(";")
            .map((item) => item.trim())
            .find((item) => item.startsWith(name + "="));
        return cookie ? decodeURIComponent(cookie.split("=")[1]) : "";
    }

    function showLiveToast(message, tone, link) {
        const container = document.getElementById("liveToastContainer");
        if (!container) {
            return;
        }
        const wrapper = document.createElement("div");
        wrapper.className = `toast show border-0 text-bg-${tone || "primary"}`;
        wrapper.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi bi-bell-fill me-2"></i>${message}
                    ${link ? `<div class="mt-2"><a class="btn btn-sm btn-light" href="${link}">Open</a></div>` : ""}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        container.prepend(wrapper);
        setTimeout(() => wrapper.remove(), 6000);
    }

    function initToasts() {
        document.querySelectorAll(".toast").forEach((element) => {
            const toast = bootstrap.Toast.getOrCreateInstance(element);
            toast.show();
        });
    }

    function initAOS() {
        if (window.AOS) {
            AOS.init({
                once: true,
                duration: 700,
                offset: 70,
            });
        }
    }

    function initNavbarState() {
        const navbar = document.getElementById("mainNavbar");
        const scrollTop = document.querySelector("[data-scroll-top]");
        if (!navbar) {
            return;
        }
        const update = () => {
            const active = window.scrollY > 16;
            navbar.classList.toggle("is-scrolled", active);
            if (scrollTop) {
                scrollTop.classList.toggle("is-visible", window.scrollY > 200);
            }
        };
        update();
        window.addEventListener("scroll", update);
        scrollTop?.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
    }

    function initCounters() {
        document.querySelectorAll("[data-count-to]").forEach((counter) => {
            const target = Number(counter.dataset.countTo || "0");
            const duration = 1000;
            const start = performance.now();
            const step = (now) => {
                const progress = Math.min((now - start) / duration, 1);
                counter.textContent = Math.round(target * progress);
                if (progress < 1) {
                    requestAnimationFrame(step);
                }
            };
            requestAnimationFrame(step);
        });
    }

    function initGreeting() {
        const target = document.querySelector("[data-greeting-target]");
        if (!target) {
            return;
        }
        const hour = new Date().getHours();
        const greeting = hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";
        const clock = new Intl.DateTimeFormat(undefined, {
            hour: "numeric",
            minute: "2-digit",
        }).format(new Date());
        target.textContent = `${greeting}. It's ${clock}.`;
    }

    function initParallax() {
        const hero = document.querySelector("[data-parallax-hero]");
        if (!hero) {
            return;
        }
        const layers = hero.querySelectorAll("[data-parallax]");
        window.addEventListener("scroll", () => {
            const offset = window.scrollY * 0.12;
            layers.forEach((layer) => {
                const speed = Number(layer.dataset.parallax || "1");
                layer.style.transform = `translateY(${offset * speed}px)`;
            });
        });
    }

    function initTypedHeadline() {
        const el = document.querySelector("[data-typed]");
        if (!el || !window.Typed) {
            return;
        }
        const values = (el.dataset.typed || "").split("|").filter(Boolean);
        if (!values.length) {
            return;
        }
        new Typed(el, {
            strings: values,
            typeSpeed: 42,
            backSpeed: 26,
            backDelay: 1800,
            loop: true,
        });
    }

    function initForms() {
        document.querySelectorAll("form").forEach((form) => {
            form.addEventListener("submit", () => {
                const submit = form.querySelector('button[type="submit"]');
                if (!submit || submit.dataset.loading === "true") {
                    return;
                }
                submit.dataset.loading = "true";
                submit.dataset.original = submit.innerHTML;
                submit.innerHTML = `<span class="submit-spinner"></span>Working...`;
                submit.disabled = true;
            });
        });
    }

    function initRegistrationValidation() {
        const form = document.querySelector("[data-register-form]");
        if (!form) {
            return;
        }
        const password = form.querySelector("#id_password1");
        const confirm = form.querySelector("#id_password2");
        const meter = form.querySelector("[data-password-meter]");
        const feedback = form.querySelector("[data-password-feedback]");
        const criteria = [
            { regex: /.{8,}/, label: "8+ chars" },
            { regex: /[A-Z]/, label: "uppercase" },
            { regex: /[a-z]/, label: "lowercase" },
            { regex: /[0-9]/, label: "number" },
        ];

        function updateStrength() {
            const value = password.value;
            const score = criteria.filter((item) => item.regex.test(value)).length;
            const width = (score / criteria.length) * 100;
            meter.style.width = `${width}%`;
            meter.style.background = score >= 4 ? "#198754" : score >= 3 ? "#ffc107" : "#dc3545";
            feedback.textContent = score >= 4 ? "Strong password" : score >= 3 ? "Almost there" : "Use uppercase, lowercase, numbers, and 8+ characters";
            password.classList.toggle("is-valid", score >= 3);
            password.classList.toggle("is-invalid", Boolean(value) && score < 3);
            const matches = confirm.value && confirm.value === value;
            confirm.classList.toggle("is-valid", Boolean(matches));
            confirm.classList.toggle("is-invalid", Boolean(confirm.value) && !matches);
        }

        password?.addEventListener("input", updateStrength);
        confirm?.addEventListener("input", updateStrength);
    }

    function initTooltips() {
        document.querySelectorAll("[data-bs-toggle='tooltip']").forEach((element) => {
            bootstrap.Tooltip.getOrCreateInstance(element);
        });
        document.querySelectorAll("[data-bs-toggle='popover']").forEach((element) => {
            bootstrap.Popover.getOrCreateInstance(element);
        });
    }

    function initCopyButtons() {
        document.querySelectorAll("[data-copy-text]").forEach((button) => {
            button.addEventListener("click", async () => {
                try {
                    await navigator.clipboard.writeText(button.dataset.copyText);
                    const feedback = button.parentElement.querySelector(".copy-feedback");
                    if (feedback) {
                        feedback.textContent = "Copied to clipboard";
                    }
                    showLiveToast("Invite code copied.", "success");
                } catch (error) {
                    showLiveToast("Copy failed. Please copy manually.", "danger");
                }
            });
        });
    }

    function renderNotificationList(items) {
        const list = document.querySelector("[data-notification-list]");
        if (!list) {
            return;
        }
        if (!items.length) {
            list.innerHTML = '<div class="dropdown-item text-muted py-3">No notifications yet.</div>';
            return;
        }
        list.innerHTML = items.slice(0, 5).map((item) => `
            <a class="dropdown-item notification-item ${item.is_read ? "" : "is-unread"}" href="${item.link || "#"}">
                <span class="notification-dot"></span>
                <span>
                    <strong>${item.message}</strong>
                    <small>${new Date(item.created_at).toLocaleString()}</small>
                </span>
            </a>
        `).join("");
    }

    function initNotifications() {
        if (document.body.dataset.authenticated !== "true") {
            return;
        }
        let initialized = false;
        let seenIds = new Set();
        const updateBadges = (items) => {
            const unread = items.filter((item) => !item.is_read).length;
            document.querySelectorAll("[data-notification-badge]").forEach((badge) => {
                badge.textContent = unread;
                badge.classList.toggle("d-none", unread === 0);
            });
        };
        const poll = () => {
            fetch("/api/notifications/", {
                headers: { "X-Requested-With": "XMLHttpRequest" },
                credentials: "same-origin",
            })
                .then((response) => response.ok ? response.json() : [])
                .then((items) => {
                    updateBadges(items);
                    renderNotificationList(items);
                    if (!initialized) {
                        seenIds = new Set(items.map((item) => item.id));
                        initialized = true;
                        return;
                    }
                    items.forEach((item) => {
                        if (!seenIds.has(item.id)) {
                            seenIds.add(item.id);
                            showLiveToast(item.message, item.is_read ? "secondary" : "primary", item.link);
                        }
                    });
                })
                .catch(() => undefined);
        };
        poll();
        setInterval(poll, 30000);
    }

    function initCommentRefresh() {
        const target = document.querySelector("[data-comments-feed]");
        if (!target) {
            return;
        }
        const url = target.dataset.commentsFeed;
        setInterval(() => {
            fetch(url, {
                headers: { "X-Requested-With": "XMLHttpRequest" },
                credentials: "same-origin",
            })
                .then((response) => response.text())
                .then((html) => {
                    target.innerHTML = html;
                })
                .catch(() => undefined);
        }, 10000);
    }

    function initTaskCompletionConfetti() {
        document.querySelectorAll("[data-task-status-select]").forEach((select) => {
            select.addEventListener("change", () => {
                if (select.value === "done" && window.confetti) {
                    confetti({ particleCount: 120, spread: 70, origin: { y: 0.75 } });
                }
            });
        });
    }

    function initDeadlineTimers() {
        document.querySelectorAll("[data-deadline]").forEach((item) => {
            const value = item.dataset.deadline;
            if (!value) {
                return;
            }
            const deadline = new Date(value);
            const diff = deadline - new Date();
            const days = Math.ceil(Math.abs(diff) / (1000 * 60 * 60 * 24));
            if (Number.isNaN(days)) {
                return;
            }
            item.textContent = diff >= 0 ? `Due in ${days} day${days === 1 ? "" : "s"}` : `Overdue by ${days} day${days === 1 ? "" : "s"}`;
            item.classList.toggle("text-danger", diff < 0);
        });
    }

    function initSkeletons() {
        document.querySelectorAll(".skeleton-group").forEach((group) => {
            setTimeout(() => group.classList.add("is-hidden"), 300);
        });
    }

    window.taskManagerUI = {
        csrfToken: () => getCookie("csrftoken"),
        showLiveToast,
    };

    document.addEventListener("DOMContentLoaded", () => {
        initAOS();
        initToasts();
        initNavbarState();
        initCounters();
        initGreeting();
        initParallax();
        initTypedHeadline();
        initForms();
        initRegistrationValidation();
        initTooltips();
        initCopyButtons();
        initNotifications();
        initCommentRefresh();
        initTaskCompletionConfetti();
        initDeadlineTimers();
        initSkeletons();
    });
})();
