import { generateDraftmancerSession } from "draftmancer-connect";

let dots = 0;
const loadingText = document.getElementById('loading-text');
let intervalId = setInterval(() => {
    dots = (dots + 1) % 4;
    loadingText.textContent = 'Loading' + '.'.repeat(dots);
}, 500);

const currentUrl = window.location.href;
const cubeId = currentUrl.split('/cube/')[1].split("/draft")[0];
const draftNowButton = document.getElementById('draft-now-button');
const viewListButton = document.getElementById('view-list-button');
const cubeTitle = document.getElementById('cube-title');
const authorText = document.getElementById('author-text');
const cardCount = document.getElementById("element-cards")
const timesViewed = document.getElementById("element-times-viewed")
const timesDrafted = document.getElementById("element-times-drafted")
const cubeDraftmancerUrl = `/api/cube/${cubeId}/draftmancerFile`
const cubeInspectListUrl = `/cube/${cubeId}/inspect-list`

request(cubeDraftmancerUrl, null, (responseText) => {
    let response = JSON.parse(responseText);
    draftNowButton.disabled = false;
    if (isValidCardlistUrl(response.metadata.link)) {
        viewListButton.disabled = false
    }
    clearInterval(intervalId);
    loadingText.hidden = true;
    cubeTitle.textContent = response.metadata.cubeName;
    authorText.textContent = `By: ${response.metadata.author}`;
    cardCount.textContent = response.metadata.cardCount;
    timesViewed.textContent = response.metadata.timesViewed;
    timesDrafted.textContent = response.metadata.timesDrafted;

    draftNowButton.addEventListener('click', () => {
        let newTab = window.open("/loading");
        generateDraftmancerSession(response.draftmancerFile, newTab, response.metadata);
    });

    viewListButton.addEventListener('click', () => {
        window.open(cubeInspectListUrl);
    });
}, 
() => {
    newTab.close();
}, 
'GET');