// Format Analysis JavaScript
// Import request function from shared.js (will be available globally)

// Get set ID from URL
const urlParts = window.location.pathname.split('/');
const setId = urlParts[urlParts.indexOf('retail-set') + 1];

// Global variables for charts and data
let cardTypeChart = null;
let strengthChart = null;
let willpowerChart = null;
let traitInkCostChart = null;
let setData = null;
let draftmancerData = null;

// DOM elements
const maxPodSizeInput = document.getElementById('maxPodSize');
const boostersPerPlayerInput = document.getElementById('boostersPerPlayer');
const traitSelect = document.getElementById('traitSelect');
const traitTable = document.getElementById('traitTable');

// Sample data structure (will be replaced with actual API data)
const sampleSetData = {
    cards: [
        // Sample cards with different types and traits
        { name: "Elsa - Snow Queen", type: "Character", traits: ["Hero", "Queen", "Sorcerer"], strength: 4, willpower: 6, inkCost: 8, rarity: "Legendary" },
        { name: "Let It Go", type: "Song", traits: ["Song"], strength: null, willpower: null, inkCost: 5, rarity: "Super Rare" },
        { name: "Freeze", type: "Action", traits: ["Action"], strength: null, willpower: null, inkCost: 2, rarity: "Common" },
        { name: "Beast's Castle", type: "Location", traits: ["Location", "Castle"], strength: null, willpower: 5, inkCost: 4, rarity: "Uncommon" },
        { name: "Lantern", type: "Item", traits: ["Item"], strength: null, willpower: null, inkCost: 2, rarity: "Common" },
        // Add more sample cards for demonstration
        { name: "Mickey Mouse - Brave Little Tailor", type: "Character", traits: ["Hero", "Hero"], strength: 2, willpower: 3, inkCost: 3, rarity: "Common" },
        { name: "Donald Duck - Boisterous Fowl", type: "Character", traits: ["Ally", "Duck"], strength: 2, willpower: 2, inkCost: 2, rarity: "Common" },
        { name: "Goofy - Knight for a Day", type: "Character", traits: ["Ally", "Knight"], strength: 1, willpower: 4, inkCost: 3, rarity: "Uncommon" },
    ],
    slots: {
        "CommonSlot": { rarity: "Common", weight: 10 },
        "UncommonSlot": { rarity: "Uncommon", weight: 3 },
        "RareSlot": { rarity: "Rare", weight: 1 },
        "SuperRareSlot": { rarity: "Super Rare", weight: 0.3 },
        "LegendarySlot": { rarity: "Legendary", weight: 0.1 }
    }
};

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    loadSetData();
    setupEventListeners();
});

function setupEventListeners() {
    maxPodSizeInput.addEventListener('change', updateTraitAnalysis);
    boostersPerPlayerInput.addEventListener('change', updateTraitAnalysis);
    // Note: traitSelect event listener is now handled in updateTraitAnalysis
    // since the dropdown gets recreated when the table updates
}

async function loadSetData() {
    try {
        // Load analysis data from API
        const analysisUrl = `${window.location.origin}/api/retail_sets/${setId}/analysis`;
        
        // Use the global request function from shared.js
        request(analysisUrl, null, (responseText) => {
            const analysisData = JSON.parse(responseText);
            processAnalysisData(analysisData);
            initializeCharts();
            populateTraitDropdown();
            updateAllCharts();
        }, (error) => {
            console.error('Error loading analysis data:', error);
            // Use sample data as fallback
            setData = sampleSetData;
            initializeCharts();
            populateTraitDropdown();
            updateAllCharts();
        }, 'GET');
        
    } catch (error) {
        console.error('Error loading set data:', error);
        // Use sample data as fallback
        setData = sampleSetData;
        initializeCharts();
        populateTraitDropdown();
        updateAllCharts();
    }
}

function processAnalysisData(analysisData) {
    // Convert API data to the format expected by our charts
    setData = {
        cardTypes: analysisData.cardTypes,
        traits: analysisData.traits,
        strengthDistribution: analysisData.strengthDistribution,
        willpowerDistribution: analysisData.willpowerDistribution,
        // Use the card data from the API
        cards: analysisData.cards || sampleSetData.cards
    };
}

