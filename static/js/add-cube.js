const submitButton = document.getElementById('submit-button')
const cardListInput = document.getElementById('cardListInput');
const currentUrl = window.location.href;
const cubeForm = document.getElementById('cubeForm');
const successModal = document.getElementById('successModal');
const modalMessage = document.getElementById('modalMessage');
const modalOkButton = document.getElementById('modalOkButton');

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
    cubeForm.cubeFeaturedCard.value = responseCube.featuredCardPrintingId || '';
    cubeForm.cubeDescription.value = responseCube.cubeDescription || '';
    cardListInput.value = toCardList(responseCube.nameToCardCount);
    cubeForm.cubeBoostersPerPlayer.value = responseCube.cubeSettings.boostersPerPlayer;
    cubeForm.cubeCardsPerBooster.value = responseCube.cubeSettings.cardsPerBooster;
    cubeForm.powerBand.value = responseCube.cubeSettings.powerBand;
    cubeId = responseCube.id;
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

function showSuccessModal(innerHtml) {
    modalMessage.innerHTML = innerHtml;
    successModal.style.display = 'flex';
}

modalOkButton.addEventListener('click', () => {
    successModal.style.display = 'none';
});

function postCreateCube() {
    const formData = {
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
            powerBand: cubeForm.powerBand.value
        }
    };

    request(`${window.location.origin}/api/cube`, JSON.stringify(formData), (responseText) => {
        const response = JSON.parse(responseText);
        const fullEditCubeLink = `${window.location.origin + response.editCubeLink}`;
        clearInputs();
        showSuccessModal(`Cube successfully created!<br \\>You <span class="emphasis-word">MUST</span> save this link to edit your cube:<br \\><br \\><a href="${fullEditCubeLink}">${fullEditCubeLink}</a>`);
    },() => {
        submitButton.disabled = false;
    },
    'POST');
}

submitButton.addEventListener('click', function(event) {
    event.preventDefault();
        
    hideError();
    submitButton.disabled = true;
    postCreateCube();
});