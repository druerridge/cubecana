
const submitButton = document.getElementById('submit-button')
const cardListInput = document.getElementById('cardListInput');
const currentUrl = window.location.href;
const cubeForm = document.getElementById('cubeForm');
const successNotification = document.getElementById('successNotification');
let cubeId = null;

function getActiveTags() {
    const tags = document.getElementsByClassName('tag-button active');
    const activeTags = [];
    for (let i = 0; i < tags.length; i++) {
        activeTags.push(tags[i].innerText);
    }
    return activeTags;
}

function toCardList(cardIdToCardCount) {
    let cardList = '';
    for (const cardId in cardIdToCardCount) {
        cardList += `${cardIdToCardCount[cardId]} ${cardId}\n`;
    }
    return cardList;
}

function populateInputs(responseCube) {
    cubeForm.cubeName.value = responseCube.name;
    cubeForm.cubeLink.value = responseCube.link;
    cubeForm.cubeAuthor.value = responseCube.author;
    cardListInput.value = toCardList(responseCube.cardIdToCardCount);
    cubeForm.cubeBoostersPerPlayer.value = responseCube.cubeSettings.boostersPerPlayer;
    cubeForm.cubeCardsPerBooster.value = responseCube.cubeSettings.cardsPerBooster;
    cubeId = responseCube.id;
    const tags = document.getElementsByClassName('tag-button');
    for (let i = 0; i < tags.length; i++) {
        if (responseCube.tags.includes(tags[i].innerText)) {
            tags[i].classList.add('active');
        }
    }
}

if (currentUrl.includes('edit-cube')) {
    const cubeId = currentUrl.split('/edit-cube/')[1].split("?")[0];
    const cubeUrl = `/api/cube/${cubeId}`;
    request(cubeUrl, null, (responseText) => {
        const responseCube = JSON.parse(responseText);
        populateInputs(responseCube);
    }, () => {  
    }, 
    'GET');
}

function clearInputs() {
    cubeForm.cubeName.value = '';
    cubeForm.cubeLink.value = '';
    cubeForm.cubeAuthor.value = '';
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
        cardListText: cardListInput.value.trim(),
        cubeSettings: {
            boostersPerPlayer: cubeForm.cubeBoostersPerPlayer.value,
            cardsPerBooster: cubeForm.cubeCardsPerBooster.value
        }
    };

    const editSecret = new URLSearchParams(window.location.search).get('editSecret');
    const url = `/api/cube/${cubeId}?editSecret=${editSecret}`;
    request(url, JSON.stringify(formData), (responseText) => {
        const response = JSON.parse(responseText);
        successNotification.innerText = "Successfully uploaded.";
        successNotification.style.display = 'block';
        successNotification.style.disabled = false;
        const fullEditCubeLink = `${window.location.origin + response.editCubeLink}`;
        successNotification.innerHTML = `Successfully uploaded.<br \\>Save this link somewhere to edit your cube:<br \\><a href="${fullEditCubeLink}"'>${fullEditCubeLink}</a>`;
        clearInputs();
    },() => {
        submitButton.disabled = false;
    },
    'PUT');
}

function postCreateCube() {
    const formData = {
        name: cubeForm.cubeName.value.trim(),
        tags: getActiveTags(),
        link: cubeForm.cubeLink.value.trim(),
        author: cubeForm.cubeAuthor.value.trim(),
        cardListText: cardListInput.value.trim(),
        cubeSettings: {
            boostersPerPlayer: cubeForm.cubeBoostersPerPlayer.value,
            cardsPerBooster: cubeForm.cubeCardsPerBooster.value
        }
    };

    request('/api/cube', JSON.stringify(formData), (responseText) => {
        const response = JSON.parse(responseText);
        successNotification.innerText = "Successfully uploaded.";
        successNotification.style.display = 'block';
        successNotification.style.disabled = false;
        const fullEditCubeLink = `${window.location.origin + response.editCubeLink}`;
        successNotification.innerHTML = `Successfully uploaded.<br \\>Save this link somewhere to edit your cube:<br \\><a href="${fullEditCubeLink}"'>${fullEditCubeLink}</a>`;
        // clearInputs();
    },() => {
        submitButton.disabled = false;
    },
    'POST');
}

submitButton.addEventListener('click', function(event) {
    event.preventDefault();
        
    hideError();
    submitButton.disabled = true;
    if (window.location.href.includes('edit-cube')) {
        putUpdateCube();
    } else {
        postCreateCube();
    }
});