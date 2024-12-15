import { generateDraftmancerSession } from "draftmancer-connect";

const container = document.getElementById('cubeContainer');

function populateCubes(cubes) {
    cubes.forEach(cube => {
        if ("content" in document.createElement("template")) {
            const template = document.getElementById("cube-list-element-template");
            const cubeDraftLink = `http://localhost:5000/cube/${cube.id}/draft`

            let clone = template.content.cloneNode(true);
            clone.getElementById("element-name").textContent = cube.name;
            clone.getElementById("element-cards").textContent = "(" + cube.cardCount + " cards)";
            clone.getElementById("element-author").textContent = "by: " + cube.author;
            clone.getElementById("copy-link-btn").addEventListener("click", function() {
                navigator.clipboard.writeText(cubeDraftLink);
                popToastNotification(`Copied draft link to your clipboard`);
            });
            clone.getElementById("element-link").href = cube.link;
            clone.getElementById("element-draft").addEventListener("click", function() {
                let newTab = window.open("/loading");
                const cubeDraftmancerUrl = `/api/cube/${cube.id}/draftmancerFile`
                request(cubeDraftmancerUrl, null, (responseText) => {
                    let response = JSON.parse(responseText);
                    generateDraftmancerSession(response.draftmancerFile, newTab, response.metadata);
                }, 
                null, 
                'GET');
            });
            clone.getElementById("element-last-updated").textContent = "last updated: " + new Date(cube.lastUpdatedEpochSeconds * 1000).toDateString();
            let elementTags = clone.getElementById("element-tags")
            cube.tags.forEach(tag => {
                let tagElement = document.createElement("span");
                tagElement.classList.add("cube-tag");
                tagElement.textContent = tag;
                elementTags.appendChild(tagElement);
            });
        
            container.appendChild(clone);
        }
    });
}

function onRetrieveCubesSuccess(response) {
    const cubes = JSON.parse(response);
    populateCubes(cubes);
}

const url = "/api/cube";
request(url, null, onRetrieveCubesSuccess, null, 'GET');     