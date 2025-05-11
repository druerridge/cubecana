import { generateDraftmancerSession } from "draftmancer-connect";

const container = document.getElementById('cubeContainer');
const loadingText = document.getElementById('loading-text');
const sortOptions = document.getElementById('sortOptions');
const orderOptions = document.getElementById('orderOptions');
const pageNumbers = document.getElementById('page-numbers');
const prevPage = document.getElementById('prev-page');
const nextPage = document.getElementById('next-page');
const filtersContainer = document.getElementById('filters-container');

function renderActiveFilters() {
    filtersContainer.innerHTML = '';
    if (tagsToFilterBy && tagsToFilterBy.length > 0 && tagsToFilterBy[0] !== ',') {
        tagsToFilterBy.forEach(tag => {
            const filterElement = document.createElement('span');
            filterElement.style.marginRight = '10px';
            filterElement.style.padding = '5px';
            filterElement.style.border = '1px solid gray';
            filterElement.style.borderRadius = '3px';
            filterElement.style.backgroundColor = 'lightgray';
            filterElement.style.cursor = 'pointer';

            filterElement.textContent = `${tag} ✕`;
            filterElement.addEventListener('click', () => {
                tagsToFilterBy = tagsToFilterBy.filter(item => item !== tag);
                currentPage = 1;
                refetchPage();
            });

            filtersContainer.appendChild(filterElement);
        });
    }
}

function populateCubes(cubes) {
    container.innerHTML = '';
    cubes.forEach(cube => {
        if ("content" in document.createElement("template")) {
            const template = document.getElementById("cube-list-element-template");
            const cubeDraftLink = `${window.location.origin}/cube/${cube.id}/draft`;

            let clone = template.content.cloneNode(true);
            clone.getElementById("element-name").textContent = cube.name;
            clone.getElementById("element-cards").textContent = cube.cardCount;
            clone.getElementById("element-times-viewed").textContent = cube.timesViewed;
            clone.getElementById("element-times-drafted").textContent = cube.timesDrafted;
            clone.getElementById("element-author").textContent = "by: " + cube.author;
            clone.getElementById("copy-link-btn").addEventListener("click", function() {
                navigator.clipboard.writeText(cubeDraftLink);
                popToastNotification(`Copied draft link to your clipboard`);
            });
            clone.getElementById("element-link").href = `${window.location.origin}/cube/${cube.id}/inspect-list`;
            if (!isValidCardlistUrl(cube.link)) {
                clone.getElementById("element-link").href = "/404.html";
                clone.getElementById("element-link").style.disabled = true;
                clone.getElementById("inspect-btn").style.disabled = true;
                clone.getElementById("inspect-btn").disabled = true;
                clone.getElementById("element-link").disabled = true;
            }
            clone.getElementById("element-draft").addEventListener("click", function() {
                let newTab = window.open("/loading");
                const cubeDraftmancerUrl = `${window.location.origin}/api/cube/${cube.id}/draftmancerFile`;
                request(cubeDraftmancerUrl, null, (responseText) => {
                    let response = JSON.parse(responseText);
                    generateDraftmancerSession(response.draftmancerFile, newTab, response.metadata);
                }, 
                () => {
                    newTab.close();
                }, 
                'GET');
            });
            clone.getElementById("element-last-updated").textContent = "last updated: " + new Date(cube.lastUpdatedEpochSeconds * 1000).toDateString();
            let elementTags = clone.getElementById("element-tags");
            cube.tags.forEach(tag => {
                let tagElement = document.createElement("span");
                tagElement.classList.add("cube-tag");
                tagElement.textContent = tag;
                if (!tag.startsWith('Power:')) {
                    tagElement.classList.add("clickable-cube-tag");
                
                    tagElement.addEventListener('click', () => {
                        if (!tagsToFilterBy) {
                            tagsToFilterBy = [];
                        } 
                        if (!tagsToFilterBy.includes(tag)) {
                            tagsToFilterBy.push(tag);
                            currentPage = 1;
                            refetchPage();
                        }
                    });
                }
                elementTags.appendChild(tagElement);
            });
            loadingText.disabled = true;
            container.appendChild(clone);
        }
    });
    renderActiveFilters();
}

let totalPages = -1;
let currentPage = 1;
const pageParam = new URLSearchParams(window.location.search).get('page');
if (pageParam) {
    currentPage = parseInt(pageParam);
}   

let perPage = 20;
const perPageParam = new URLSearchParams(window.location.search).get('per_page');
if (perPageParam) {
    perPage = parseInt(perPageParam);
}

let sort = 'rank';
const sortTypeParam = new URLSearchParams(window.location.search).get('sort');
if (sortTypeParam) {
    sort = sortTypeParam;
    sortOptions.value = sort;
}

let order = 'desc';
const orderTypeParam = new URLSearchParams(window.location.search).get('order');
if (orderTypeParam) {
    order = orderTypeParam;
    orderOptions.value = order;
}

let tagsToFilterBy = null;
const tagsToFilterByParam = new URLSearchParams(window.location.search).get('tags');
if (tagsToFilterByParam) {
    tagsToFilterBy = new URL(window.location.href).searchParams.getAll('tags');
}

function updatePagination(totalPages) {
    pageNumbers.innerHTML = `Page ${currentPage} of ${totalPages}`;

    prevPage.disabled = currentPage === 1;
    nextPage.disabled = currentPage === totalPages;
}

sortOptions.addEventListener('change', () => {
    if (sortOptions.value != sort) {
        sort = sortOptions.value;
        currentPage = 1;
        refetchPage();
    }
});

orderOptions.addEventListener('change', () => {
    if (orderOptions.value != order) {
        order = orderOptions.value;
        currentPage = 1;
        refetchPage();
    }
});

function setSearchParams(searchParams) {
    let keys = [];
    searchParams.keys().forEach((key) => {
        keys.push(key);
    });
    keys.forEach((key) => {      
        searchParams.delete(key);
    });
    
    searchParams.append('page', currentPage);
    searchParams.append('per_page', perPage);
    searchParams.append('sort', sort);
    searchParams.append('order', order);
    if (tagsToFilterBy && tagsToFilterBy.length > 0 && tagsToFilterBy[0] !== ',') {
        tagsToFilterBy.forEach((tag) => {
            searchParams.append('tags', tag);
        });
    }
}

function fetchCubes(page, perPage, sort, order) {
    const url = new URL(`${window.location.origin}/api/cube`);
    setSearchParams(url.searchParams);
    request(url, null, onRetrieveCubesSuccess, null, 'GET');
}

function refetchPage() {
    let searchParams = new URLSearchParams(window.location.search);
    setSearchParams(searchParams);
    window.location.search = searchParams.toString();
}

prevPage.addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        refetchPage();
    }
});

nextPage.addEventListener('click', () => {
    if (currentPage < totalPages) {
        currentPage++;
        refetchPage();
    }
});

function onRetrieveCubesSuccess(response) {
    const parsedRespone = JSON.parse(response);
    populateCubes(parsedRespone.cubes);
    totalPages = Math.ceil(parsedRespone.totalCubes / perPage);
    updatePagination(totalPages);
}

// Initial fetch
fetchCubes(currentPage, perPage, sort, order);
