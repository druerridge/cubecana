
const submitButton = document.getElementById('submit-button')
const cardListInput = document.getElementById('cardListInput');
const currentUrl = window.location.href;
const cubeForm = document.getElementById('cubeForm');

function getActiveTags() {
    const tags = document.getElementsByClassName('tag-button active');
    const activeTags = [];
    for (let i = 0; i < tags.length; i++) {
        activeTags.push(tags[i].innerText);
    }
    return activeTags;
}

function populateInputs(responseCube) {
    cubeForm.cubeName.value = responseCube.name;
    cubeForm.cubeLink.value = responseCube.link;
    cubeForm.cubeAuthor.value = responseCube.author;
    cardListInput.value = JSON.stringify(responseCube.cardIdToCardCount); // TODO: convert to cardListText
    cubeForm.cubeBoostersPerPlayer.value = responseCube.cubeSettings.boostersPerPlayer;
    cubeForm.cubeCardsPerBooster.value = responseCube.cubeSettings.cardsPerBooster;
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

submitButton.addEventListener('click', function(event) {
    event.preventDefault();
    
    const successNotification = document.getElementById('successNotification');
    
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
    
    hideError();
    submitButton.disabled = true;
    const url = '/api/cube';
    const verb = 'POST';
    if (window.location.href.includes('cube-edit')) {
        verb = 'PUT';
    }
    request(url, JSON.stringify(formData), (responseText) => {
        const response = JSON.parse(responseText);
        successNotification.innerText = "Successfully uploaded.";
        successNotification.style.display = 'block';
        successNotification.style.disabled = false;
        successNotification.innerHTML = `Successfully uploaded.<br \\>Save this link somewhere to edit your cube:<br \\><a href="${response.editCubeLink}"'>${response.editCubeLink}</a>`;
        // clearInputs();
    },() => {
        submitButton.disabled = false;
    },
    verb);
});