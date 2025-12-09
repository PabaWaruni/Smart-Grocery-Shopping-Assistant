/**
 * Grocery Assistant - Frontend Script
 * 
 * Handles all client-side logic:
 * - Fetch and display grocery list
 * - Add/remove items with form validation
 * - Category browsing with pre-fill functionality
 * - Display suggestions and reminders
 * - Purchase management
 * 
 * API: http://127.0.0.1:8000 (FastAPI backend)
 * Auto-refresh: Every 30 seconds
 */

const apiUrl = "http://127.0.0.1:8002";


// DOM element references
const groceryList = document.getElementById("grocery-list");
const itemNameInput = document.getElementById("item-name");
const itemUnitInput = document.getElementById("item-unit");
const itemCategorySelect = document.getElementById("item-category");
const itemExpiryDateInput = document.getElementById("item-expiry-date");
const addItemBtn = document.getElementById("add-item-btn");
const missingItemsList = document.getElementById("missing-items-list");
const healthierAlternativesList = document.getElementById("healthier-alternatives-list");
const expiryRemindersList = document.getElementById("expiry-reminders-list");
const purchaseBtn = document.getElementById("purchase-btn");
const categoriesList = document.getElementById("categories-list");

/**
 * Fetch and display the current grocery list from the API
 * Renders each item with name, category, unit, and a remove button
 */
async function getGroceryList() {
    try {
        const response = await fetch(`${apiUrl}/grocery-list`);
        const data = await response.json();
        groceryList.innerHTML = "";
        data.forEach((item, index) => {
            const li = document.createElement("li");
            li.className = "grocery-item";

            const itemText = document.createElement("span");
            const categoryPart = item.category ? ` (${item.category})` : "";
            const unitPart = item.unit ? ` - ${item.unit}` : "";
            const expiryPart = item.expiry_date ? ` (Expires: ${item.expiry_date})` : "";
            itemText.textContent = `${item.name}${categoryPart}${unitPart}${expiryPart}`;

            const removeBtn = document.createElement("button");
            removeBtn.textContent = "✕ Remove";
            removeBtn.className = "remove-item-btn";
            removeBtn.onclick = () => removeFromGroceryList(item.name);

            li.appendChild(itemText);
            li.appendChild(removeBtn);
            groceryList.appendChild(li);
        });
    } catch (error) {
        console.error("Error fetching grocery list:", error);
    }
}

async function addItem() {
    const name = itemNameInput.value.trim();
    const unit = itemUnitInput.value.trim();
    const category = itemCategorySelect ? itemCategorySelect.value : "";
    const expiry_date = itemExpiryDateInput.value;

    if (!name || !unit) {
        alert("Please fill in all fields (name and unit).");
        return;
    }

    const item = { name, unit, category };
    if (expiry_date) {
        item.expiry_date = expiry_date;
    }

    try {
        const response = await fetch(`${apiUrl}/grocery-list`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(item)
        });
        const newItem = await response.json();
        itemNameInput.value = "";
        itemUnitInput.value = "";
        if (itemCategorySelect) itemCategorySelect.value = "";
        itemExpiryDateInput.value = "";
        refreshAllData();
    } catch (error) {
        console.error("Error adding item:", error);
    }
}

async function removeFromGroceryList(itemName) {
    if (confirm(`Are you sure you want to remove "${itemName}" from your grocery list?`)) {
        try {
            const response = await fetch(`${apiUrl}/grocery-list/${encodeURIComponent(itemName)}`, {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json"
                }
            });
            if (response.ok) {
                const result = await response.json();
                refreshAllData();
                alert(result.message || "Item removed successfully!");
            }
        } catch (error) {
            console.error("Error removing item:", error);
        }
    }
}

async function addItemFromCategory(itemName) {
    const unit = prompt("Enter unit (e.g., kg, liters, pieces):", "pieces");
    if (unit === null) return;

    try {
        const response = await fetch(`${apiUrl}/grocery-list`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ name: itemName, unit: unit })
        });
        if (response.ok) {
            getGroceryList();
            alert(`${itemName} added to your grocery list!`);
        }
    } catch (error) {
        console.error("Error adding item:", error);
    }
}

async function getMissingItemSuggestions() {
    try {
        const response = await fetch(`${apiUrl}/suggestions/missing`);
        const data = await response.json();
        missingItemsList.innerHTML = "";
        if (data.suggestions.length === 0) {
            missingItemsList.innerHTML = "<li>No missing items suggested</li>";
        } else {
            data.suggestions.forEach(item => {
                const li = document.createElement("li");
                li.textContent = item;
                missingItemsList.appendChild(li);
            });
        }
    } catch (error) {
        console.error("Error fetching missing item suggestions:", error);
    }
}

async function getHealthierAlternativeSuggestions() {
    try {
        const response = await fetch(`${apiUrl}/suggestions/healthier`);
        const data = await response.json();
        healthierAlternativesList.innerHTML = "";
        if (data.suggestions.length === 0) {
            healthierAlternativesList.innerHTML = "<li>No healthier alternatives found</li>";
        } else {
            data.suggestions.forEach(item => {
                const li = document.createElement("li");
                li.textContent = item;
                healthierAlternativesList.appendChild(li);
            });
        }
    } catch (error) {
        console.error("Error fetching healthier alternative suggestions:", error);
    }
}

