const { createApp } = Vue

createApp({
    data() {
        return {
            currentView: 'welcome',  // Start with welcome for first-time users
            loading: false,
            config: {
                monitoring: {
                    category: 'plumber',
                    locations: {
                        states: null,
                        cities: null,
                        min_population: 50000
                    },
                    batch_size: 10,
                    browser_instances: 1
                }
            },
            configForm: {
                scope: 'nationwide',
                statesInput: '',
                citiesInput: '',
                monitoring: {
                    category: 'plumber',
                    locations: {
                        states: null,
                        cities: null,
                        min_population: 50000
                    },
                    batch_size: 10,
                    browser_instances: 1
                }
            },
            statistics: {},
            businesses: [],
            recentBusinesses: [],
            scraperStatus: {
                running: false,
                stats: {}
            },
            availableCategories: {},
            businessDays: 30,
            businessLimit: 100,
            exportForm: {
                format: 'csv',
                days: 30
            },
            exportResult: '',
            toasts: [],
            toastId: 0
        }
    },
    
    async mounted() {
        // Load everything with error handling for first-time users
        try {
            await this.loadConfig()
            await this.loadStatistics()
            await this.loadRecentBusinesses()
            await this.loadCategories()
            await this.checkScraperStatus()
            
            // Poll scraper status every 5 seconds
            setInterval(this.checkScraperStatus, 5000)
            
            // Poll statistics every 30 seconds
            setInterval(this.loadStatistics, 30000)
        } catch (error) {
            console.error('Error during app initialization:', error)
            // Show setup view for first-time users
            this.currentView = 'config'
            this.showToast('Welcome! Please configure MapLeads to get started.', 'info')
        }
    },
    
    methods: {
        setView(view) {
            this.currentView = view
            if (view === 'businesses') {
                this.loadBusinesses()
            }
        },
        
        async loadConfig() {
            try {
                const response = await fetch('/api/config')
                const data = await response.json()
                if (data.success && data.config && data.config.monitoring && data.config.monitoring.category) {
                    this.config = data.config
                    this.updateConfigForm()
                    // User has config, go to dashboard
                    this.currentView = 'dashboard'
                } else {
                    // First-time user - use default config and stay on welcome
                    console.log('First-time user detected')
                    this.updateConfigForm()
                    this.currentView = 'welcome'
                }
            } catch (error) {
                console.error('Error loading configuration:', error)
                // First-time user - show welcome screen
                this.updateConfigForm()
                this.currentView = 'welcome'
            }
        },
        
        updateConfigForm() {
            // Deep copy config to form
            this.configForm.monitoring = JSON.parse(JSON.stringify(this.config.monitoring))
            
            // Determine scope
            if (!this.config.monitoring.locations.states && !this.config.monitoring.locations.cities) {
                this.configForm.scope = 'nationwide'
            } else if (this.config.monitoring.locations.states) {
                this.configForm.scope = 'states'
                this.configForm.statesInput = this.config.monitoring.locations.states.join(', ')
            } else {
                this.configForm.scope = 'cities'
                this.configForm.citiesInput = this.config.monitoring.locations.cities.join(', ')
            }
        },
        
        onScopeChange() {
            if (this.configForm.scope === 'nationwide') {
                this.configForm.monitoring.locations.states = null
                this.configForm.monitoring.locations.cities = null
            }
        },
        
        async saveConfiguration() {
            this.loading = true
            try {
                // Process location settings based on scope
                if (this.configForm.scope === 'states' && this.configForm.statesInput) {
                    this.configForm.monitoring.locations.states = this.configForm.statesInput
                        .split(',')
                        .map(s => s.trim().toUpperCase())
                        .filter(s => s.length === 2)
                    this.configForm.monitoring.locations.cities = null
                } else if (this.configForm.scope === 'cities' && this.configForm.citiesInput) {
                    this.configForm.monitoring.locations.cities = this.configForm.citiesInput
                        .split(',')
                        .map(s => s.trim())
                        .filter(s => s.length > 0)
                    this.configForm.monitoring.locations.states = null
                } else {
                    this.configForm.monitoring.locations.states = null
                    this.configForm.monitoring.locations.cities = null
                }
                
                const response = await fetch('/api/config', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        monitoring: this.configForm.monitoring
                    })
                })
                
                const data = await response.json()
                if (data.success) {
                    this.config = { monitoring: this.configForm.monitoring }
                    this.showToast('Configuration saved successfully!', 'success')
                    
                    // For first-time users, redirect to dashboard after saving
                    if (this.currentView === 'config') {
                        setTimeout(() => {
                            this.currentView = 'dashboard'
                            this.showToast('Setup complete! You can now start monitoring.', 'info')
                        }, 1500)
                    }
                } else {
                    this.showToast(data.error || 'Failed to save configuration', 'error')
                }
            } catch (error) {
                this.showToast('Error saving configuration', 'error')
            } finally {
                this.loading = false
            }
        },
        
        async loadStatistics() {
            try {
                const response = await fetch('/api/statistics')
                const data = await response.json()
                if (data.success) {
                    this.statistics = data.statistics
                }
            } catch (error) {
                console.error('Error loading statistics:', error)
                // Set default stats for first-time users
                this.statistics = {
                    total_businesses: 0,
                    new_this_week: 0,
                    new_this_month: 0,
                    categories_count: 0
                }
            }
        },
        
        async loadBusinesses() {
            this.loading = true
            try {
                let url = `/api/businesses?limit=${this.businessLimit}`
                if (this.businessDays) {
                    url += `&days=${this.businessDays}`
                }
                
                const response = await fetch(url)
                const data = await response.json()
                if (data.success) {
                    this.businesses = data.businesses
                }
            } catch (error) {
                this.showToast('Error loading businesses', 'error')
            } finally {
                this.loading = false
            }
        },
        
        async loadRecentBusinesses() {
            try {
                const response = await fetch('/api/businesses?limit=6')
                const data = await response.json()
                if (data.success) {
                    this.recentBusinesses = data.businesses
                }
            } catch (error) {
                console.error('Error loading recent businesses:', error)
            }
        },
        
        async loadCategories() {
            try {
                const response = await fetch('/api/categories')
                const data = await response.json()
                if (data.success) {
                    this.availableCategories = data.categories
                } else {
                    // Fallback categories for first-time users
                    this.availableCategories = {
                        "Home Services": ["plumber", "electrician", "hvac", "contractor"],
                        "Health & Wellness": ["gym", "dentist", "doctor"],
                        "Professional Services": ["lawyer", "accountant"]
                    }
                }
            } catch (error) {
                console.error('Error loading categories:', error)
                // Set default categories
                this.availableCategories = {
                    "Home Services": ["plumber", "electrician", "hvac", "contractor"],
                    "Health & Wellness": ["gym", "dentist", "doctor"],
                    "Professional Services": ["lawyer", "accountant"]
                }
            }
        },
        
        async checkScraperStatus() {
            try {
                const response = await fetch('/api/scraper/status')
                const data = await response.json()
                if (data.success) {
                    this.scraperStatus = data.status
                }
            } catch (error) {
                console.error('Error checking scraper status:', error)
            }
        },
        
        async startScraper() {
            this.loading = true
            try {
                const response = await fetch('/api/scraper/start', { method: 'POST' })
                const data = await response.json()
                if (data.success) {
                    this.showToast('Scraper started successfully!', 'success')
                    setTimeout(() => this.checkScraperStatus(), 1000)
                } else {
                    this.showToast(data.error || 'Failed to start scraper', 'error')
                }
            } catch (error) {
                this.showToast('Error starting scraper', 'error')
            } finally {
                this.loading = false
            }
        },
        
        async stopScraper() {
            this.loading = true
            try {
                const response = await fetch('/api/scraper/stop', { method: 'POST' })
                const data = await response.json()
                if (data.success) {
                    this.showToast('Scraper stopped successfully!', 'success')
                    setTimeout(() => this.checkScraperStatus(), 1000)
                } else {
                    this.showToast(data.error || 'Failed to stop scraper', 'error')
                }
            } catch (error) {
                this.showToast('Error stopping scraper', 'error')
            } finally {
                this.loading = false
            }
        },
        
        async exportData() {
            this.loading = true
            this.exportResult = ''
            try {
                const response = await fetch('/api/export', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.exportForm)
                })
                
                const data = await response.json()
                if (data.success) {
                    this.exportResult = data.message
                    this.showToast(`Exported ${data.count} businesses!`, 'success')
                } else {
                    this.showToast(data.error || 'Export failed', 'error')
                }
            } catch (error) {
                this.showToast('Error exporting data', 'error')
            } finally {
                this.loading = false
            }
        },
        
        formatDate(dateString) {
            if (!dateString) return 'N/A'
            const date = new Date(dateString)
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
        },
        
        showToast(message, type = 'success') {
            const toast = {
                id: this.toastId++,
                message,
                type
            }
            this.toasts.push(toast)
            
            // Auto remove after 5 seconds for success/error, 8 seconds for info
            const delay = type === 'info' ? 8000 : 5000
            setTimeout(() => {
                this.removeToast(toast.id)
            }, delay)
        },
        
        removeToast(id) {
            const index = this.toasts.findIndex(t => t.id === id)
            if (index > -1) {
                this.toasts.splice(index, 1)
            }
        }
    }
}).mount('#app')