import { generateDraftmancerSession } from "draftmancer-connect";

const container = document.getElementById('retail-sets-container');
const loadingText = document.getElementById('loading-text');
const orderOptions = document.getElementById('orderOptions');
const pageNumbers = document.getElementById('page-numbers');
const prevPage = document.getElementById('prev-page');
const nextPage = document.getElementById('next-page');
const paginationDiv = document.getElementById('pagination');

function populateRetailSets(retailSets) {
    container.innerHTML = '';
    retailSets.forEach(retailSet => {
        if ("content" in document.createElement("template")) {
            const template = document.getElementById("cube-list-element-template");
            const retailSetDraftLink = `${window.location.origin}/retail_sets/${retailSet.id}/draft`

            let clone = template.content.cloneNode(true);
            clone.getElementById("cube-element-name").textContent = retailSet.name;
            clone.getElementById("cube-element-draft").addEventListener("click", function() {
                let newTab = window.open("/loading");
                const retailSetDraftmancerUrl = `${window.location.origin}/api/retail_sets/${retailSet.id}/draftmancerFile`
                request(retailSetDraftmancerUrl, null, (responseText) => {
                    let response = JSON.parse(responseText);
                    generateDraftmancerSession(response.draftmancerFile, newTab, response.metadata);
                }, 
                () => {
                    newTab.close();
                }, 
                'GET');
            });
            loadingText.disabled = true;
            container.appendChild(clone);
        }
    });
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

let order = 'asc';
const orderTypeParam = new URLSearchParams(window.location.search).get('order');
if (orderTypeParam) {
    order = orderTypeParam;
    orderOptions.value = order;
}

function updatePagination(totalPages) {
    if (totalPages === 1) {
        paginationDiv.style.display = 'none';
        paginationDiv.disabled = true;
        return;
    }
    pageNumbers.innerHTML = `Page ${currentPage} of ${totalPages}`;

    prevPage.disabled = currentPage === 1;
    nextPage.disabled = currentPage === totalPages;
}

orderOptions.addEventListener('change', () => {
    if (orderOptions.value != order) {
        order = orderOptions.value;
        refetchPage();
    }
});

function refetchPage() {
    window.location.search = `?page=${currentPage}&per_page=${perPage}&order=${order}`;
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

function onRetrieveRetailSetsSuccess(response) {
    const parsedRespone = JSON.parse(response);
    populateRetailSets(parsedRespone.sets);
    totalPages = Math.ceil(parsedRespone.totalSets / perPage);
    updatePagination(totalPages);
}

function fetchRetailSets(page, perPage, order) {
    const url = `${window.location.origin}/api/retail_sets?page=${page}&per_page=${perPage}&order=${order}`;
    request(url, null, onRetrieveRetailSetsSuccess, null, 'GET');
}

// Initial fetch
fetchRetailSets(currentPage, perPage, order);