const urlParts = window.location.pathname.split('/');
const setId = urlParts[urlParts.indexOf('retail-set') + 1];

let cardTypeChart = null;
let strengthChart = null;
let willpowerChart = null;
let traitInkCostChart = null;
let setData = null;
let draftmancerData = null;

const maxPodSizeInput = document.getElementById('maxPodSize');
const boostersPerPlayerInput = document.getElementById('boostersPerPlayer');
const traitSelect = document.getElementById('traitSelect');
const traitTable = document.getElementById('traitTable');

const sampleSetData = {
    cards: [
        { name: "Elsa - Snow Queen", type: "Character", traits: ["Hero", "Queen", "Sorcerer"], strength: 4, willpower: 6, inkCost: 8, rarity: "Legendary" },
        { name: "Let It Go", type: "Song", traits: ["Song"], strength: null, willpower: null, inkCost: 5, rarity: "Super Rare" },
        { name: "Freeze", type: "Action", traits: ["Action"], strength: null, willpower: null, inkCost: 2, rarity: "Common" },
        { name: "Beast's Castle", type: "Location", traits: ["Location", "Castle"], strength: null, willpower: 5, inkCost: 4, rarity: "Uncommon" },
        { name: "Lantern", type: "Item", traits: ["Item"], strength: null, willpower: null, inkCost: 2, rarity: "Common" },
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

document.addEventListener('DOMContentLoaded', function() {
    loadSetData();
    setupEventListeners();
});

function setupEventListeners() {
    maxPodSizeInput.addEventListener('change', updateTraitAnalysis);
    boostersPerPlayerInput.addEventListener('change', updateTraitAnalysis);
}

async function loadSetData() {
    try {
        const analysisUrl = `${window.location.origin}/api/retail_sets/${setId}/analysis`;
        
        request(analysisUrl, null, (responseText) => {
            const analysisData = JSON.parse(responseText);
            processAnalysisData(analysisData);
            initializeCharts();
            populateTraitDropdown();
            
            setTimeout(() => {
                updateAllCharts();
            }, 100);
        }, (error) => {
            console.error('Error loading analysis data:', error);
            setData = sampleSetData;
            initializeCharts();
            populateTraitDropdown();
            setTimeout(() => {
                updateAllCharts();
            }, 100);
        }, 'GET');
        
    } catch (error) {
        console.error('Error loading set data:', error);
        setData = sampleSetData;
        initializeCharts();
        populateTraitDropdown();
        updateAllCharts();
    }
}

function processAnalysisData(analysisData) {
    // Convert new API response format to expected frontend format
    setData = {
        cardTypes: analysisData.countAtTableByCardType || {},
        strengthDistribution: analysisData.strengthDistributionByCost || {},
        willpowerDistribution: analysisData.willpowerDistributionByCost || {},
        costDistribution: analysisData.costDistributionByClassification || {},
        setId: analysisData.setId
    };
    
    // Extract traits from costDistributionByClassification keys
    if (analysisData.costDistributionByClassification) {
        setData.traits = Object.keys(analysisData.costDistributionByClassification);
    } else {
        setData.traits = [];
    }
    
    // Generate chart data from the API response
    setData.chartData = generateChartDataFromResponse(analysisData);
    
    // Set default settings if not provided
    setData.settings = {
        boostersPerPlayer: 4,
        playersCount: 8
    };
    
    boostersPerPlayerInput.value = setData.settings.boostersPerPlayer;
    maxPodSizeInput.value = setData.settings.playersCount;
}

function generateChartDataFromResponse(analysisData) {
    const chartData = {};
    
    // Generate card type chart data
    if (analysisData.countAtTableByCardType) {
        chartData.cardTypeChart = {
            labels: Object.keys(analysisData.countAtTableByCardType),
            data: Object.values(analysisData.countAtTableByCardType)
        };
    }
    
    // Generate strength chart data
    if (analysisData.strengthDistributionByCost) {
        chartData.strengthChart = generateStackedChartData(analysisData.strengthDistributionByCost, 'Strength');
    }
    
    // Generate willpower chart data
    if (analysisData.willpowerDistributionByCost) {
        chartData.willpowerChart = generateStackedChartData(analysisData.willpowerDistributionByCost, 'Willpower');
    }
    
    // Generate trait ink cost distributions for trait analysis
    chartData.traitInkCostDistributions = {};
    if (analysisData.costDistributionByClassification) {
        Object.keys(analysisData.costDistributionByClassification).forEach(trait => {
            chartData.traitInkCostDistributions[trait] = analysisData.costDistributionByClassification[trait];
        });
    }
    
    return chartData;
}

function generateStackedChartData(distributionByCost, label) {
    // Get all ink costs (0-8+)
    const inkCosts = ['0', '1', '2', '3', '4', '5', '6', '7', '8+'];
    
    // Get all unique stat values
    const allStatValues = new Set();
    Object.values(distributionByCost).forEach(costData => {
        Object.keys(costData).forEach(statValue => {
            allStatValues.add(parseInt(statValue));
        });
    });
    
    const sortedStatValues = Array.from(allStatValues).sort((a, b) => a - b);
    
    // Generate datasets for each stat value
    const datasets = sortedStatValues.map((statValue, index) => {
        const data = inkCosts.map(cost => {
            const costKey = cost === '8+' ? '8' : cost;
            const costData = distributionByCost[costKey] || {};
            return costData[statValue.toString()] || 0;
        });
        
        return {
            label: `${label} ${statValue}`,
            data: data,
            backgroundColor: generateColor(index),
            borderColor: '#333',
            borderWidth: 1
        };
    });
    
    return {
        labels: inkCosts,
        datasets: datasets
    };
}

function generateColor(index) {
    const colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40',
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'
    ];
    return colors[index % colors.length];
}

function initializeCharts() {
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

function getActiveInkCosts() {
    if (!setData || !setData.chartData) {
        return ['0', '1', '2', '3', '4', '5', '6', '7', '8+'];
    }

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
    
    sortedTraits.forEach(trait => {
        const option = document.createElement('option');
        option.value = trait;
        option.textContent = trait;
        traitSelect.appendChild(option);
    });
    
    if (sortedTraits.length > 0) {
        traitSelect.value = sortedTraits[0];
    }
    
    traitSelect.removeEventListener('change', updateTraitAnalysis);
    traitSelect.addEventListener('change', updateTraitAnalysis);
    
    updateTraitAnalysis();
}

function updateTraitAnalysis() {
    const selectedTrait = traitSelect.value;
    console.log('updateTraitAnalysis called with trait:', selectedTrait);
    
    if (!selectedTrait || !setData || !setData.costDistribution) {
        console.log('No trait selected or no data available');
        return;
    }

    const traitCostData = setData.costDistribution[selectedTrait];
    if (!traitCostData) {
        console.log(`No statistics found for trait "${selectedTrait}"`);
        return;
    }

    // Calculate total expected at table and per seat from cost distribution
    const totalExpectedAtTable = Object.values(traitCostData).reduce((sum, count) => sum + count, 0);
    const maxPodSize = parseInt(maxPodSizeInput.value) || 8;
    const totalExpectedPerSeat = totalExpectedAtTable / maxPodSize;
    
    console.log(`Expected at table: ${totalExpectedAtTable.toFixed(1)}, per seat: ${totalExpectedPerSeat.toFixed(1)}`);

    const tbody = traitTable.querySelector('tbody');
    const existingRow = tbody.querySelector('tr');
    const cells = existingRow.querySelectorAll('td');
    
    cells[1].textContent = totalExpectedAtTable.toFixed(1);
    cells[2].textContent = totalExpectedPerSeat.toFixed(1);
    
    updateTraitInkCostChart(selectedTrait);
}

function updateTraitInkCostChart(selectedTrait) {
    if (!selectedTrait || !setData || !traitInkCostChart) {
        traitInkCostChart.data.labels = [];
        traitInkCostChart.data.datasets[0].data = [];
        traitInkCostChart.options.plugins.title.text = 'Cards by Ink Cost (Select a trait above)';
        traitInkCostChart.update();
        return;
    }

    const traitDistributions = setData.chartData && setData.chartData.traitInkCostDistributions;
    if (!traitDistributions || !traitDistributions[selectedTrait]) {
        traitInkCostChart.data.labels = [];
        traitInkCostChart.data.datasets[0].data = [];
        traitInkCostChart.options.plugins.title.text = `No data for "${selectedTrait}" trait`;
        traitInkCostChart.update();
        return;
    }

    const inkCosts = ['0', '1', '2', '3', '4', '5', '6', '7', '8+'];
    const traitData = traitDistributions[selectedTrait];
    
    const inkCostCounts = inkCosts.map(label => {
        const cost = label === '8+' ? '8' : label;
        return traitData[cost] || 0;
    });

    traitInkCostChart.data.labels = inkCosts;
    traitInkCostChart.data.datasets[0].data = inkCostCounts;
    traitInkCostChart.data.datasets[0].label = `Cards with "${selectedTrait}" trait`;
    traitInkCostChart.options.plugins.title.text = `"${selectedTrait}" Cards by Ink Cost`;
    traitInkCostChart.update();
}

function getRarityMultiplier(rarity) {
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

    if (setData.chartData && setData.chartData.strengthChart) {
        const chartConfig = setData.chartData.strengthChart;
        
        strengthChart.data.labels = chartConfig.labels;
        strengthChart.data.datasets = chartConfig.datasets;
        
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

    if (setData.chartData && setData.chartData.willpowerChart) {
        const chartConfig = setData.chartData.willpowerChart;
        
        willpowerChart.data.labels = chartConfig.labels;
        willpowerChart.data.datasets = chartConfig.datasets;
        
        if (chartConfig.options && chartConfig.options.scales && chartConfig.options.scales.y) {
            const yScale = chartConfig.options.scales.y;
            if (yScale.suggestedMax !== null && yScale.suggestedMax !== undefined) {
                willpowerChart.options.scales.y.suggestedMax = yScale.suggestedMax;
            }
        }
        
        willpowerChart.update();
    }
}