function initializeCharts() {
    // Initialize Card Type Pie Chart
    const cardTypeCtx = document.getElementById('cardTypeChart').getContext('2d');
    cardTypeChart = new Chart(cardTypeCtx, {
        type: 'pie',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'
                ],
                borderColor: '#333',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: {
                        color: 'white'
                    }
                }
            }
        }
    });

    // Initialize Strength Chart
    const strengthCtx = document.getElementById('strengthChart').getContext('2d');
    strengthChart = new Chart(strengthCtx, {
        type: 'bar',
        data: {
            labels: ['0', '1', '2', '3', '4', '5', '6', '7', '8+'],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    stacked: true,
                    title: {
                        display: true,
                        text: 'Ink Cost',
                        color: 'white'
                    },
                    ticks: { color: 'white' },
                    grid: { color: '#555' }
                },
                y: {
                    stacked: true,
                    title: {
                        display: true,
                        text: 'Number of Cards',
                        color: 'white'
                    },
                    ticks: { color: 'white' },
                    grid: { color: '#555' }
                }
            },
            plugins: {
                legend: {
                    labels: { color: 'white' }
                }
            }
        }
    });

    // Initialize Willpower Chart
    const willpowerCtx = document.getElementById('willpowerChart').getContext('2d');
    willpowerChart = new Chart(willpowerCtx, {
        type: 'bar',
        data: {
            labels: ['0', '1', '2', '3', '4', '5', '6', '7', '8+'],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    stacked: true,
                    title: {
                        display: true,
                        text: 'Ink Cost',
                        color: 'white'
                    },
                    ticks: { color: 'white' },
                    grid: { color: '#555' }
                },
                y: {
                    stacked: true,
                    title: {
                        display: true,
                        text: 'Number of Cards',
                        color: 'white'
                    },
                    ticks: { color: 'white' },
                    grid: { color: '#555' }
                }
            },
            plugins: {
                legend: {
                    labels: { color: 'white' }
                }
            }
        }
    });

    // Initialize Trait by Ink Cost Chart
    const traitInkCostCtx = document.getElementById('traitInkCostChart').getContext('2d');
    traitInkCostChart = new Chart(traitInkCostCtx, {
        type: 'bar',
        data: {
            labels: ['0', '1', '2', '3', '4', '5', '6', '7', '8+'],
            datasets: [{
                label: 'Cards with Selected Trait',
                data: [],
                backgroundColor: '#36A2EB',
                borderColor: '#333',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Ink Cost',
                        color: 'white'
                    },
                    ticks: { color: 'white' },
                    grid: { color: '#555' }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Number of Cards',
                        color: 'white'
                    },
                    ticks: { color: 'white' },
                    grid: { color: '#555' },
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    labels: { color: 'white' }
                },
                title: {
                    display: true,
                    text: 'Cards by Ink Cost (Select a trait above)',
                    color: 'white',
                    font: { size: 16 }
                }
            }
        }
    });
}

function updateAllCharts() {
    updateCardTypeChart();
    updateStrengthChart();
    updateWillpowerChart();
}

function updateCardTypeChart() {
    if (!setData || !cardTypeChart) return;

    let typeCounts;
    if (setData.cardTypes) {
        // Use API data
        typeCounts = setData.cardTypes;
    } else {
        // Fall back to calculating from cards array
        typeCounts = {};
        setData.cards.forEach(card => {
            typeCounts[card.type] = (typeCounts[card.type] || 0) + 1;
        });
    }

    cardTypeChart.data.labels = Object.keys(typeCounts);
    cardTypeChart.data.datasets[0].data = Object.values(typeCounts);
    cardTypeChart.update();
}

function populateTraitDropdown() {
    if (!setData) return;

    let traits;
    if (setData.traits) {
        // Use API data
        traits = setData.traits;
    } else {
        // Fall back to extracting from cards array
        const traitSet = new Set();
        setData.cards.forEach(card => {
            if (card.traits) {
                card.traits.forEach(trait => traitSet.add(trait));
            }
        });
        traits = Array.from(traitSet);
    }

    const sortedTraits = traits.sort();
    traitSelect.innerHTML = '';
    
    // Populate dropdown with traits, no empty option
    sortedTraits.forEach(trait => {
        const option = document.createElement('option');
        option.value = trait;
        option.textContent = trait;
        traitSelect.appendChild(option);
    });
    
    // Set the first trait as selected by default
    if (sortedTraits.length > 0) {
        traitSelect.value = sortedTraits[0];
    }
    
    // Remove any existing event listeners and add a fresh one
    traitSelect.removeEventListener('change', updateTraitAnalysis);
    traitSelect.addEventListener('change', updateTraitAnalysis);
    
    // Trigger initial analysis with the first trait
    updateTraitAnalysis();
}

