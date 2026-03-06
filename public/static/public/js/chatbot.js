(function () {
    const chatMessages = document.getElementById("chatMessages");
    const chatForm = document.getElementById("chatForm");
    const chatInput = document.getElementById("chatInput");
    const chips = document.querySelectorAll("[data-question]");
    const drawer = document.getElementById("drawer");
    const menuBtn = document.getElementById("menuBtn");
    const drawerCloseBtn = document.getElementById("drawerCloseBtn");
    const themeSwitch = document.getElementById("themeSwitch");
    const clearChatBtn = document.getElementById("clearChatBtn");
    const welcomePanel = document.getElementById("welcomePanel");
    const quickChips = document.getElementById("quickChips");

    const STORAGE_KEY = "cea_chat_history_v5";
    const THEME_KEY = "cea_chat_theme";
    const BOT_NAME = "CEA Assistant";
    const BOT_ICON_SRC = "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Robot/3D/robot_3d.png";
    const MIN_TYPING_MS = 650;
    const MAX_TYPING_MS = 1900;
    const CONTACT_MARKER = "[[CONTACT_ACTIONS]]";

    let history = [];
    let typingRow = null;

    function csrfToken() {
        const tokenInput = document.querySelector("input[name='csrfmiddlewaretoken']");
        return tokenInput ? tokenInput.value : "";
    }

    function renderMessage(message) {
        const row = document.createElement("div");
        row.className = `msg-row ${message.role}`;

        if (message.role === "bot") {
            const avatar = document.createElement("div");
            avatar.className = "avatar msg-avatar";
            const icon = document.createElement("img");
            icon.className = "bot-emoji";
            icon.src = BOT_ICON_SRC;
            icon.alt = "";
            avatar.appendChild(icon);

            const bubble = document.createElement("div");
            bubble.className = "msg-bubble bot";

            const name = document.createElement("div");
            name.className = "msg-name";
            name.textContent = BOT_NAME;

            const text = document.createElement("div");
            text.className = "msg-text";

            bubble.appendChild(name);

            const actions = message.actions || null;
            const hasActions = actions && (actions.phone || actions.whatsapp || actions.email);
            const hasMarker = String(message.text || "").includes(CONTACT_MARKER);

            if (hasActions && hasMarker) {
                const parts = String(message.text || "").split(CONTACT_MARKER);
                const before = document.createElement("div");
                before.className = "msg-text";
                before.textContent = parts[0] || "";
                bubble.appendChild(before);

                const actionWrap = document.createElement("div");
                actionWrap.className = "contact-actions";

                if (actions.phone) {
                    const phoneLink = document.createElement("a");
                    phoneLink.className = "contact-pill call";
                    phoneLink.href = `tel:${actions.phone}`;
                    phoneLink.textContent = `Call ${actions.phone}`;
                    actionWrap.appendChild(phoneLink);
                }

                if (actions.whatsapp) {
                    const digits = String(actions.whatsapp).replace(/[^\d+]/g, "");
                    const waLink = document.createElement("a");
                    waLink.className = "contact-pill whatsapp";
                    waLink.href = `https://wa.me/${digits.replace("+", "")}`;
                    waLink.target = "_blank";
                    waLink.rel = "noopener";
                    waLink.textContent = `WhatsApp ${actions.whatsapp}`;
                    actionWrap.appendChild(waLink);
                }

                if (actions.email) {
                    const emailBtn = document.createElement("button");
                    emailBtn.type = "button";
                    emailBtn.className = "contact-pill email";
                    emailBtn.textContent = `Email ${actions.email}`;
                    emailBtn.addEventListener("click", async function () {
                        try {
                            await navigator.clipboard.writeText(actions.email);
                            emailBtn.textContent = "Email copied";
                            setTimeout(() => {
                                emailBtn.textContent = `Email ${actions.email}`;
                            }, 900);
                        } catch (e) {
                            emailBtn.textContent = "Copy failed";
                            setTimeout(() => {
                                emailBtn.textContent = `Email ${actions.email}`;
                            }, 900);
                        }
                    });
                    actionWrap.appendChild(emailBtn);
                }

                bubble.appendChild(actionWrap);

                const after = document.createElement("div");
                after.className = "msg-text";
                after.textContent = parts.slice(1).join(CONTACT_MARKER) || "";
                bubble.appendChild(after);
            } else {
                text.textContent = String(message.text || "").replaceAll(CONTACT_MARKER, "");
                bubble.appendChild(text);

                if (hasActions) {
                    const actionWrap = document.createElement("div");
                    actionWrap.className = "contact-actions";

                    if (actions.phone) {
                        const phoneLink = document.createElement("a");
                        phoneLink.className = "contact-pill call";
                        phoneLink.href = `tel:${actions.phone}`;
                        phoneLink.textContent = `Call ${actions.phone}`;
                        actionWrap.appendChild(phoneLink);
                    }

                    if (actions.whatsapp) {
                        const digits = String(actions.whatsapp).replace(/[^\d+]/g, "");
                        const waLink = document.createElement("a");
                        waLink.className = "contact-pill whatsapp";
                        waLink.href = `https://wa.me/${digits.replace("+", "")}`;
                        waLink.target = "_blank";
                        waLink.rel = "noopener";
                        waLink.textContent = `WhatsApp ${actions.whatsapp}`;
                        actionWrap.appendChild(waLink);
                    }

                    if (actions.email) {
                        const emailBtn = document.createElement("button");
                        emailBtn.type = "button";
                        emailBtn.className = "contact-pill email";
                        emailBtn.textContent = `Email ${actions.email}`;
                        emailBtn.addEventListener("click", async function () {
                            try {
                                await navigator.clipboard.writeText(actions.email);
                                emailBtn.textContent = "Email copied";
                                setTimeout(() => {
                                    emailBtn.textContent = `Email ${actions.email}`;
                                }, 900);
                            } catch (e) {
                                emailBtn.textContent = "Copy failed";
                                setTimeout(() => {
                                    emailBtn.textContent = `Email ${actions.email}`;
                                }, 900);
                            }
                        });
                        actionWrap.appendChild(emailBtn);
                    }

                    bubble.appendChild(actionWrap);
                }
            }
            row.appendChild(avatar);
            row.appendChild(bubble);
        } else {
            const bubble = document.createElement("div");
            bubble.className = "msg-bubble user";
            bubble.textContent = message.text;
            row.appendChild(bubble);
        }

        chatMessages.appendChild(row);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function setWelcomeMode(show) {
        if (show) {
            welcomePanel.classList.remove("is-hidden");
            quickChips.classList.add("is-hidden");
        } else {
            welcomePanel.classList.add("is-hidden");
            quickChips.classList.remove("is-hidden");
        }
    }

    function saveHistory() {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    }

    function wait(ms) {
        return new Promise((resolve) => setTimeout(resolve, ms));
    }

    function getTypingDelay(text) {
        const lengthDelay = Math.min(900, (text || "").length * 12);
        const base = 450 + lengthDelay;
        const jitter = Math.floor(Math.random() * 180);
        return Math.max(MIN_TYPING_MS, Math.min(MAX_TYPING_MS, base + jitter));
    }

    function showTypingIndicator() {
        if (typingRow) return;
        setWelcomeMode(false);
        typingRow = document.createElement("div");
        typingRow.className = "msg-row bot";
        const avatar = document.createElement("div");
        avatar.className = "avatar msg-avatar";
        const icon = document.createElement("img");
        icon.className = "bot-emoji";
        icon.src = BOT_ICON_SRC;
        icon.alt = "";
        avatar.appendChild(icon);

        const bubble = document.createElement("div");
        bubble.className = "msg-bubble bot typing-bubble";
        bubble.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';

        typingRow.appendChild(avatar);
        typingRow.appendChild(bubble);
        chatMessages.appendChild(typingRow);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function hideTypingIndicator() {
        if (!typingRow) return;
        typingRow.remove();
        typingRow = null;
    }

    function pushMessage(role, text, actions = null) {
        setWelcomeMode(false);
        const msg = { role, text: String(text || ""), actions };
        history.push(msg);
        renderMessage(msg);
        saveHistory();
    }

    function loadHistory() {
        const saved = localStorage.getItem(STORAGE_KEY);
        chatMessages.innerHTML = "";

        if (saved) {
            try {
                history = JSON.parse(saved);
                if (Array.isArray(history) && history.length > 0) {
                    setWelcomeMode(false);
                    history.forEach(renderMessage);
                    return;
                }
            } catch (e) {
                history = [];
            }
        }

        history = [];
        setWelcomeMode(true);
    }

    async function askBot(question) {
        pushMessage("user", question);
        showTypingIndicator();

        try {
            const body = new URLSearchParams({ question });
            const response = await fetch("/ask/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": csrfToken(),
                },
                body,
            });

            if (!response.ok) {
                await wait(700);
                hideTypingIndicator();
                pushMessage("bot", "I could not process that right now. Please try again.");
                return;
            }

            const data = await response.json();
            const finalReply = data.follow_up
                ? `${data.answer || "I am here to help."}\n\n${data.follow_up}`
                : (data.answer || "I am here to help.");

            await wait(getTypingDelay(finalReply));
            hideTypingIndicator();
            pushMessage("bot", finalReply, data.contact_actions || null);
        } catch (error) {
            await wait(700);
            hideTypingIndicator();
            pushMessage("bot", "Network issue detected. Please try again.");
        }
    }

    chatForm.addEventListener("submit", function (e) {
        e.preventDefault();
        const value = chatInput.value.trim();
        if (!value) return;
        chatInput.value = "";
        askBot(value);
    });

    chips.forEach((chip) => {
        chip.addEventListener("click", function () {
            const value = chip.dataset.question || "";
            if (value) askBot(value);
        });
    });

    function openDrawer() {
        drawer.classList.add("open");
        drawer.setAttribute("aria-hidden", "false");
    }

    function closeDrawer() {
        drawer.classList.remove("open");
        drawer.setAttribute("aria-hidden", "true");
    }

    menuBtn.addEventListener("click", function () {
        if (drawer.classList.contains("open")) {
            closeDrawer();
        } else {
            openDrawer();
        }
    });

    if (drawerCloseBtn) {
        drawerCloseBtn.addEventListener("click", closeDrawer);
    }

    document.addEventListener("click", function (e) {
        if (!drawer.classList.contains("open")) return;
        if (drawer.contains(e.target) || menuBtn.contains(e.target)) return;
        closeDrawer();
    });

    clearChatBtn.addEventListener("click", function () {
        localStorage.removeItem(STORAGE_KEY);
        history = [];
        chatMessages.innerHTML = "";
        setWelcomeMode(true);
        loadHistory();
        closeDrawer();
    });

    function applyTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem(THEME_KEY, theme);
        if (themeSwitch) {
            themeSwitch.checked = theme === "dark";
        }
    }

    function toggleTheme() {
        const current = document.documentElement.getAttribute("data-theme") || "dark";
        applyTheme(current === "dark" ? "light" : "dark");
    }

    if (themeSwitch) {
        themeSwitch.addEventListener("change", function () {
            applyTheme(themeSwitch.checked ? "dark" : "light");
        });
    }

    const savedTheme = localStorage.getItem(THEME_KEY);
    const initialTheme = savedTheme || document.documentElement.getAttribute("data-theme") || "dark";
    applyTheme(initialTheme);

    loadHistory();
})();
