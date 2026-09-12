let franchises = [];

const maximumFeaturedFranchises = 5;
const franchiseList = document.getElementById("franchise-list");
const franchiseSearch = document.getElementById("franchise-search");
const selectionStatus = document.getElementById("selection-status");
const clearFranchiseSelectionButton = document.getElementById("clear-franchise-selection");
const wildFranchise = document.getElementById("wild-franchise");
const wildFranchiseOptions = document.getElementById("wild-franchise-options");
const legality = document.getElementById("legality");
const removeUnplayables = document.getElementById("remove-unplayables");
const setYears = document.getElementById("set-years");
const draftButton = document.getElementById("draft-button");
const draftStatus = document.getElementById("draft-status");
const selectedFranchises = new Set([
    "Peter Pan",
    "Beauty and the Beast",
    "Aladdin",
    "Moana",
    "The Little Mermaid"
]);
const selectedSetIds = new Set();

function populateWildFranchiseOptions() {
    wildFranchiseOptions.replaceChildren();
    franchises.forEach((franchise) => {
        const option = document.createElement("option");
        option.value = franchise;
        wildFranchiseOptions.appendChild(option);
    });
}

function updateSelectionStatus() {
    selectionStatus.textContent =
        `${selectedFranchises.size} of ${maximumFeaturedFranchises} franchises selected`;
}

function renderFranchiseList() {
    const searchTerm = franchiseSearch.value.trim().toLocaleLowerCase();
    const matchingFranchises = franchises.filter((franchise) =>
        franchise.toLocaleLowerCase().includes(searchTerm)
    );
    const selectionLimitReached = selectedFranchises.size === maximumFeaturedFranchises;

    franchiseList.replaceChildren();

    if (matchingFranchises.length === 0) {
        const noResults = document.createElement("p");
        noResults.className = "no-results";
        noResults.textContent = "No franchises match your search.";
        franchiseList.appendChild(noResults);
        return;
    }

    const listItems = document.createDocumentFragment();
    matchingFranchises.forEach((franchise) => {
        const label = document.createElement("label");
        const checkbox = document.createElement("input");
        const isSelected = selectedFranchises.has(franchise);

        label.className = "franchise-option";
        checkbox.type = "checkbox";
        checkbox.value = franchise;
        checkbox.checked = isSelected;
        checkbox.disabled = selectionLimitReached && !isSelected;
        checkbox.addEventListener("change", () => {
            if (checkbox.checked) {
                selectedFranchises.add(franchise);
            } else {
                selectedFranchises.delete(franchise);
            }
            updateSelectionStatus();
            renderFranchiseList();
        });

        if (checkbox.disabled) {
            label.classList.add("is-unavailable");
        }

        label.append(checkbox, document.createTextNode(franchise));
        listItems.appendChild(label);
    });
    franchiseList.appendChild(listItems);
}

franchiseSearch.addEventListener("input", renderFranchiseList);
clearFranchiseSelectionButton.addEventListener("click", () => {
    selectedFranchises.clear();
    updateSelectionStatus();
    renderFranchiseList();
});
draftButton.addEventListener("click", submitDraftConfiguration);

function updateYearSelection(yearCheckbox, sets) {
    const selectedSetCount = sets.filter((retailSet) =>
        selectedSetIds.has(retailSet.id)
    ).length;

    yearCheckbox.checked = selectedSetCount === sets.length;
    yearCheckbox.indeterminate =
        selectedSetCount > 0 && selectedSetCount < sets.length;
}

