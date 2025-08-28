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
            
            // Add a small delay to ensure charts are fully initialized before updating
            setTimeout(() => {
                updateAllCharts();
            }, 100);
        }, (error) => {
            console.error('Error loading analysis data:', error);
            // Use sample data as fallback
            setData = sampleSetData;
            initializeCharts();
            populateTraitDropdown();
            setTimeout(() => {
                updateAllCharts();
            }, 100);
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
        traitCalculations: analysisData.traitCalculations,
        traitInkCostDistributions: analysisData.traitInkCostDistributions,
        chartData: analysisData.chartData,
        settings: analysisData.settings
    };
    
    if (analysisData.settings) {
        boostersPerPlayerInput.value = analysisData.settings.boostersPerPlayer;
        maxPodSizeInput.value = analysisData.settings.playersCount;
    }
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

// Helper function to determine which ink costs should be shown based on chart data
function getActiveInkCosts() {
    if (!setData || !setData.chartData) {
        return ['0', '1', '2', '3', '4', '5', '6', '7', '8+']; // Default all costs
    }

    // Use the strength chart labels as they represent the active ink costs
    return setData.chartData.strengthChart.labels || ['0', '1', '2', '3', '4', '5', '6', '7', '8+'];
}

function updateCardTypeChart() {
    if (!setData || !cardTypeChart || !setData.chartData) return;

    const chartData = setData.chartData.cardTypeChart;
    cardTypeChart.data.labels = chartData.labels;
    cardTypeChart.data.datasets[0].data = chartData.data;
    cardTypeChart.update();
}

function populateTraitDropdown() {
    if (!setData || !setData.traits) return;

    const sortedTraits = setData.traits.sort();
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
    
    if (!selectedTrait || !setData || !setData.traitCalculations) {
        console.log('No trait selected or no data available');
        return; // Exit early if no data or trait
    }

    const traitStats = setData.traitCalculations[selectedTrait];
    if (!traitStats) {
        console.log(`No statistics found for trait "${selectedTrait}"`);
        return;
    }

    const maxPodSize = parseInt(maxPodSizeInput.value);
    
    // Use pre-computed trait statistics
    const totalExpectedAtTable = traitStats.expectedAtTable;
    const totalExpectedPerSeat = traitStats.expectedInSeat;
    
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
        traitInkCostChart.data.labels = [];
        traitInkCostChart.data.datasets[0].data = [];
        traitInkCostChart.options.plugins.title.text = 'Cards by Ink Cost (Select a trait above)';
        traitInkCostChart.update();
        return;
    }

    // Use pre-computed trait ink cost distribution data
    const traitDistributions = setData.chartData && setData.chartData.traitInkCostDistributions;
    if (!traitDistributions || !traitDistributions[selectedTrait]) {
        // Clear chart if no data for this trait
        traitInkCostChart.data.labels = [];
        traitInkCostChart.data.datasets[0].data = [];
        traitInkCostChart.options.plugins.title.text = `No data for "${selectedTrait}" trait`;
        traitInkCostChart.update();
        return;
    }

    // Use the same active ink costs as the strength/willpower charts for consistency
    const activeInkCosts = setData.chartData.strengthChart.labels;
    const traitData = traitDistributions[selectedTrait];
    
    const inkCostCounts = activeInkCosts.map(label => {
        // Convert label back to cost number (handle "8+" case)
        const cost = label === '8+' ? '8' : label;
        return traitData[cost] || 0;
    });

    // Update chart labels and data
    traitInkCostChart.data.labels = activeInkCosts;
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

    // Use pre-computed chart data from backend
    if (setData.chartData && setData.chartData.strengthChart) {
        const chartConfig = setData.chartData.strengthChart;
        
        // Use the data directly from backend (already filtered to active ink costs)
        strengthChart.data.labels = chartConfig.labels;
        strengthChart.data.datasets = chartConfig.datasets;
        
        // Apply scaling options from backend if available
        if (chartConfig.options && chartConfig.options.scales && chartConfig.options.scales.y) {
            const yScale = chartConfig.options.scales.y;
            if (yScale.suggestedMax !== null && yScale.suggestedMax !== undefined) {
                strengthChart.options.scales.y.suggestedMax = yScale.suggestedMax;
            }
        }
        
        strengthChart.update();
    }
}

function updateWillpowerChart() {
    if (!setData || !willpowerChart) return;

    // Use pre-computed chart data from backend
    if (setData.chartData && setData.chartData.willpowerChart) {
        const chartConfig = setData.chartData.willpowerChart;
        
        // Use the data directly from backend (already filtered to active ink costs)
        willpowerChart.data.labels = chartConfig.labels;
        willpowerChart.data.datasets = chartConfig.datasets;
        
        // Apply scaling options from backend if available
        if (chartConfig.options && chartConfig.options.scales && chartConfig.options.scales.y) {
            const yScale = chartConfig.options.scales.y;
            if (yScale.suggestedMax !== null && yScale.suggestedMax !== undefined) {
                willpowerChart.options.scales.y.suggestedMax = yScale.suggestedMax;
            }
        }
        
        willpowerChart.update();
    }
}