function updateTraitAnalysis() {
    const selectedTrait = traitSelect.value;
    console.log('updateTraitAnalysis called with trait:', selectedTrait);
    
    if (!selectedTrait || !setData) {
        console.log('No trait selected or no data available');
        return; // Exit early if no data or trait
    }

    const maxPodSize = parseInt(maxPodSizeInput.value);
    const boostersPerPlayer = parseInt(boostersPerPlayerInput.value);

    // Calculate trait analysis
    const cardsWithTrait = setData.cards.filter(card => 
        card.traits && card.traits.includes(selectedTrait)
    );
    
    console.log(`Found ${cardsWithTrait.length} cards with trait "${selectedTrait}"`);

    // Calculate expected counts based on rarity and frequency
    let totalExpectedAtTable = 0;

    cardsWithTrait.forEach(card => {
        // Simple calculation - in a real implementation, this would be more complex
        // based on actual slot weights and pack generation logic
        const rarityMultiplier = getRarityMultiplier(card.rarity);
        const expectedPerBooster = rarityMultiplier;
        const expectedAtTable = expectedPerBooster * boostersPerPlayer * maxPodSize;

        totalExpectedAtTable += expectedAtTable;
    });

    const totalExpectedPerSeat = totalExpectedAtTable / maxPodSize;
    
    console.log(`Expected at table: ${totalExpectedAtTable.toFixed(1)}, per seat: ${totalExpectedPerSeat.toFixed(1)}`);

    // Update only the data cells, keeping the dropdown intact
    const tbody = traitTable.querySelector('tbody');
    const existingRow = tbody.querySelector('tr');
    const cells = existingRow.querySelectorAll('td');
    
    // Update the data cells (cells[1] and cells[2], keeping cells[0] with dropdown)
    cells[1].textContent = totalExpectedAtTable.toFixed(1);
    cells[2].textContent = totalExpectedPerSeat.toFixed(1);
    
    // Update the trait ink cost chart
    updateTraitInkCostChart(selectedTrait);
}

function updateTraitInkCostChart(selectedTrait) {
    if (!selectedTrait || !setData || !traitInkCostChart) {
        // Clear the chart if no trait is selected
        traitInkCostChart.data.datasets[0].data = new Array(9).fill(0);
        traitInkCostChart.options.plugins.title.text = 'Cards by Ink Cost (Select a trait above)';
        traitInkCostChart.update();
        return;
    }

    // Calculate distribution of cards with the selected trait by ink cost
    const inkCostCounts = new Array(9).fill(0); // 0-8+ ink costs

    const cardsWithTrait = setData.cards.filter(card => 
        card.traits && card.traits.includes(selectedTrait)
    );

    cardsWithTrait.forEach(card => {
        const inkCost = Math.min(card.inkCost, 8); // Cap at 8 for 8+ category
        inkCostCounts[inkCost]++;
    });

    // Update chart
    traitInkCostChart.data.datasets[0].data = inkCostCounts;
    traitInkCostChart.data.datasets[0].label = `Cards with "${selectedTrait}" trait`;
    traitInkCostChart.options.plugins.title.text = `"${selectedTrait}" Cards by Ink Cost`;
    traitInkCostChart.update();
}

function getRarityMultiplier(rarity) {
    // Simplified rarity weights - in reality this would come from the draftmancer file
    const rarityWeights = {
        'Common': 0.7,
        'Uncommon': 0.25,
        'Rare': 0.04,
        'Super Rare': 0.008,
        'Legendary': 0.002
    };
    return rarityWeights[rarity] || 0.1;
}

