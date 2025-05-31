const { createApp } = Vue

createApp({
    data() {
        return {
            currentView: 'dashboard',
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
        await this.loadConfig()
        await this.loadStatistics()
        await this.loadRecentBusinesses()
        await this.loadCategories()
        await this.checkScraperStatus()
        
        // Poll scraper status every 5 seconds
        setInterval(this.checkScraperStatus, 5000)
        
        // Poll statistics every 30 seconds
        setInterval(this.loadStatistics, 30000)
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
                if (data.success) {
                    this.config = data.config
                    this.updateConfigForm()
                }
            } catch (error) {
                this.showToast('Error loading configuration', 'error')
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
                }
            } catch (error) {
                console.error('Error loading categories:', error)
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
            
            // Auto remove after 5 seconds
            setTimeout(() => {
                this.removeToast(toast.id)
            }, 5000)
        },
        
        removeToast(id) {
            const index = this.toasts.findIndex(t => t.id === id)
            if (index > -1) {
                this.toasts.splice(index, 1)
            }
        }
    }
}).mount('#app')