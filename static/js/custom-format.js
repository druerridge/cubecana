const MODE = {
    DRAFT: 'draft',
    SEALED: 'sealed',
};

const MIN_PACKS_PER_ROW = 1;
const MAX_PACKS_PER_ROW = 16;
const MAX_TOTAL_PACKS = 24;
const LONG_DRAFT_PACKS = 8;
const MIN_RECOMMENDED_SEALED_PACKS = 6;

// Each preset is a list of sets; packs per set and the name suffix depend on the mode.
const PRESET_SET_LISTS = [
    {name: "Ursula Block", setIds: () => ["1", "2", "3", "4"]},
    {name: "Jafar Block", setIds: () => ["5", "6", "7", "8"]},
    // Uses the newest sets once retail sets load, so it tracks new releases.
    {name: "Last 4 Sets", setIds: () => retailSets.slice(-4).map(s => s.id)},
];

const PRESET_MODE_SETTINGS = {
    [MODE.SEALED]: {nameSuffix: "Super Sealed", packsPerSet: 4},
    [MODE.DRAFT]: {nameSuffix: "Draft", packsPerSet: 1},
};

function getPresets(mode) {
    const {nameSuffix, packsPerSet} = PRESET_MODE_SETTINGS[mode];
    return PRESET_SET_LISTS.map(preset => ({
        name: `${preset.name} ${nameSuffix}`,
        mode,
        rows: preset.setIds().map(setId => ({setId, count: packsPerSet})),
    }));
}

const modeToggle = document.getElementById('mode-toggle');
const nameInput = document.getElementById('format-name');
const presetsContainer = document.getElementById('presets');
const rowsContainer = document.getElementById('pack-rows');
const emptyRowsText = document.getElementById('empty-rows-text');
const addRowButton = document.getElementById('add-row-btn');
const clearRowsButton = document.getElementById('clear-rows-btn');
const totalPacksElement = document.getElementById('total-packs');
const roundOrderList = document.getElementById('round-order');
const packBreakdownList = document.getElementById('pack-breakdown');
const warningsContainer = document.getElementById('warnings');
const startButton = document.getElementById('start-btn');
const configPreview = document.getElementById('config-preview');

let retailSets = []; // [{id, name}]
let state = {
    mode: MODE.SEALED,
    name: '',
    rows: [],
};

function setName(setId) {
    const retailSet = retailSets.find(s => s.id === setId);
    return retailSet ? retailSet.name : `Set ${setId}`;
}

function totalPacks() {
    return state.rows.reduce((sum, row) => sum + row.count, 0);
}

function clampCount(count) {
    return Math.max(MIN_PACKS_PER_ROW, Math.min(MAX_PACKS_PER_ROW, count));
}

// URL format: ?mode=sealed&name=...&packs=5x4,6x4,7x4,8x4
function readStateFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const mode = params.get('mode');
    if (mode === MODE.DRAFT || mode === MODE.SEALED) {
        state.mode = mode;
    }
    state.name = params.get('name') || '';
    const packs = params.get('packs');
    if (packs) {
        state.rows = packs.split(',')
            .map(entry => entry.split('x'))
            .filter(([setId, count]) => setId && retailSets.some(s => s.id === setId) && !isNaN(parseInt(count)))
            .map(([setId, count]) => ({setId, count: clampCount(parseInt(count))}));
    }
}

function writeStateToUrl() {
    const params = new URLSearchParams();
    params.set('mode', state.mode);
    if (state.name) {
        params.set('name', state.name);
    }
    if (state.rows.length > 0) {
        params.set('packs', state.rows.map(row => `${row.setId}x${row.count}`).join(','));
    }
    history.replaceState(null, '', `${window.location.pathname}?${params.toString()}`);
}

function getWarnings() {
    const warnings = [];
    const total = totalPacks();
    if (state.rows.length === 0) {
        warnings.push({text: 'Add at least one set.', isError: true});
    }
    if (total > MAX_TOTAL_PACKS) {
        warnings.push({text: `Too many packs: max is ${MAX_TOTAL_PACKS} per player.`, isError: true});
    }
    if (state.mode === MODE.DRAFT && total > LONG_DRAFT_PACKS && total <= MAX_TOTAL_PACKS) {
        warnings.push({text: `${total} draft rounds is a long draft (retail draft is 4).`, isError: false});
    }
    if (state.mode === MODE.SEALED && total > 0 && total < MIN_RECOMMENDED_SEALED_PACKS) {
        warnings.push({text: `Fewer than ${MIN_RECOMMENDED_SEALED_PACKS} packs may make it hard to build a 60-card deck.`, isError: false});
    }
    return warnings;
}

function renderModeToggle() {
    modeToggle.querySelectorAll('button').forEach(button => {
        button.classList.toggle('active', button.dataset.mode === state.mode);
    });
    startButton.textContent = state.mode === MODE.DRAFT ? 'Draft!' : 'Sealed!';
    startButton.className = state.mode;
}

