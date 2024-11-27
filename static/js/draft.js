import { generateDraftmancerSession } from "draftmancer-connect";


const fileInfo = document.getElementById('fileInfo');
const fileNameSpan = document.getElementById('fileName');
const removeFileButton = document.getElementById('removeFileButton');

const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');

const draftFromTtsButton = document.getElementById('ttsDraftButton');
const saveFromTtsButton = document.getElementById('ttsSaveButton');
let saveFromCardListButton = document.getElementById('cardListSaveButton');
let draftFromCardListButton = document.getElementById('cardListDraftButton');
let cardsPerBooster = document.getElementById('cardsPerBooster');
let boostersPerPlayer = document.getElementById('boostersPerPlayer');
let ttsInput = null;

removeFileButton.addEventListener('click', () => {
    fileInfo.style.display = 'none';
    fileInput.value = '';
    ttsInput = null;
    fileNameSpan.textContent = '';
    dropZone.style.display = 'block';
    saveFromTtsButton.disabled = true;
    draftFromTtsButton.disabled = true;
});

dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = 'green';
});

dropZone.addEventListener('dragleave', () => {
    dropZone.style.borderColor = '#ccc';
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = '#ccc';
    const files = e.dataTransfer.files;
    handleFiles(files);
});

fileInput.addEventListener('change', (e) => {
    const files = e.target.files;
    handleFiles(files);
});

function handleFiles(files) {
    if (files.length > 0 && files[0].type === 'application/json') {
        const file = files[0];
        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target.result;
            if (content.length > 50000000) {
                showError('File is too large. Please upload a file smaller than 50MB.');
                return;
            }
            try {
                JSON.parse(content);
                ttsInput = content;
            } catch (e) {
                console.error(e);
                showError('Invalid JSON file. Please upload a valid JSON file.');
            }
        };
        reader.readAsText(file);
        fileNameSpan.textContent = file.name;
        fileInfo.style.display = 'block';
        dropZone.style.display = 'none';
        saveFromTtsButton.disabled = false;
        draftFromTtsButton.disabled = false;
    } else {
        showError('no file or file is not a json file');
    }
}

draftFromTtsButton.addEventListener('click', async _ => {
    hideError();

    var url = "/dreamborn-to-draftmancer/";
    var data = JSON.stringify({ "dreamborn_export": ttsInput, "settings": { "cards_per_booster": cardsPerBooster.value, "boosters_per_player": boostersPerPlayer.value } });
    let newTab = window.open("/loading");
    request(url, data, (responseText) => {
        let response = JSON.parse(responseText);
        generateDraftmancerSession(response.draftmancerFile, newTab, response.metadata);
    }, (xhr) => {
        newTab.close();
    });
});

saveFromTtsButton.addEventListener('click', async _ => {
    hideError();

    var url = "/dreamborn-to-draftmancer/";
    var data = JSON.stringify({ "dreamborn_export": ttsInput, "settings": { "cards_per_booster": cardsPerBooster.value, "boosters_per_player": boostersPerPlayer.value } });
    request(url, data, (responseText) => {
        let response = JSON.parse(responseText);
        download(response.draftmancerFile, "custom-cube.draftmancer.txt", "txt");
    });
});

saveFromCardListButton.addEventListener('click', async _ => {
    hideError();

    const cardListInput = document.getElementById('cardListInput').value.trim();
    var url = "/card-list-to-draftmancer/";
    var data = JSON.stringify({ "card_list": cardListInput, "settings": { "cards_per_booster": cardsPerBooster.value, "boosters_per_player": boostersPerPlayer.value } });
    request(url, data, (responseText) => {
        let response = JSON.parse(responseText);
        download(response.draftmancerFile, "custom-cube.draftmancer.txt", "txt");
    });
});

draftFromCardListButton.addEventListener('click', async _ => {
    hideError();

    const cardListInput = document.getElementById('cardListInput').value.trim();
    var url = "/card-list-to-draftmancer/";
    var data = JSON.stringify({ "card_list": cardListInput, "settings": { "cards_per_booster": cardsPerBooster.value, "boosters_per_player": boostersPerPlayer.value } });
    let newTab = window.open("/loading");
    request(url, data, (responseText) => {
        let response = JSON.parse(responseText);
        generateDraftmancerSession(response.draftmancerFile, newTab, response.metadata);
    }, (xhr) => {
        newTab.close();
    });
});

cardListInput.addEventListener('input', () => {
    saveFromCardListButton.disabled = cardListInput.value.trim().length === 0;
    draftFromCardListButton.disabled = cardListInput.value.trim().length === 0;
});