async function getExpiryReminders() {
    try {
        const response = await fetch(`${apiUrl}/reminders/expiry`);
        const data = await response.json();
        expiryRemindersList.innerHTML = "";
        if (data.reminders.length === 0) {
            expiryRemindersList.innerHTML = "<li>No expiry reminders</li>";
        } else {
            data.reminders.forEach(item => {
                const li = document.createElement("li");
                li.textContent = item;
                expiryRemindersList.appendChild(li);
            });
        }
    } catch (error) {
        console.error("Error fetching expiry reminders:", error);
    }
}

async function loadCategories() {
    try {
        const response = await fetch(`${apiUrl}/categories`);
        const categories = await response.json();

        categoriesList.innerHTML = "";
        // populate category select (manual add)
        if (itemCategorySelect) {
            // clear existing options except the first
            itemCategorySelect.innerHTML = '<option value="">Select category (optional)</option>';
            for (const categoryName of Object.keys(categories)) {
                const opt = document.createElement('option');
                opt.value = categoryName;
                opt.textContent = categoryName;
                itemCategorySelect.appendChild(opt);
            }
        }

        for (const [categoryName, items] of Object.entries(categories)) {
            const categoryDiv = document.createElement("div");
            categoryDiv.className = "category";

            const categoryHeader = document.createElement("div");
            categoryHeader.className = "category-header";
            categoryHeader.innerHTML = `
                <span>${categoryName}</span>
                <span class="toggle">▼</span>
            `;

            const categoryItems = document.createElement("div");
            categoryItems.className = "category-items";

            const itemsUl = document.createElement("ul");
            items.forEach(item => {
                const li = document.createElement("li");
                li.className = "category-item";

                const nameSpan = document.createElement('span');
                nameSpan.className = 'category-item-name';
                nameSpan.textContent = item;

                const actionsDiv = document.createElement('div');
                actionsDiv.className = 'category-item-actions';

                const addBtn = document.createElement('button');
                addBtn.className = 'add-category-item-btn';
                addBtn.textContent = 'Add';
                addBtn.addEventListener('click', () => {
                    // Pre-fill the manual add form so user can edit before confirming
                    if (itemNameInput) itemNameInput.value = item;
                    if (itemCategorySelect) itemCategorySelect.value = categoryName;
                    if (itemUnitInput) itemUnitInput.value = '';
                    // bring the form into view and focus the unit input
                    try {
                        const formEl = itemNameInput.closest('.add-item-form') || itemNameInput;
                        formEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    } catch (e) {}
                    if (itemUnitInput) itemUnitInput.focus();
                });

                actionsDiv.appendChild(addBtn);
                li.appendChild(nameSpan);
                li.appendChild(actionsDiv);
                itemsUl.appendChild(li);
            });

            categoryItems.appendChild(itemsUl);

            categoryHeader.addEventListener("click", () => {
                categoryItems.classList.toggle("open");
                categoryHeader.querySelector(".toggle").textContent = categoryItems.classList.contains("open") ? "▲" : "▼";
            });

            categoryDiv.appendChild(categoryHeader);
            categoryDiv.appendChild(categoryItems);
            categoriesList.appendChild(categoryDiv);
        }
    } catch (error) {
        console.error("Error loading categories:", error);
    }
}

async function markAsPurchased() {
    try {
        const response = await fetch(`${apiUrl}/purchase`, { method: "POST" });
        const result = await response.json();
        alert(result.message || "Items marked as purchased!");
        refreshAllData();
    } catch (error) {
        console.error("Error marking items as purchased:", error);
    }
}

function refreshAllData() {
    getGroceryList();
    getMissingItemSuggestions();
    getHealthierAlternativeSuggestions();
    getExpiryReminders();
}

addItemBtn.addEventListener("click", addItem);
purchaseBtn.addEventListener("click", markAsPurchased);

// Initial load
refreshAllData();
loadCategories();

// Auto-refresh every 30 seconds
setInterval(refreshAllData, 30000);

// ============ CHATBOT ============

const chatbotOpener = document.getElementById("chatbot-opener");
const chatbotWindow = document.getElementById("chatbot-window");
const chatbotCloser = document.getElementById("chatbot-closer");
const chatbotMessages = document.getElementById("chatbot-messages");
const chatbotInput = document.getElementById("chatbot-input");
const chatbotSendBtn = document.getElementById("chatbot-send-btn");

chatbotOpener.addEventListener("click", () => chatbotWindow.classList.remove("hidden"));
chatbotCloser.addEventListener("click", () => chatbotWindow.classList.add("hidden"));
chatbotSendBtn.addEventListener("click", sendChatMessage);
chatbotInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        sendChatMessage();
    }
});

function addChatMessage(message, sender) {
    const messageElement = document.createElement("div");
    messageElement.classList.add("chatbot-message", `${sender}-message`);
    messageElement.textContent = message;
    chatbotMessages.appendChild(messageElement);
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
}

async function sendChatMessage() {
    const message = chatbotInput.value.trim();
    if (!message) return;

    addChatMessage(message, "user");
    chatbotInput.value = "";

    try {
        const response = await fetch(`${apiUrl}/chatbot`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message })
        });
        const data = await response.json();
        addChatMessage(data.reply, "bot");
        if (data.refresh) {
            refreshAllData();
        }
    } catch (error) {
        console.error("Error sending chat message:", error);
        addChatMessage("Sorry, I'm having trouble connecting to the server.", "bot");
    }
}

