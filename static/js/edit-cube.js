
const submitButton = document.getElementById('submit-button')
const deleteButton = document.getElementById('delete-button')
const cardListInput = document.getElementById('cardListInput');
const currentUrl = window.location.href;
const cubeForm = document.getElementById('cubeForm');
const successNotification = document.getElementById('successNotification');
const editSecret = new URLSearchParams(window.location.search).get('editSecret');

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
    submitButton.disabled = cardListInput.value.trim().length === 0;
});

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