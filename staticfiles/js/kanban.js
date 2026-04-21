(function () {
    function patchTask(taskId, payload) {
        return fetch(`/api/tasks/${taskId}/`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": window.taskManagerUI?.csrfToken() || "",
                "X-Requested-With": "XMLHttpRequest",
            },
            credentials: "same-origin",
            body: JSON.stringify(payload),
        }).then((response) => {
            if (!response.ok) {
                throw new Error("Task update failed");
            }
            return response.json();
        });
    }

    function syncStatusDisplay(card, status) {
        card.dataset.status = status;
        const badges = card.querySelectorAll("[data-status-badge]");
        badges.forEach((badge) => {
            badge.className = `status-badge ${status}`;
            const labels = {
                pending: "Pending",
                in_progress: "In Progress",
                done: "Done",
            };
            badge.innerHTML = `<i class="bi bi-dot"></i>${labels[status] || status}`;
        });
        const select = card.querySelector("[data-task-status-select]");
        if (select) {
            select.value = status;
        }
    }

    function initViewToggle() {
        const buttons = document.querySelectorAll("[data-view-target]");
        if (!buttons.length) {
            return;
        }
        buttons.forEach((button) => {
            button.addEventListener("click", () => {
                const view = button.dataset.viewTarget;
                document.querySelectorAll("[data-view]").forEach((pane) => {
                    pane.classList.toggle("is-active", pane.dataset.view === view);
                });
                buttons.forEach((item) => item.classList.toggle("active", item === button));
            });
        });
    }

    function initInlineEdits() {
        document.querySelectorAll("[data-task-card]").forEach((card) => {
            const editButton = card.querySelector("[data-inline-edit]");
            const saveButton = card.querySelector("[data-inline-save]");
            editButton?.addEventListener("click", () => {
                card.classList.toggle("is-editing");
            });
            saveButton?.addEventListener("click", () => {
                const taskId = card.dataset.taskId;
                const titleInput = card.querySelector("[data-task-title-input]");
                const statusInput = card.querySelector("[data-task-status-select]");
                patchTask(taskId, {
                    title: titleInput.value,
                    status: statusInput.value,
                })
                    .then((data) => {
                        card.querySelectorAll("[data-task-title]").forEach((label) => {
                            label.textContent = data.title;
                        });
                        syncStatusDisplay(card, data.status);
                        card.classList.remove("is-editing");
                        window.taskManagerUI?.showLiveToast("Task updated.", "success");
                    })
                    .catch(() => window.taskManagerUI?.showLiveToast("Could not update task.", "danger"));
            });
        });
    }

    function initDragDrop() {
        document.querySelectorAll("[data-sortable-column]").forEach((column) => {
            new Sortable(column, {
                group: "task-board",
                animation: 180,
                ghostClass: "is-dragging",
                onEnd: (event) => {
                    const card = event.item;
                    const taskId = card.dataset.taskId;
                    const status = event.to.dataset.status;
                    patchTask(taskId, { status })
                        .then((data) => {
                            syncStatusDisplay(card, data.status);
                            if (data.status === "done" && window.confetti) {
                                confetti({ particleCount: 140, spread: 80, origin: { y: 0.72 } });
                            }
                            window.taskManagerUI?.showLiveToast("Task moved successfully.", "success");
                        })
                        .catch(() => {
                            if (event.from) {
                                event.from.appendChild(card);
                            }
                            window.taskManagerUI?.showLiveToast("Move failed.", "danger");
                        });
                },
            });
        });
    }

    document.addEventListener("DOMContentLoaded", () => {
        initViewToggle();
        initInlineEdits();
        if (window.Sortable) {
            initDragDrop();
        }
    });
})();
