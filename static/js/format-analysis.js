const urlParts = window.location.pathname.split('/');
const isCubeAnalysis = urlParts.includes('cube') && urlParts.includes('analysis');
const cubeId = isCubeAnalysis ? urlParts[urlParts.indexOf('cube') + 1] : null;
const setId = !isCubeAnalysis && urlParts.includes('retail-set') ? urlParts[urlParts.indexOf('retail-set') + 1] : null;

let cardTypeChart = null;
let strengthChart = null;
let willpowerChart = null;
let loreChart = null;
let ratingChart = null;
let traitInkCostChart = null;
let inkabilityChart = null;
let setData = null;
let draftmancerData = null;

const maxPodSizeInput = document.getElementById('maxPodSize');
const boostersPerPlayerInput = document.getElementById('boostersPerPlayer');
const cardsPerPackInput = document.getElementById('cardsPerPack');
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
    setupDynamicBackButton();
    setInputValuesFromUrlParams();
    loadFormatData();
    setupEventListeners();
});

function setupDynamicBackButton() {
    const backLink = document.getElementById('back-link');
    const analysisTitle = document.getElementById('analysis-title');
    
    // Check if this is a cube analysis page
    if (isCubeAnalysis && cubeId) {
        backLink.href = `/cube/${cubeId}`;
        backLink.textContent = '← Back to Cube';
        analysisTitle.textContent = `Cube ID: ${cubeId}`;
    } else {
        backLink.href = "/retail-directory";
        backLink.textContent = '← Back to Retail Directory';
        analysisTitle.textContent = 'Retail Set: ' + (setId ? setId : 'Unknown');
    }
    // For retail sets, keep the default values (already set in HTML)
}

function getUrlParam(name, defaultValue) {
    const urlParams = new URLSearchParams(window.location.search);
    const value = urlParams.get(name);
    return value ? parseInt(value) : defaultValue;
}

function setInputValuesFromUrlParams() {
    const boostersPerPlayer = getUrlParam('boostersPerPlayer', 4);
    const numPlayers = getUrlParam('numPlayers', 8);
    const cardsPerPack = getUrlParam('cardsPerPack', 12);
    
    if (boostersPerPlayerInput) {
        boostersPerPlayerInput.value = boostersPerPlayer;
    }
    if (maxPodSizeInput) {
        maxPodSizeInput.value = numPlayers;
    }
    if (cardsPerPackInput) {
        cardsPerPackInput.value = cardsPerPack;
    }
}

function reloadPageWithNewParams() {
    const boostersPerPlayer = boostersPerPlayerInput ? parseInt(boostersPerPlayerInput.value) || 4 : 4;
    const numPlayers = maxPodSizeInput ? parseInt(maxPodSizeInput.value) || 8 : 8;
    const cardsPerPack = cardsPerPackInput ? parseInt(cardsPerPackInput.value) || 12 : 12;
    
    const url = new URL(window.location);
    url.searchParams.set('boostersPerPlayer', boostersPerPlayer);
    url.searchParams.set('numPlayers', numPlayers);
    url.searchParams.set('cardsPerPack', cardsPerPack);
    
    window.location.href = url.toString();
}

function setupEventListeners() {
    if (maxPodSizeInput) {
        maxPodSizeInput.addEventListener('change', reloadPageWithNewParams);
    }
    if (boostersPerPlayerInput) {
        boostersPerPlayerInput.addEventListener('change', reloadPageWithNewParams);
    }
    if (cardsPerPackInput && !cardsPerPackInput.disabled) {
        cardsPerPackInput.addEventListener('change', reloadPageWithNewParams);
    }
}

