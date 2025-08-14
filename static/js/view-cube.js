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
const cubeDescription = document.getElementById("cube-description")
const descriptionText = document.getElementById("description-text")
const headerImage = document.getElementById("header-image")
const featuredCardImage = document.getElementById("featured-card-image")
const cardListContainer = document.getElementById("card-list-container")
const cardList = document.getElementById("card-list")
const instructionsSection = document.getElementById("instructions")

const apiCubeUrl = `/api/cube/${cubeId}`
const draftmancerFileUrl = `/api/cube/${cubeId}/draftmancerFile`
const cubeInspectListUrl = `/cube/${cubeId}/inspect-list`

request(apiCubeUrl, null, (responseText) => {
    let response = JSON.parse(responseText);
    draftNowButton.disabled = false;
    if (isValidCardlistUrl(response.link)) {
        viewListButton.disabled = false
    }
    clearInterval(intervalId);
    loadingText.hidden = true;
    
    // Populate basic cube information
    cubeTitle.textContent = response.name;
    authorText.textContent = `By: ${response.author}`;
    cardCount.textContent = Object.keys(response.nameToCardCount).length;
    timesViewed.textContent = response.timesViewed;
    timesDrafted.textContent = response.timesDrafted;

    // Show and populate description
    if (response.description) {
        descriptionText.textContent = response.description;
        cubeDescription.style.display = 'block';
    }

    // Show and populate featured card image in header
    if (response.featuredCardImageLink) {
        featuredCardImage.src = response.featuredCardImageLink;
        headerImage.style.display = 'block';
    }

    // Show and populate card list
    if (response.nameToCardCount) {
        populateCardList(response.nameToCardCount);
        cardListContainer.style.display = 'block';
    }

    // Show instructions and buttons
    instructionsSection.style.display = 'block';

    draftNowButton.addEventListener('click', () => {
        let newTab = window.open("/loading");
        request(draftmancerFileUrl, null, (responseText) => {
                    let response = JSON.parse(responseText);
                    generateDraftmancerSession(response.draftmancerFile, newTab, response.metadata);
                }, 
                () => {
                    newTab.close();
                }, 
                'GET');
    });

    viewListButton.addEventListener('click', () => {
        window.open(cubeInspectListUrl);
    });
}, 
() => {
    newTab.close();
}, 
'GET');

function populateCardList(nameToCardCount) {
    // Convert to array and sort by card name
    const cardArray = Object.entries(nameToCardCount).sort((a, b) => a[0].localeCompare(b[0]));
    
    cardList.innerHTML = '';
    cardArray.forEach(([cardName, count]) => {
        const cardItem = document.createElement('div');
        cardItem.className = 'card-item';
        
        const nameDiv = document.createElement('div');
        nameDiv.className = 'card-name';
        nameDiv.textContent = cardName;
        
        const countDiv = document.createElement('div');
        countDiv.className = 'card-count';
        countDiv.textContent = count;
        
        cardItem.appendChild(nameDiv);
        cardItem.appendChild(countDiv);
        cardList.appendChild(cardItem);
    });
}