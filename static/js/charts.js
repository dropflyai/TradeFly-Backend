/**
 * TradeFly Charts Module
 * Reusable chart components using TradingView Lightweight Charts
 */

const TradeFlyCharts = {
    /**
     * Create a mini price chart for signal cards
     * @param {string} containerId - DOM element ID to render chart
     * @param {string} symbol - Stock symbol
     * @param {object} options - Chart options
     * @returns {object} Chart instance
     */
    createMiniChart(containerId, symbol, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return null;
        }

        // Create chart with dark theme
        const chart = LightweightCharts.createChart(container, {
            width: options.width || 250,
            height: options.height || 150,
            layout: {
                background: { color: 'transparent' },
                textColor: '#9ca3af',
            },
            grid: {
                vertLines: { color: 'rgba(255, 255, 255, 0.02)' },
                horzLines: { color: 'rgba(255, 255, 255, 0.03)' },
            },
            crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal,
            },
            rightPriceScale: {
                borderColor: 'rgba(255, 255, 255, 0.1)',
            },
            timeScale: {
                borderColor: 'rgba(255, 255, 255, 0.1)',
                timeVisible: true,
                secondsVisible: false,
                barSpacing: 12,
                minBarSpacing: 8,
            },
            handleScroll: false,
            handleScale: false,
        });

        // Create candlestick series
        const candlestickSeries = chart.addCandlestickSeries({
            upColor: '#10b981',
            downColor: '#ef4444',
            borderVisible: false,
            wickUpColor: '#10b981',
            wickDownColor: '#ef4444',
        });

        return {
            chart,
            candlestickSeries,
            symbol,
            updateData: async function(data) {
                this.candlestickSeries.setData(data);
                chart.timeScale().fitContent();
            },
            addMarker: function(time, position, text, color) {
                this.candlestickSeries.setMarkers([{
                    time,
                    position: position, // 'aboveBar' or 'belowBar'
                    color,
                    shape: 'circle',
                    text
                }]);
            },
            destroy: function() {
                chart.remove();
            }
        };
    },

    /**
     * Create a full candlestick chart with volume
     * @param {string} containerId - DOM element ID to render chart
     * @param {string} symbol - Stock symbol
     * @returns {object} Chart instance
     */
    createFullChart(containerId, symbol) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return null;
        }

        // Create chart with dark theme
        const chart = LightweightCharts.createChart(container, {
            width: container.clientWidth,
            height: 600,
            layout: {
                background: { color: 'transparent' },
                textColor: '#9ca3af',
            },
            grid: {
                vertLines: { color: 'rgba(255, 255, 255, 0.02)' },
                horzLines: { color: 'rgba(255, 255, 255, 0.03)' },
            },
            crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal,
            },
            rightPriceScale: {
                borderColor: 'rgba(255, 255, 255, 0.1)',
            },
            timeScale: {
                borderColor: 'rgba(255, 255, 255, 0.1)',
                timeVisible: true,
                secondsVisible: false,
                barSpacing: 12,
                minBarSpacing: 8,
            },
        });

        // Create candlestick series
        const candlestickSeries = chart.addCandlestickSeries({
            upColor: '#10b981',
            downColor: '#ef4444',
            borderVisible: false,
            wickUpColor: '#10b981',
            wickDownColor: '#ef4444',
        });

        // Create volume series
        const volumeSeries = chart.addHistogramSeries({
            color: '#26a69a',
            priceFormat: {
                type: 'volume',
            },
            priceScaleId: '',
            scaleMargins: {
                top: 0.75,
                bottom: 0,
            },
        });

        // Make chart responsive
        const resizeObserver = new ResizeObserver(entries => {
            if (entries.length === 0 || entries[0].target !== container) return;
            const newRect = entries[0].contentRect;
            chart.applyOptions({ width: newRect.width });
        });
        resizeObserver.observe(container);

        return {
            chart,
            candlestickSeries,
            volumeSeries,
            symbol,
            resizeObserver,
            updateData: async function(candleData, volumeData) {
                this.candlestickSeries.setData(candleData);
                if (volumeData) {
                    this.volumeSeries.setData(volumeData);
                }
                chart.timeScale().fitContent();
            },
            addLine: function(value, color, lineWidth = 2, lineStyle = LightweightCharts.LineStyle.Solid, title = '') {
                const line = this.candlestickSeries.createPriceLine({
                    price: value,
                    color: color,
                    lineWidth: lineWidth,
                    lineStyle: lineStyle,
                    axisLabelVisible: true,
                    title: title,
                });
                return line;
            },
            addMovingAverage: function(period, color) {
                const lineSeries = chart.addLineSeries({
                    color: color,
                    lineWidth: 2,
                    title: `MA${period}`
                });
                return lineSeries;
            },
            destroy: function() {
                this.resizeObserver.disconnect();
                chart.remove();
            }
        };
    },

    /**
     * Fetch historical price data from backend
     * @param {string} symbol - Stock symbol
     * @param {string} timeframe - Timeframe (1Min, 5Min, 15Min, 1Hour, 1Day)
     * @param {number} days - Number of days of history
     * @returns {Promise<object>} Price data
     */
    async fetchPriceData(symbol, timeframe = '1Day', days = 30) {
        try {
            const response = await fetch(`/api/market/price-history?symbol=${symbol}&timeframe=${timeframe}&days=${days}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching price data:', error);
            return null;
        }
    },

    /**
     * Transform API price data to TradingView chart format
     * @param {Array} apiData - Array of price bars from API
     * @returns {object} Formatted data for candlestick and volume
     */
    transformPriceData(apiData) {
        if (!apiData || !Array.isArray(apiData)) {
            return { candleData: [], volumeData: [] };
        }

        const candleData = apiData.map(bar => ({
            time: bar.timestamp || bar.time,
            open: parseFloat(bar.open),
            high: parseFloat(bar.high),
            low: parseFloat(bar.low),
            close: parseFloat(bar.close),
        }));

        const volumeData = apiData.map(bar => ({
            time: bar.timestamp || bar.time,
            value: parseFloat(bar.volume || 0),
            color: bar.close >= bar.open ? 'rgba(16, 185, 129, 0.25)' : 'rgba(239, 68, 68, 0.25)',
        }));

        return { candleData, volumeData };
    },

    /**
     * Generate demo data for testing (30 days of price bars)
     * @param {number} startPrice - Starting price
     * @param {number} days - Number of days
     * @returns {object} Demo candlestick and volume data
     */
    generateDemoData(startPrice = 100, days = 30) {
        const candleData = [];
        const volumeData = [];
        const now = Math.floor(Date.now() / 1000);
        const daySeconds = 24 * 60 * 60;

        let price = startPrice;
        for (let i = days; i >= 0; i--) {
            const time = now - (i * daySeconds);
            const change = (Math.random() - 0.5) * 5; // Random price movement
            const open = price;
            const close = price + change;
            const high = Math.max(open, close) + Math.random() * 2;
            const low = Math.min(open, close) - Math.random() * 2;

            candleData.push({
                time,
                open,
                high,
                low,
                close,
            });

            volumeData.push({
                time,
                value: Math.random() * 10000000 + 1000000,
                color: close >= open ? 'rgba(16, 185, 129, 0.25)' : 'rgba(239, 68, 68, 0.25)',
            });

            price = close;
        }

        return { candleData, volumeData };
    }
};

// Make available globally
window.TradeFlyCharts = TradeFlyCharts;