function updateStrengthChart() {
    if (!setData || !strengthChart) return;

    let strengthByCost;
    let strengthValues = new Set();

    if (setData.strengthDistribution) {
        // Use API data
        strengthByCost = setData.strengthDistribution;
        Object.values(strengthByCost).forEach(costData => {
            Object.keys(costData).forEach(strength => strengthValues.add(parseInt(strength)));
        });
    } else {
        // Fall back to calculating from cards array
        strengthByCost = {};
        for (let cost = 0; cost <= 8; cost++) {
            strengthByCost[cost] = {};
        }

        setData.cards.forEach(card => {
            if (card.strength !== null && card.strength !== undefined) {
                const cost = Math.min(card.inkCost, 8);
                const strength = card.strength;
                
                strengthValues.add(strength);
                strengthByCost[cost][strength] = (strengthByCost[cost][strength] || 0) + 1;
            }
        });
    }

    // Prepare chart data
    const sortedStrengthValues = Array.from(strengthValues).sort((a, b) => a - b);
    const datasets = sortedStrengthValues.map((strength, index) => {
        // Use a red to yellow to green spectrum for strength values
        const maxStrength = Math.max(...sortedStrengthValues);
        const ratio = strength / Math.max(maxStrength, 1); // Normalize to 0-1
        let color;
        
        if (ratio <= 0.5) {
            // Red to yellow (low to medium strength)
            const r = 255;
            const g = Math.round(255 * ratio * 2);
            const b = 0;
            color = `rgb(${r}, ${g}, ${b})`;
        } else {
            // Yellow to green (medium to high strength)
            const r = Math.round(255 * (1 - (ratio - 0.5) * 2));
            const g = 255;
            const b = 0;
            color = `rgb(${r}, ${g}, ${b})`;
        }
        
        return {
            label: `Strength ${strength}`,
            data: Object.keys(strengthByCost).map(cost => strengthByCost[cost][strength] || 0),
            backgroundColor: color,
            borderColor: '#333',
            borderWidth: 1
        };
    });

    strengthChart.data.datasets = datasets;
    strengthChart.update();
}

function updateWillpowerChart() {
    if (!setData || !willpowerChart) return;

    let willpowerByCost;
    let willpowerValues = new Set();

    if (setData.willpowerDistribution) {
        // Use API data
        willpowerByCost = setData.willpowerDistribution;
        Object.values(willpowerByCost).forEach(costData => {
            Object.keys(costData).forEach(willpower => willpowerValues.add(parseInt(willpower)));
        });
    } else {
        // Fall back to calculating from cards array
        willpowerByCost = {};
        for (let cost = 0; cost <= 8; cost++) {
            willpowerByCost[cost] = {};
        }

        setData.cards.forEach(card => {
            if (card.willpower !== null && card.willpower !== undefined) {
                const cost = Math.min(card.inkCost, 8);
                const willpower = card.willpower;
                
                willpowerValues.add(willpower);
                willpowerByCost[cost][willpower] = (willpowerByCost[cost][willpower] || 0) + 1;
            }
        });
    }

    // Prepare chart data
    const sortedWillpowerValues = Array.from(willpowerValues).sort((a, b) => a - b);
    const datasets = sortedWillpowerValues.map((willpower, index) => {
        // Use a blue to purple to pink spectrum for willpower values
        const maxWillpower = Math.max(...sortedWillpowerValues);
        const ratio = willpower / Math.max(maxWillpower, 1); // Normalize to 0-1
        let color;
        
        if (ratio <= 0.5) {
            // Blue to purple (low to medium willpower)
            const r = Math.round(128 * ratio * 2);
            const g = 0;
            const b = 255;
            color = `rgb(${r}, ${g}, ${b})`;
        } else {
            // Purple to pink (medium to high willpower)
            const r = Math.round(128 + 127 * (ratio - 0.5) * 2);
            const g = Math.round(64 * (ratio - 0.5) * 2);
            const b = Math.round(255 - 127 * (ratio - 0.5) * 2);
            color = `rgb(${r}, ${g}, ${b})`;
        }
        
        return {
            label: `Willpower ${willpower}`,
            data: Object.keys(willpowerByCost).map(cost => willpowerByCost[cost][willpower] || 0),
            backgroundColor: color,
            borderColor: '#333',
            borderWidth: 1
        };
    });

    willpowerChart.data.datasets = datasets;
    willpowerChart.update();
}
