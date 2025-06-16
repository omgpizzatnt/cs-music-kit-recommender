class MusicKitRecommender {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.updateSliderValues();
    }

    initializeElements() {
        // Form elements
        this.feelingsForm = document.getElementById('feelingsForm');
        this.mainContent = document.getElementById('mainContent');
        this.loadingScreen = document.getElementById('loadingScreen');
        this.recommendationResult = document.getElementById('recommendationResult');
          // Sliders
        this.motivationSlider = document.getElementById('motivation');
        this.identitySlider = document.getElementById('identity');
        this.styleSlider = document.getElementById('style');
        this.statusSlider = document.getElementById('status');
        
        // Slider values
        this.motivationValue = document.getElementById('motivationValue');
        this.identityValue = document.getElementById('identityValue');
        this.styleValue = document.getElementById('styleValue');
        this.statusValue = document.getElementById('statusValue');
        
        // Mood buttons
        this.moodButtons = document.querySelectorAll('.mood-btn');
        this.selectedMood = 'neutral';
          // Action buttons
        this.getRecommendationBtn = document.getElementById('getRecommendation');
        this.tryAgainBtn = document.getElementById('tryAgain');
        this.shareResultBtn = document.getElementById('shareResult');
        
        // Result elements
        this.kitImage = document.getElementById('kitImage');
        this.kitName = document.getElementById('kitName');
        this.kitDescription = document.getElementById('kitDescription');
        this.kitRarity = document.getElementById('kitRarity');
        this.aiExplanation = document.getElementById('aiExplanation');
        this.loadingText = document.getElementById('loadingText');
        
        // Enhanced result elements
        this.aiBadge = document.getElementById('aiBadge');
        this.moodMatchText = document.getElementById('moodMatchText');
    }bindEvents() {
        // Slider events
        this.motivationSlider.addEventListener('input', () => this.updateSliderValue('motivation'));
        this.identitySlider.addEventListener('input', () => this.updateSliderValue('identity'));
        this.styleSlider.addEventListener('input', () => this.updateSliderValue('style'));
        this.statusSlider.addEventListener('input', () => this.updateSliderValue('status'));
        
        // Mood button events
        this.moodButtons.forEach(btn => {
            btn.addEventListener('click', () => this.selectMood(btn));
        });
          // Action button events
        this.getRecommendationBtn.addEventListener('click', () => this.getRecommendation());
        this.tryAgainBtn.addEventListener('click', () => this.resetForm());
        this.shareResultBtn.addEventListener('click', () => this.shareResult());        
        // Check if exploreMore button exists
        this.exploreMoreBtn = document.getElementById('exploreMore');
        if (this.exploreMoreBtn) {
            this.exploreMoreBtn.addEventListener('click', () => this.exploreMoreKits());
        }
        
        // YouTube search button
        this.searchYoutubeBtn = document.getElementById('searchYoutube');
        if (this.searchYoutubeBtn) {
            this.searchYoutubeBtn.addEventListener('click', () => this.searchOnYoutube());
        }
        
        // Add some hover effects
        this.addHoverEffects();
    }

    updateSliderValue(sliderName) {
        const slider = document.getElementById(sliderName);
        const valueElement = document.getElementById(sliderName + 'Value');
        valueElement.textContent = slider.value;
        
        // Add visual feedback
        this.updateSliderGradient(slider);
    }

    updateSliderGradient(slider) {
        const value = (slider.value - slider.min) / (slider.max - slider.min) * 100;
        slider.style.background = `linear-gradient(to right, #ff6b35 0%, #f7931e ${value}%, #333333 ${value}%, #333333 100%)`;
    }    updateSliderValues() {
        // Initialize all slider values and gradients
        ['motivation', 'identity', 'style', 'status'].forEach(name => {
            this.updateSliderValue(name);
        });
    }

    selectMood(button) {
        // Remove active class from all buttons
        this.moodButtons.forEach(btn => btn.classList.remove('active'));
        
        // Add active class to clicked button
        button.classList.add('active');
        this.selectedMood = button.dataset.mood;
        
        // Add visual feedback
        button.style.transform = 'scale(0.95)';
        setTimeout(() => {
            button.style.transform = '';
        }, 150);
    }    async getRecommendation() {
        // Collect feelings data with new axis system
        const feelingsData = {
            motivation: parseInt(this.motivationSlider.value),
            identity: parseInt(this.identitySlider.value),
            style: parseInt(this.styleSlider.value),
            status: parseInt(this.statusSlider.value),
            mood: this.selectedMood
        };

        // Show loading screen
        this.showLoading();
        
        try {
            // Start the loading messages
            this.startLoadingMessages();
            
            // Make API request
            const response = await fetch('/api/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(feelingsData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            // Wait a bit for better UX
            setTimeout(() => {
                this.displayRecommendation(result);
            }, 2000);
            
        } catch (error) {
            console.error('Error getting recommendation:', error);
            this.showError('Unable to get recommendation. Please try again.');
        }
    }

    showLoading() {
        this.loadingScreen.classList.remove('hidden');
        this.mainContent.style.display = 'none';
    }

    hideLoading() {
        this.loadingScreen.classList.add('hidden');
        this.mainContent.style.display = 'block';
    }

    async startLoadingMessages() {
        const messages = [
            "Aligning headshots...",
            "Analyzing your vibe...",
            "Consulting the AI...",
            "Matching music styles...",
            "Calibrating recommendations...",
            "Loading the perfect kit..."
        ];
        
        let messageIndex = 0;
        
        const updateMessage = async () => {
            // Get a random CS:GO loading message from API
            try {
                const response = await fetch('/api/loading-message');
                const data = await response.json();
                this.loadingText.textContent = data.message;
            } catch (error) {
                // Fallback to preset messages
                this.loadingText.textContent = messages[messageIndex % messages.length];
                messageIndex++;
            }
        };
        
        // Update message immediately
        updateMessage();
        
        // Update message every 3000ms
        this.loadingInterval = setInterval(updateMessage, 3000);
    }    displayRecommendation(result) {
        // Clear loading interval
        if (this.loadingInterval) {
            clearInterval(this.loadingInterval);
        }
        
        // Hide loading and show result
        this.hideLoading();
        
        // Populate result data
        const kit = result.kit;
        
        this.kitImage.src = kit.image || '/static/images/default-kit.png';
        this.kitImage.alt = kit.name;
        this.kitName.textContent = kit.name;
        this.kitDescription.textContent = kit.description;
        this.kitRarity.textContent = kit.rarity.name;
        this.kitRarity.style.backgroundColor = kit.rarity.color || '#ff6b35';
        this.aiExplanation.textContent = result.explanation;
        
        // Handle AI badge
        if (this.aiBadge) {
            if (result.ai_powered !== false) {
                this.aiBadge.style.display = 'block';
                this.aiBadge.textContent = result.ai_powered ? '🤖 AI Powered' : '🧠 Smart Match';
            } else {
                this.aiBadge.style.display = 'none';
            }
        }        
        // Handle mood match
        if (this.moodMatchText && result.mood_match) {
            this.moodMatchText.textContent = result.mood_match;
        }
        
        // Show result with animation
        this.feelingsForm.classList.add('hidden');
        this.recommendationResult.classList.remove('hidden');
        
        // Add entrance animation
        this.recommendationResult.style.opacity = '0';
        this.recommendationResult.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            this.recommendationResult.style.transition = 'all 0.6s ease';
            this.recommendationResult.style.opacity = '1';
            this.recommendationResult.style.transform = 'translateY(0)';
        }, 100);
    }    resetForm() {
        // Hide result and show form
        this.recommendationResult.classList.add('hidden');
        this.feelingsForm.classList.remove('hidden');
        
        // Reset form values to defaults
        this.motivationSlider.value = 50;
        this.identitySlider.value = 50;
        this.styleSlider.value = 50;
        this.statusSlider.value = 50;
        
        // Reset mood to neutral
        this.moodButtons.forEach(btn => btn.classList.remove('active'));
        const neutralBtn = document.querySelector('[data-mood="neutral"]');
        if (neutralBtn) {
            neutralBtn.classList.add('active');
            this.selectedMood = 'neutral';
        }
        
        // Update slider values
        this.updateSliderValues();
        
        // Add entrance animation to form
        this.feelingsForm.style.opacity = '0';
        this.feelingsForm.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            this.feelingsForm.style.transition = 'all 0.6s ease';
            this.feelingsForm.style.opacity = '1';
            this.feelingsForm.style.transform = 'translateY(0)';
        }, 100);
    }    shareResult() {
        const kitName = this.kitName.textContent;
        const shareText = `I just got recommended "${kitName}" as my perfect CS2 music kit! 🎵 Find your perfect kit at: ${window.location.href}`;
        
        if (navigator.share) {
            navigator.share({
                title: 'My CS2 Music Kit Recommendation',
                text: shareText,
                url: window.location.href
            });
        } else {
            // Fallback: copy to clipboard
            navigator.clipboard.writeText(shareText).then(() => {
                // Show feedback
                const originalText = this.shareResultBtn.textContent;
                this.shareResultBtn.textContent = '✅ Copied!';
                this.shareResultBtn.style.backgroundColor = '#4caf50';
                
                setTimeout(() => {
                    this.shareResultBtn.textContent = originalText;
                    this.shareResultBtn.style.backgroundColor = '';
                }, 2000);
            }).catch(() => {
                alert('Share text: ' + shareText);
            });
        }
    }    exploreMoreKits() {
        // Open music kits API in new tab for exploration
        window.open('/api/music-kits', '_blank');
        
        // Add feedback
        const originalText = this.exploreMoreBtn.textContent;
        this.exploreMoreBtn.textContent = '🚀 Opening...';
        
        setTimeout(() => {
            this.exploreMoreBtn.textContent = originalText;
        }, 1500);
    }

    searchOnYoutube() {
        // Search for the music kit on YouTube
        const kitName = this.kitName.textContent;
        if (kitName) {
            const searchQuery = encodeURIComponent(`CS2 ${kitName}`);
            const youtubeUrl = `https://www.youtube.com/results?search_query=${searchQuery}`;
            window.open(youtubeUrl, '_blank');
            
            // Add feedback
            const originalText = this.searchYoutubeBtn.textContent;
            this.searchYoutubeBtn.textContent = '🎬 Searching...';
            
            setTimeout(() => {
                this.searchYoutubeBtn.textContent = originalText;
            }, 1500);
        }
    }

    showError(message) {
        this.hideLoading();
        alert(message); // Simple error handling for now
    }

    addHoverEffects() {
        // Add particle effects on hover for buttons
        const buttons = document.querySelectorAll('.recommend-btn, .primary-btn, .secondary-btn');
        
        buttons.forEach(button => {
            button.addEventListener('mouseenter', () => {
                button.style.transform = 'translateY(-2px)';
            });
            
            button.addEventListener('mouseleave', () => {
                button.style.transform = '';
            });
        });
        
        // Add ripple effect to mood buttons
        this.moodButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const ripple = document.createElement('span');
                const rect = btn.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = x + 'px';
                ripple.style.top = y + 'px';
                ripple.classList.add('ripple');
                
                btn.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MusicKitRecommender();
});

// Add some CSS for ripple effect
const style = document.createElement('style');
style.textContent = `
    .mood-btn {
        position: relative;
        overflow: hidden;
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .feelings-form, .recommendation-result {
        transition: all 0.6s ease;
    }
`;
document.head.appendChild(style);