function createSetYear(yearNumber, sets) {
    const year = document.createElement("section");
    const heading = document.createElement("label");
    const yearCheckbox = document.createElement("input");
    const options = document.createElement("div");

    year.className = "set-year";
    heading.className = "set-year-heading";
    yearCheckbox.type = "checkbox";
    yearCheckbox.setAttribute("aria-label", `Select all Year ${yearNumber} sets`);
    heading.append(yearCheckbox, document.createTextNode(`Year ${yearNumber}`));

    options.className = "set-options";
    sets.forEach((retailSet) => {
        const label = document.createElement("label");
        const checkbox = document.createElement("input");

        label.className = "set-option";
        checkbox.type = "checkbox";
        checkbox.value = retailSet.id;
        checkbox.checked = selectedSetIds.has(retailSet.id);
        checkbox.addEventListener("change", () => {
            if (checkbox.checked) {
                selectedSetIds.add(retailSet.id);
            } else {
                selectedSetIds.delete(retailSet.id);
            }
            updateYearSelection(yearCheckbox, sets);
        });
        label.append(checkbox, document.createTextNode(retailSet.name));
        options.appendChild(label);
    });

    yearCheckbox.addEventListener("change", () => {
        options.querySelectorAll("input").forEach((checkbox) => {
            checkbox.checked = yearCheckbox.checked;
            if (checkbox.checked) {
                selectedSetIds.add(checkbox.value);
            } else {
                selectedSetIds.delete(checkbox.value);
            }
        });
        updateYearSelection(yearCheckbox, sets);
    });

    updateYearSelection(yearCheckbox, sets);
    year.append(heading, options);
    return year;
}

function renderRetailSets(retailSets) {
    setYears.replaceChildren();

    if (retailSets.length === 0) {
        const message = document.createElement("p");
        message.className = "set-loading";
        message.textContent = "No retail sets are available.";
        setYears.appendChild(message);
        return;
    }

    for (let index = 0; index < retailSets.length; index += 4) {
        const yearNumber = Math.floor(index / 4) + 1;
        const setsForYear = retailSets.slice(index, index + 4);
        setYears.appendChild(createSetYear(yearNumber, setsForYear));
    }
}

async function loadRetailSets() {
    try {
        const response = await fetch("/api/retail_sets?page=1&per_page=100&order=asc");
        if (!response.ok) {
            throw new Error(`Retail set request failed with status ${response.status}`);
        }
        const { sets } = await response.json();
        sets.forEach((retailSet) => selectedSetIds.add(retailSet.id));
        renderRetailSets(sets);
    } catch (error) {
        console.error("Unable to load retail sets.", error);
        const message = document.createElement("p");
        message.className = "set-loading";
        message.textContent = "Retail sets could not be loaded. Please try again later.";
        setYears.replaceChildren(message);
    }
}

async function loadFranchises() {
    try {
        const response = await fetch("/api/franchises");
        if (!response.ok) {
            throw new Error(`Franchise request failed with status ${response.status}`);
        }
        const data = await response.json();
        franchises = data.franchises;
        populateWildFranchiseOptions();
        renderFranchiseList();
    } catch (error) {
        console.error("Unable to load franchises.", error);
        const message = document.createElement("p");
        message.className = "no-results";
        message.textContent = "Franchises could not be loaded. Please try again later.";
        franchiseList.replaceChildren(message);
    }
}

function getDraftConfiguration() {
    return {
        wildFranchise: wildFranchise.value,
        featuredFranchises: Array.from(selectedFranchises),
        legality: legality.value,
        removeUnplayables: removeUnplayables.checked,
        setIds: Array.from(selectedSetIds)
    };
}

async function submitDraftConfiguration() {
    draftButton.disabled = true;
    draftStatus.textContent = "Sending draft configuration...";

    try {
        const response = await fetch("/api/double-feature-draft", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(getDraftConfiguration())
        });
        if (!response.ok) {
            throw new Error(`Draft request failed with status ${response.status}`);
        }
        draftStatus.textContent = "Draft configuration received.";
    } catch (error) {
        console.error("Unable to submit the draft configuration.", error);
        draftStatus.textContent = "Draft configuration could not be submitted. Please try again.";
    } finally {
        draftButton.disabled = false;
    }
}

updateSelectionStatus();
loadFranchises();
loadRetailSets();
