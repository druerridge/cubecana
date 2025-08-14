import { generateDraftmancerSession } from "draftmancer-connect";

let dots = 0;
let currentCardList = null; // Store the card list data for copying
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
const copyListButton = document.getElementById("copy-list-button")
const copyListSection = document.getElementById("copy-list-section")
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
    
    // Show the views and drafts elements
    timesViewed.removeAttribute('hidden');
    timesDrafted.removeAttribute('hidden');
    
    // Show the eye and hand images
    const eyeImage = document.querySelector('img[alt="Times Viewed"]');
    const handImage = document.querySelector('img[alt="Times Drafted"]');
    if (eyeImage) eyeImage.removeAttribute('hidden');
    if (handImage) handImage.removeAttribute('hidden');
    
    // Show the parent span elements for views and drafts
    const viewsSpan = document.querySelector('.views');
    const draftsSpan = document.querySelector('.drafts');
    if (viewsSpan) viewsSpan.style.display = 'inline';
    if (draftsSpan) draftsSpan.style.display = 'inline';

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
        currentCardList = response.nameToCardCount; // Store for copying
        populateCardList(response.nameToCardCount);
        cardListContainer.style.display = 'block';
        copyListSection.style.display = 'block'; // Show copy button section
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

    // Add copy list functionality
    copyListButton.addEventListener('click', () => {
        if (currentCardList) {
            copyCardList(currentCardList);
        }
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

function copyCardList(nameToCardCount) {
    // Convert to array, sort by card name, and format as text
    const cardArray = Object.entries(nameToCardCount).sort((a, b) => a[0].localeCompare(b[0]));
    const listText = cardArray.map(([cardName, count]) => {
        return `${count} ${cardName}`;
    }).join('\n');
    
    // Copy to clipboard
    navigator.clipboard.writeText(listText).then(() => {
        // Visual feedback
        const originalText = copyListButton.textContent;
        copyListButton.textContent = 'Copied!';
        copyListButton.style.background = 'linear-gradient(45deg, #4CAF50, #66BB6A)';
        
        setTimeout(() => {
            copyListButton.textContent = originalText;
            copyListButton.style.background = 'linear-gradient(45deg, #2196F3, #21CBF3)';
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy: ', err);
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = listText;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        
        // Visual feedback
        const originalText = copyListButton.textContent;
        copyListButton.textContent = 'Copied!';
        setTimeout(() => {
            copyListButton.textContent = originalText;
        }, 2000);
    });
}