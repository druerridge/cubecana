
const submitButton = document.getElementById('submit-button')
const deleteButton = document.getElementById('delete-button')
const cardListInput = document.getElementById('cardListInput');
const currentUrl = window.location.href;
const cubeForm = document.getElementById('cubeForm');
const successNotification = document.getElementById('successNotification');
const editSecret = new URLSearchParams(window.location.search).get('editSecret');

// Store original values to track changes
let originalValues = {};

const cubeId = currentUrl.split('/edit-cube/')[1].split("?")[0];
const cubeUrl = `${window.location.origin}/api/cube/${cubeId}`;

request(cubeUrl, null, (responseText) => {
    const responseCube = JSON.parse(responseText);
    populateInputs(responseCube);
}, () => {  
}, 
'GET');

function getActiveTags() {
    const tags = document.getElementsByClassName('tag-button active');
    const activeTags = [];
    for (let i = 0; i < tags.length; i++) {
        activeTags.push(tags[i].innerText);
    }
    return activeTags;
}

function toCardList(nameToCardCount) {
    let cardList = '';
    for (const cardId in nameToCardCount) {
        cardList += `${nameToCardCount[cardId]} ${cardId}\n`;
    }
    return cardList;
}

function populateInputs(responseCube) {
    cubeForm.cubeName.value = responseCube.name;
    cubeForm.cubeLink.value = responseCube.link;
    cubeForm.cubeAuthor.value = responseCube.author;
    cubeForm.cubeFeaturedCard.value = responseCube.featuredCardPrintingId;
    cubeForm.cubeDescription.value = responseCube.cubeDescription;
    cardListInput.value = toCardList(responseCube.nameToCardCount);
    cubeForm.cubeBoostersPerPlayer.value = responseCube.cubeSettings.boostersPerPlayer;
    cubeForm.cubeCardsPerBooster.value = responseCube.cubeSettings.cardsPerBooster;
    cubeForm.cubePowerBand.value = responseCube.cubeSettings.powerBand;
    
    // Store original values for change detection
    originalValues = {
        cubeName: responseCube.name,
        cubeLink: responseCube.link,
        cubeAuthor: responseCube.author,
        cubeFeaturedCard: responseCube.featuredCardPrintingId,
        cubeDescription: responseCube.cubeDescription,
        cardListInput: toCardList(responseCube.nameToCardCount),
        cubeBoostersPerPlayer: responseCube.cubeSettings.boostersPerPlayer,
        cubeCardsPerBooster: responseCube.cubeSettings.cardsPerBooster,
        cubePowerBand: responseCube.cubeSettings.powerBand,
        tags: [...responseCube.tags] // Copy array
    };
    
    const tags = document.getElementsByClassName('tag-button');
    for (let i = 0; i < tags.length; i++) {
        if (responseCube.tags.includes(tags[i].innerText)) {
            tags[i].classList.add('active');
        }
    }
}

function clearInputs() {
    cubeForm.cubeName.value = '';
    cubeForm.cubeLink.value = '';
    cubeForm.cubeAuthor.value = '';
    cubeForm.cubeFeaturedCard.value = '';
    cubeForm.cubeDescription.value = '';
    cardListInput.value = '';
    cubeForm.cubeBoostersPerPlayer.value = 4;
    cubeForm.cubeCardsPerBooster.value = 12;
    const tags = document.getElementsByClassName('tag-button active');
    for (let i = 0; i < tags.length; i++) {
        tags[i].classList.remove('active');
    }
}

cardListInput.addEventListener('input', function() {
    validateForm();
});

// Add validation for all form fields
document.getElementById('cubeName').addEventListener('input', validateForm);
document.getElementById('cubeLink').addEventListener('input', validateForm);
document.getElementById('cubeAuthor').addEventListener('input', validateForm);
document.getElementById('cubeFeaturedCard').addEventListener('input', validateForm);
document.getElementById('cubeDescription').addEventListener('input', validateForm);
document.getElementById('cubeBoostersPerPlayer').addEventListener('input', validateForm);
document.getElementById('cubeCardsPerBooster').addEventListener('input', validateForm);
document.getElementById('cubePowerBand').addEventListener('change', validateForm);

// Add validation for tag changes
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('tag-button')) {
        // Delay validation slightly to allow tag state to update
        setTimeout(validateForm, 10);
    }
});

function validateForm() {
    // Check if card list has content (minimum requirement)
    const hasCardList = cardListInput.value.trim().length > 0;
    
    // Check if any field has changed from original values
    const currentTags = getActiveTags();
    const hasChanges = 
        cubeForm.cubeName.value !== originalValues.cubeName ||
        cubeForm.cubeLink.value !== originalValues.cubeLink ||
        cubeForm.cubeAuthor.value !== originalValues.cubeAuthor ||
        cubeForm.cubeFeaturedCard.value !== originalValues.cubeFeaturedCard ||
        cubeForm.cubeDescription.value !== originalValues.cubeDescription ||
        cardListInput.value !== originalValues.cardListInput ||
        cubeForm.cubeBoostersPerPlayer.value !== originalValues.cubeBoostersPerPlayer ||
        cubeForm.cubeCardsPerBooster.value !== originalValues.cubeCardsPerBooster ||
        cubeForm.cubePowerBand.value !== originalValues.cubePowerBand ||
        JSON.stringify(currentTags.sort()) !== JSON.stringify(originalValues.tags.sort());
    
    // Enable submit button only if there's a card list AND there are changes
    submitButton.disabled = !hasCardList || !hasChanges;
}

function putUpdateCube() {
    const formData = {
        id: cubeId,
        name: cubeForm.cubeName.value.trim(),
        tags: getActiveTags(),
        link: cubeForm.cubeLink.value.trim(),
        author: cubeForm.cubeAuthor.value.trim(),
        featuredCardPrintingId: cubeForm.cubeFeaturedCard.value.trim(),
        cubeDescription: cubeForm.cubeDescription.value.trim(),
        cardListText: cardListInput.value.trim(),
        cubeSettings: {
            boostersPerPlayer: cubeForm.cubeBoostersPerPlayer.value,
            cardsPerBooster: cubeForm.cubeCardsPerBooster.value,
            powerBand: cubeForm.cubePowerBand.value
        }
    };

    const url = `${window.location.origin}/api/cube/${cubeId}?editSecret=${editSecret}`;
    request(url, JSON.stringify(formData), (responseText) => {
        const response = JSON.parse(responseText);
        successNotification.style.display = 'block';
        successNotification.style.disabled = false;
        successNotification.innerHTML = "Successfully updated.";
    },() => {
        submitButton.disabled = false;
    },
    'PUT');
}

submitButton.addEventListener('click', function(event) {
    event.preventDefault();
        
    hideError();
    submitButton.disabled = true;
    putUpdateCube();
});

deleteButton.addEventListener('click', function(event) {
    event.preventDefault();
    if (confirm('Are you sure you want to delete this cube?')) {
        deleteButton.disabled = true;
        const url = `${window.location.origin}/api/cube/${cubeId}?editSecret=${editSecret}`;
        request(url, null, (responseText) => {
            successNotification.style.display = 'block';
            successNotification.style.disabled = false;
            successNotification.innerHTML = "Successfully deleted.";
            clearInputs();
            deleteButton.disabled = false;
        }, () => {
            alert('Failed to delete the cube.');
            deleteButton.disabled = false;
        }, 'DELETE');
    }

});