async function loadFormatData() {
    try {
        const boostersPerPlayer = getUrlParam('boostersPerPlayer', 4);
        const numPlayers = getUrlParam('numPlayers', 8);
        const cardsPerPack = getUrlParam('cardsPerPack', 12);
        let analysisUrl = `${window.location.origin}/api/retail_sets/${setId}/analysis?boostersPerPlayer=${boostersPerPlayer}&numPlayers=${numPlayers}&cardsPerPack=${cardsPerPack}`;
        if (isCubeAnalysis && cubeId) {
            analysisUrl = `/api/cube/${cubeId}/analysis?boostersPerPlayer=${boostersPerPlayer}&numPlayers=${numPlayers}&cardsPerPack=${cardsPerPack}`;
        }

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
        boostersPerPlayer: getUrlParam('boostersPerPlayer', 4),
        playersCount: getUrlParam('numPlayers', 8),
        cardsPerPack: getUrlParam('cardsPerPack', 12)
    };
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
    
    // Generate lore chart data
    if (analysisData.loreDistributionByCost) {
        chartData.loreChart = generateStackedChartData(analysisData.loreDistributionByCost, 'Lore');
    }
    
    // Generate rating chart data
    if (analysisData.ratingDistributionByCost) {
        chartData.ratingChart = generateRatingChartData(analysisData.ratingDistributionByCost);
    }
    
    // Generate trait ink cost distributions for classification analysis
    chartData.traitInkCostDistributions = {};
    if (analysisData.costDistributionByClassification) {
        Object.keys(analysisData.costDistributionByClassification).forEach(trait => {
            chartData.traitInkCostDistributions[trait] = analysisData.costDistributionByClassification[trait];
        });
    }
    
    // Generate inkability by cost chart data
    if (analysisData.inkabilityByCost) {
        chartData.inkabilityChart = generateInkabilityChartData(analysisData.inkabilityByCost);
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
            if (cost === '8+') {
                // Sum all costs 8 and higher
                let total = 0;
                Object.keys(distributionByCost).forEach(costKey => {
                    const costNum = parseInt(costKey);
                    if (costNum >= 8) {
                        const costData = distributionByCost[costKey] || {};
                        total += costData[statValue.toString()] || 0;
                    }
                });
                return total;
            } else {
                const costData = distributionByCost[cost] || {};
                return costData[statValue.toString()] || 0;
            }
        });
        
        // Use gradient colors for strength and willpower charts, regular colors for others
        let backgroundColor;
        if (label === 'Strength') {
            backgroundColor = generateStrengthGradientColor(index, sortedStatValues.length);
        } else if (label === 'Willpower') {
            backgroundColor = generateWillpowerGradientColor(index, sortedStatValues.length);
        } else if (label === 'Lore') {
            backgroundColor = generateLoreGradientColor(index, sortedStatValues.length);
        } else if (label === 'Rating') {
            backgroundColor = generateRatingGradientColor(index, sortedStatValues.length);
        } else {
            backgroundColor = generateColor(index);
        }
        
        return {
            label: `${label} ${statValue}`,
            data: data,
            backgroundColor: backgroundColor,
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

function generateStrengthGradientColor(index, total) {
    // Create gradient from yellow (lowest strength) to red (highest strength)
    if (total <= 1) return '#FFFF00'; // Pure yellow for single value
    
    const ratio = index / (total - 1); // 0 to 1
    
    // Interpolate from yellow (255,255,0) to red (255,0,0)
    const red = 255;
    const green = Math.round(255 * (1 - ratio));
    const blue = 0;
    
    return `rgb(${red}, ${green}, ${blue})`;
}

function generateWillpowerGradientColor(index, total) {
    // Create gradient from purple (lowest willpower) to green (highest willpower)
    if (total <= 1) return '#800080'; // Pure purple for single value
    
    const ratio = index / (total - 1); // 0 to 1
    
    // Interpolate from purple (128,0,128) to green (0,255,0)
    const red = Math.round(128 + (0 - 128) * ratio);
    const green = Math.round(0 + (255 - 0) * ratio);
    const blue = Math.round(128 + (0 - 128) * ratio);
    
    return `rgb(${red}, ${green}, ${blue})`;
}

function generateLoreGradientColor(index, total) {
    // Create gradient from blue (lowest lore) to pink (highest lore)
    if (total <= 1) return '#0080FF'; // Pure blue for single value
    
    const ratio = index / (total - 1); // 0 to 1
    
    // Interpolate from blue (0,128,255) to pink (255,192,203)
    const red = Math.round(0 + (255 - 0) * ratio);
    const green = Math.round(128 + (192 - 128) * ratio);
    const blue = Math.round(255 + (203 - 255) * ratio);
    
    return `rgb(${red}, ${green}, ${blue})`;
}

function generateRatingGradientColor(index, total) {
    // Create gradient from dark red (lowest rating) to bright green (highest rating)
    if (total <= 1) return '#800000'; // Dark red for single value
    
    const ratio = index / (total - 1); // 0 to 1
    
    // Interpolate from dark red (128,0,0) to bright green (0,255,0)
    const red = Math.round(128 + (0 - 128) * ratio);
    const green = Math.round(0 + (255 - 0) * ratio);
    const blue = 0;
    
    return `rgb(${red}, ${green}, ${blue})`;
}

function generateRatingChartData(distributionByCost) {
    // Get all ink costs (0-8+)
    const inkCosts = ['0', '1', '2', '3', '4', '5', '6', '7', '8+'];
    
    // Define the proper order for letter grades
    const ratingOrder = ['F-', 'F', 'F+', 'D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+'];
    
    // Get all unique rating values from the data
    const allRatingValues = new Set();
    Object.values(distributionByCost).forEach(costData => {
        Object.keys(costData).forEach(rating => {
            allRatingValues.add(rating);
        });
    });
    
    // Sort ratings according to our defined order
    const sortedRatings = ratingOrder.filter(rating => allRatingValues.has(rating));
    
    // Generate datasets for each rating
    const datasets = sortedRatings.map((rating, index) => {
        const data = inkCosts.map(cost => {
            if (cost === '8+') {
                // Sum all costs 8 and higher
                let total = 0;
                Object.keys(distributionByCost).forEach(costKey => {
                    const costNum = parseInt(costKey);
                    if (costNum >= 8) {
                        const costData = distributionByCost[costKey] || {};
                        total += costData[rating] || 0;
                    }
                });
                return total;
            } else {
                const costData = distributionByCost[cost] || {};
                return costData[rating] || 0;
            }
        });
        
        // Generate color based on position in rating order
        const backgroundColor = generateRatingGradientColor(index, sortedRatings.length);
        
        return {
            label: `Rating ${rating}`,
            data: data,
            backgroundColor: backgroundColor,
            borderColor: '#333',
            borderWidth: 1
        };
    });
    
    return {
        labels: inkCosts,
        datasets: datasets
    };
}

function generateInkabilityChartData(inkabilityByCost) {
    // Get all ink costs (0-8+)
    const inkCosts = ['0', '1', '2', '3', '4', '5', '6', '7', '8+'];
    
    const inkableData = [];
    const nonInkableData = [];
    
    inkCosts.forEach(costStr => {
        if (costStr === '8+') {
            // Sum all costs 8 and higher
            let inkableCount = 0;
            let nonInkableCount = 0;
            
            Object.keys(inkabilityByCost).forEach(cost => {
                const costNum = parseInt(cost);
                if (costNum >= 8) {
                    const costData = inkabilityByCost[cost] || {};
                    inkableCount += costData[true] || 0;
                    nonInkableCount += costData[false] || 0;
                }
            });
            
            inkableData.push(inkableCount);
            nonInkableData.push(nonInkableCount);
        } else {
            const costData = inkabilityByCost[costStr] || {};
            const inkableCount = costData[true] || 0;
            const nonInkableCount = costData[false] || 0;
            
            inkableData.push(inkableCount);
            nonInkableData.push(nonInkableCount);
        }
    });
    
    return {
        labels: inkCosts,
        inkableData: inkableData,
        nonInkableData: nonInkableData
    };
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
                        text: 'estimated cards at table',
                        color: 'white'
                    },
                    ticks: { color: 'white' },
                    grid: { color: '#555' }
                }
            },
            plugins: {
                legend: {
                    labels: { color: 'white' }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.raw.toFixed(1);
                        }
                    }
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
                        text: 'estimated cards at table',
                        color: 'white'
                    },
                    ticks: { color: 'white' },
                    grid: { color: '#555' }
                }
            },
            plugins: {
                legend: {
                    labels: { color: 'white' }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.raw.toFixed(1);
                        }
                    }
                }
            }
        }
    });

    const loreCtx = document.getElementById('loreChart').getContext('2d');
    loreChart = new Chart(loreCtx, {
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
                        text: 'estimated cards at table',
                        color: 'white'
                    },
                    ticks: { color: 'white' },
                    grid: { color: '#555' }
                }
            },
            plugins: {
                legend: {
                    labels: { color: 'white' }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.raw.toFixed(1);
                        }
                    }
                }
            }
        }
    });

    const ratingCtx = document.getElementById('ratingChart').getContext('2d');
    ratingChart = new Chart(ratingCtx, {
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
                        text: 'estimated cards at table',
                        color: 'white'
                    },
                    ticks: { color: 'white' },
                    grid: { color: '#555' }
                }
            },
            plugins: {
                legend: {
                    labels: { color: 'white' }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.raw.toFixed(1);
                        }
                    }
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
                        text: 'estimated cards at table',
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
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.raw.toFixed(1);
                        }
                    }
                }
            }
        }
    });
    
    // Initialize Inkability Chart
    const inkabilityCtx = document.getElementById('inkabilityChart').getContext('2d');
    inkabilityChart = new Chart(inkabilityCtx, {
        type: 'bar',
        data: {
            labels: ['0', '1', '2', '3', '4', '5', '6', '7', '8+'],
            datasets: [{
                label: 'Inkable Cards',
                data: [],
                backgroundColor: '#d4b889',
                borderColor: '#333',
                borderWidth: 1,
                stack: 'inkability'
            }, {
                label: 'Non-Inkable Cards',
                data: [],
                backgroundColor: '#42392a',
                borderColor: '#333',
                borderWidth: 1,
                stack: 'inkability'
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
                        text: 'estimated cards at table',
                        color: 'white'
                    },
                    ticks: { color: 'white' },
                    grid: { color: '#555' },
                    beginAtZero: true,
                    stacked: true
                }
            },
            plugins: {
                legend: {
                    labels: { color: 'white' }
                },
                title: {
                    display: true,
                    text: 'Inkable vs Non-Inkable Cards by Cost',
                    color: 'white',
                    font: { size: 16 }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const datasetLabel = context.dataset.label;
                            const value = context.raw;
                            
                            // Calculate total for this ink cost (sum of inkable + non-inkable)
                            const datasetIndex = context.datasetIndex;
                            const chartData = context.chart.data.datasets;
                            const inkableValue = chartData[0].data[context.dataIndex];
                            const nonInkableValue = chartData[1].data[context.dataIndex];
                            const total = inkableValue + nonInkableValue;
                            
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                            
                            return `${datasetLabel}: ${value.toFixed(1)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function updateAllCharts() {
    updateCardTypeChart();
    updateStrengthChart();
    updateWillpowerChart();
    updateLoreChart();
    updateRatingChart();
    updateInkabilityChart();
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

    const boostersPerPlayer = getUrlParam('boostersPerPlayer', 4);
    const numPlayers = getUrlParam('numPlayers', 8);
    const cardsPerBooster = getUrlParam('cardsPerBooster', 12);

    const allCardsWithTraitSeenAtTable = Object.values(traitCostData).reduce((sum, count) => sum + count, 0);

    const allCardsSeenAtTable = boostersPerPlayer * numPlayers * cardsPerBooster;
    const numCardsNotSeenPerPackInSeat = (numPlayers-1)*(numPlayers)/2;
    const numCardsNotSeenInSeatPerDraft = numCardsNotSeenPerPackInSeat * boostersPerPlayer;
    const numCardsSeenPerSeat = allCardsSeenAtTable - numCardsNotSeenInSeatPerDraft;
    const seenInSeatToAllCardsRatio = numCardsSeenPerSeat / allCardsSeenAtTable;
    const numCardsWithTraitSeenPerSeat = allCardsWithTraitSeenAtTable * seenInSeatToAllCardsRatio;
    
    const tbody = traitTable.querySelector('tbody');
    const existingRow = tbody.querySelector('tr');
    const cells = existingRow.querySelectorAll('td');

    const thead = traitTable.querySelector('thead');
    const headerRow = thead.querySelector('tr');
    const headerCells = headerRow.querySelectorAll('th');
    
    headerCells[1].innerHTML = `Seen at Table <span style="color:gray">(of ${allCardsSeenAtTable} cards)</span>`;
    headerCells[2].innerHTML = `Seen per Seat <span style="color:gray">(of ${numCardsSeenPerSeat} cards)</span>`;

    cells[1].innerHTML = `${Math.round(allCardsWithTraitSeenAtTable)} cards <span style="color:gray">(${(allCardsWithTraitSeenAtTable/allCardsSeenAtTable*100).toFixed(1)}%)</span>`;
    cells[2].innerHTML = `${Math.round(numCardsWithTraitSeenPerSeat)} cards <span style="color:gray">(${(numCardsWithTraitSeenPerSeat/numCardsSeenPerSeat*100).toFixed(1)}%)</span>`;
    
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
        if (label === '8+') {
            // Sum all costs 8 and higher
            let total = 0;
            Object.keys(traitData).forEach(cost => {
                const costNum = parseInt(cost);
                if (costNum >= 8) {
                    total += traitData[cost] || 0;
                }
            });
            return total;
        } else {
            return traitData[label] || 0;
        }
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

function updateLoreChart() {
    if (!setData || !loreChart) return;

    if (setData.chartData && setData.chartData.loreChart) {
        const chartConfig = setData.chartData.loreChart;
        
        loreChart.data.labels = chartConfig.labels;
        loreChart.data.datasets = chartConfig.datasets;
        
        if (chartConfig.options && chartConfig.options.scales && chartConfig.options.scales.y) {
            const yScale = chartConfig.options.scales.y;
            if (yScale.suggestedMax !== null && yScale.suggestedMax !== undefined) {
                loreChart.options.scales.y.suggestedMax = yScale.suggestedMax;
            }
        }
        
        loreChart.update();
    }
}

function updateRatingChart() {
    if (!setData || !ratingChart) return;

    if (setData.chartData && setData.chartData.ratingChart) {
        const chartConfig = setData.chartData.ratingChart;
        
        ratingChart.data.labels = chartConfig.labels;
        ratingChart.data.datasets = chartConfig.datasets;
        
        if (chartConfig.options && chartConfig.options.scales && chartConfig.options.scales.y) {
            const yScale = chartConfig.options.scales.y;
            if (yScale.suggestedMax !== null && yScale.suggestedMax !== undefined) {
                ratingChart.options.scales.y.suggestedMax = yScale.suggestedMax;
            }
        }
        
        ratingChart.update();
    }
}

function updateInkabilityChart() {
    if (!setData || !inkabilityChart) return;

    if (setData.chartData && setData.chartData.inkabilityChart) {
        const chartData = setData.chartData.inkabilityChart;
        
        inkabilityChart.data.labels = chartData.labels;
        inkabilityChart.data.datasets[0].data = chartData.inkableData;
        inkabilityChart.data.datasets[1].data = chartData.nonInkableData;
        
        inkabilityChart.update();
        
        updateInkabilitySummary(chartData);
    }
}

function updateInkabilitySummary(chartData) {
    if (!chartData) return;
    
    // Calculate totals
    const totalInkable = chartData.inkableData.reduce((sum, count) => sum + count, 0);
    const totalNonInkable = chartData.nonInkableData.reduce((sum, count) => sum + count, 0);
    const totalCards = totalInkable + totalNonInkable;
    
    // Calculate percentages
    const inkablePercent = totalCards > 0 ? ((totalInkable / totalCards) * 100).toFixed(1) : 0;
    const nonInkablePercent = totalCards > 0 ? ((totalNonInkable / totalCards) * 100).toFixed(1) : 0;
    
    // Update visual bar
    const inkableBar = document.getElementById('inkableBar');
    const nonInkableBar = document.getElementById('nonInkableBar');
    const inkableText = document.getElementById('inkableText');
    const nonInkableText = document.getElementById('nonInkableText');
    
    if (inkableBar) inkableBar.style.width = `${inkablePercent}%`;
    if (nonInkableBar) nonInkableBar.style.width = `${nonInkablePercent}%`;
    if (inkableText) inkableText.textContent = `${totalInkable.toFixed(1)} (${inkablePercent}%)`;
    if (nonInkableText) nonInkableText.textContent = `${totalNonInkable.toFixed(1)} (${nonInkablePercent}%)`;
}