function renderRows() {
    rowsContainer.innerHTML = '';
    emptyRowsText.style.display = state.rows.length === 0 ? 'block' : 'none';
    clearRowsButton.disabled = state.rows.length === 0;
    const template = document.getElementById('pack-row-template');

    state.rows.forEach((row, index) => {
        const clone = template.content.cloneNode(true);

        clone.querySelector('.pack-row-index').textContent = `${index + 1}.`;

        const select = clone.querySelector('.pack-row-set');
        retailSets.forEach(retailSet => {
            const option = document.createElement('option');
            option.value = retailSet.id;
            option.textContent = `${retailSet.id}. ${retailSet.name}`;
            select.appendChild(option);
        });
        select.value = row.setId;
        select.addEventListener('change', () => {
            row.setId = select.value;
            update();
        });

        clone.querySelector('.pack-row-count').textContent = row.count;

        const minusButton = clone.querySelector('.pack-row-minus');
        minusButton.disabled = row.count <= MIN_PACKS_PER_ROW;
        minusButton.addEventListener('click', () => {
            row.count = clampCount(row.count - 1);
            update();
        });

        const plusButton = clone.querySelector('.pack-row-plus');
        plusButton.disabled = row.count >= MAX_PACKS_PER_ROW;
        plusButton.addEventListener('click', () => {
            row.count = clampCount(row.count + 1);
            update();
        });

        const upButton = clone.querySelector('.pack-row-up');
        upButton.disabled = index === 0;
        upButton.addEventListener('click', () => moveRow(index, index - 1));

        const downButton = clone.querySelector('.pack-row-down');
        downButton.disabled = index === state.rows.length - 1;
        downButton.addEventListener('click', () => moveRow(index, index + 1));

        clone.querySelector('.pack-row-remove').addEventListener('click', () => {
            state.rows.splice(index, 1);
            update();
        });

        rowsContainer.appendChild(clone);
    });
}

function renderSummary() {
    const total = totalPacks();
    totalPacksElement.textContent = total;

    roundOrderList.innerHTML = '';
    packBreakdownList.innerHTML = '';
    if (state.mode === MODE.DRAFT) {
        let round = 1;
        state.rows.forEach(row => {
            const li = document.createElement('li');
            const lastRound = round + row.count - 1;
            const roundText = row.count === 1 ? `Round ${round}` : `Rounds ${round}–${lastRound}`;
            li.textContent = `${roundText}: ${setName(row.setId)}`;
            roundOrderList.appendChild(li);
            round = lastRound + 1;
        });
    } else {
        // Sealed: order doesn't matter, so combine duplicate sets.
        const countsBySet = new Map();
        state.rows.forEach(row => countsBySet.set(row.setId, (countsBySet.get(row.setId) || 0) + row.count));
        countsBySet.forEach((count, setId) => {
            const li = document.createElement('li');
            li.textContent = `${count} × ${setName(setId)}`;
            packBreakdownList.appendChild(li);
        });
    }
    roundOrderList.style.display = roundOrderList.children.length ? 'block' : 'none';
    packBreakdownList.style.display = packBreakdownList.children.length ? 'block' : 'none';

    warningsContainer.innerHTML = '';
    const warnings = getWarnings();
    warnings.forEach(warning => {
        const div = document.createElement('div');
        div.className = warning.isError ? 'warning error' : 'warning';
        div.textContent = warning.text;
        warningsContainer.appendChild(div);
    });
    startButton.disabled = warnings.some(warning => warning.isError);
}

function update() {
    renderModeToggle();
    renderPresets();
    renderRows();
    renderSummary();
    writeStateToUrl();
}

function moveRow(fromIndex, toIndex) {
    const [row] = state.rows.splice(fromIndex, 1);
    state.rows.splice(toIndex, 0, row);
    update();
}

function addRow() {
    // Default to the set after the last row's set, so building a block is quick.
    let setId = retailSets[0].id;
    if (state.rows.length > 0) {
        const lastIndex = retailSets.findIndex(s => s.id === state.rows[state.rows.length - 1].setId);
        setId = retailSets[Math.min(lastIndex + 1, retailSets.length - 1)].id;
    }
    state.rows.push({setId, count: 1});
    update();
}

function applyPreset(preset) {
    state.mode = preset.mode;
    state.name = preset.name;
    state.rows = preset.rows.map(row => ({...row}));
    nameInput.value = state.name;
    update();
}

function renderPresets() {
    presetsContainer.innerHTML = '';
    getPresets(state.mode).forEach(preset => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'cf-btn preset-btn';
        button.textContent = preset.name;
        button.title = preset.rows.map(row => `${row.count}× ${setName(row.setId)}`).join(', ');
        button.addEventListener('click', () => applyPreset(preset));
        presetsContainer.appendChild(button);
    });
}

function buildConfig() {
    return {
        mode: state.mode,
        name: state.name || 'Custom Format',
        packs: state.rows.map(row => ({setId: row.setId, count: row.count})),
    };
}

function onStart() {
    // Stage 1: no backend yet. Stage 2 will POST this config to generate a draftmancer file
    // and hand it to generateDraftmancerSession.
    const config = buildConfig();
    configPreview.textContent = JSON.stringify(config, null, 2);
    configPreview.style.display = 'block';
    popToastNotification(`${state.mode === MODE.DRAFT ? 'Draft' : 'Sealed'} isn't wired up yet - config shown below.`);
}

modeToggle.querySelectorAll('button').forEach(button => {
    button.addEventListener('click', () => {
        state.mode = button.dataset.mode;
        update();
    });
});

nameInput.addEventListener('input', () => {
    state.name = nameInput.value;
    writeStateToUrl();
});

addRowButton.addEventListener('click', addRow);
clearRowsButton.addEventListener('click', () => {
    state.rows = [];
    update();
});
startButton.addEventListener('click', onStart);

function onRetrieveRetailSetsSuccess(responseText) {
    retailSets = JSON.parse(responseText).sets.map(s => ({id: s.id, name: s.name}));
    readStateFromUrl();
    nameInput.value = state.name;
    update();
}

addRowButton.disabled = true;
request(`${window.location.origin}/api/retail_sets?page=1&per_page=100&order=asc`, null, (responseText) => {
    addRowButton.disabled = false;
    onRetrieveRetailSetsSuccess(responseText);
}, null, 'POST');
