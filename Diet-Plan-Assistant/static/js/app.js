// App State
let userData = null;

// DOM Elements
const userInfoSection = document.getElementById('user-info-section');
const dashboardSection = document.getElementById('dashboard-section');
const resultsSection = document.getElementById('results-section');
const userInfoForm = document.getElementById('user-info-form');
const loadingOverlay = document.getElementById('loading-overlay');
const loadingText = document.getElementById('loading-text');

// Modals
const searchModal = document.getElementById('search-modal');
const cuisineModal = document.getElementById('cuisine-modal');

// Buttons
const generatePlanBtn = document.getElementById('generate-plan-btn');
const searchFoodBtn = document.getElementById('search-food-btn');
const updateCuisineBtn = document.getElementById('update-cuisine-btn');
const restartBtn = document.getElementById('restart-btn');
const closeResultsBtn = document.getElementById('close-results-btn');
const closeSearchModal = document.getElementById('close-search-modal');
const closeCuisineModal = document.getElementById('close-cuisine-modal');
const searchSubmitBtn = document.getElementById('search-submit-btn');

// Event Listeners
userInfoForm.addEventListener('submit', handleUserInfoSubmit);
generatePlanBtn.addEventListener('click', handleGeneratePlan);
searchFoodBtn.addEventListener('click', () => openModal(searchModal));
updateCuisineBtn.addEventListener('click', () => openModal(cuisineModal));
restartBtn.addEventListener('click', handleRestart);
closeResultsBtn.addEventListener('click', () => hideSection(resultsSection));
closeSearchModal.addEventListener('click', () => closeModal(searchModal));
closeCuisineModal.addEventListener('click', () => closeModal(cuisineModal));
searchSubmitBtn.addEventListener('click', handleFoodSearch);

// Cuisine buttons
document.querySelectorAll('.cuisine-btn').forEach(btn => {
    btn.addEventListener('click', () => handleCuisineUpdate(btn.dataset.cuisine));
});

// Food search on Enter key
document.getElementById('food-search-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleFoodSearch();
});

// Functions
async function handleUserInfoSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(userInfoForm);
    const data = Object.fromEntries(formData.entries());
    
    showLoading('Calculating your macros...');
    
    try {
        const response = await fetch('/api/submit-info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            userData = data;
            displayMacros(result.macros);
            showSection(dashboardSection);
            hideSection(userInfoSection);
            showToast('Success! Your personalized targets are ready.', 'success');
        } else {
            showToast(result.error || 'Failed to calculate macros', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
        console.error('Error:', error);
    } finally {
        hideLoading();
    }
}

async function handleGeneratePlan() {
    showLoading('Generating your personalized diet plan...<br>This may take a moment.');
    
    try {
        const response = await fetch('/api/generate-plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayResults(result.plan, `Your ${result.cuisine.charAt(0).toUpperCase() + result.cuisine.slice(1)} Diet Plan`);
            showToast('Your diet plan is ready!', 'success');
        } else {
            showToast(result.error || 'Failed to generate plan', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
        console.error('Error:', error);
    } finally {
        hideLoading();
    }
}

async function handleFoodSearch() {
    const query = document.getElementById('food-search-input').value.trim();
    
    if (!query) {
        showToast('Please enter a food to search', 'info');
        return;
    }
    
    showLoading('Searching USDA database...');
    
    try {
        const response = await fetch('/api/search-food', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayFoodResults(result.foods);
            if (result.foods.length === 0) {
                showToast('No foods found for that search', 'info');
            }
        } else {
            showToast(result.error || 'Failed to search foods', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
        console.error('Error:', error);
    } finally {
        hideLoading();
    }
}

async function handleCuisineUpdate(cuisine) {
    showLoading('Updating cuisine preference...');
    
    try {
        const response = await fetch('/api/update-cuisine', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ cuisine })
        });
        
        const result = await response.json();
        
        if (result.success) {
            userData.cuisine_preference = cuisine;
            closeModal(cuisineModal);
            showToast(result.message, 'success');
        } else {
            showToast(result.error || 'Failed to update cuisine', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
        console.error('Error:', error);
    } finally {
        hideLoading();
    }
}

function handleRestart() {
    if (confirm('Are you sure you want to start over? This will clear all your data.')) {
        userData = null;
        userInfoForm.reset();
        hideSection(dashboardSection);
        hideSection(resultsSection);
        showSection(userInfoSection);
        showToast('Starting fresh!', 'info');
    }
}

function displayMacros(macros) {
    document.getElementById('calories-value').textContent = macros.calories;
    document.getElementById('protein-value').textContent = macros.protein_g;
    document.getElementById('carbs-value').textContent = macros.carbs_g;
    document.getElementById('fats-value').textContent = macros.fats_g;
    
    const goal = userData.goal.replace('_', ' ');
    const cuisine = userData.cuisine_preference;
    document.getElementById('user-summary').textContent = 
        `${goal.charAt(0).toUpperCase() + goal.slice(1)} with ${cuisine.charAt(0).toUpperCase() + cuisine.slice(1)} cuisine`;
}

function displayResults(content, title) {
    document.getElementById('results-title').textContent = title;
    document.getElementById('results-content').textContent = content;
    showSection(resultsSection);
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function displayFoodResults(foods) {
    const searchResults = document.getElementById('search-results');
    
    if (foods.length === 0) {
        searchResults.innerHTML = '<p style="color: var(--text-secondary); text-align: center;">No foods found. Try a different search term.</p>';
        return;
    }
    
    searchResults.innerHTML = foods.map(food => {
        const nutrients = food.nutrients || {};
        return `
            <div class="food-item">
                <h3>${food.name}</h3>
                <p>
                    <strong>Calories:</strong> ${nutrients.calories || 'N/A'} kcal | 
                    <strong>Protein:</strong> ${nutrients.protein || 'N/A'}g | 
                    <strong>Carbs:</strong> ${nutrients.carbs || 'N/A'}g | 
                    <strong>Fat:</strong> ${nutrients.fat || 'N/A'}g
                </p>
            </div>
        `;
    }).join('');
}

// UI Helper Functions
function showSection(section) {
    section.classList.add('active');
}

function hideSection(section) {
    section.classList.remove('active');
}

function openModal(modal) {
    modal.classList.add('active');
}

function closeModal(modal) {
    modal.classList.remove('active');
}

function showLoading(message = 'Processing...') {
    loadingText.innerHTML = message;
    loadingOverlay.classList.add('active');
}

function hideLoading() {
    loadingOverlay.classList.remove('active');
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    const container = document.getElementById('toast-container');
    container.appendChild(toast);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.4s ease-out reverse';
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}

// Close modals when clicking outside
window.addEventListener('click', (e) => {
    if (e.target === searchModal) closeModal(searchModal);
    if (e.target === cuisineModal) closeModal(cuisineModal);
});

// Smooth scroll behavior
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// Add input validation feedback
document.querySelectorAll('input[required], select[required]').forEach(input => {
    input.addEventListener('invalid', (e) => {
        e.preventDefault();
        showToast(`Please fill in: ${input.previousElementSibling.textContent}`, 'error');
    });
});

console.log('🥗 Diet Plan Assistant loaded successfully!');
