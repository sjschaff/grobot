
// Load the fonts

Highcharts.theme = {
	colors: ["#2b908f", "#90ee7e", "#f45b5b", "#7798BF", "#aaeeee", "#ff0066", "#eeaaee",
		"#55BF3B", "#DF5353", "#7798BF", "#aaeeee"],
	chart: {
    type: 'spline',
		backgroundColor: '#3e3e40', /*{
			linearGradient: { x1: 0, y1: 0, x2: 1, y2: 1 },
			stops: [
				//[0, '#2a2a2b'],
				[1, '#3e3e40']
			]
		},*/
		plotBorderColor: '707073',
    plotBorderWidth: 2
	},
  credits: {
    enabled: false
  },
  rangeSelector: {
    enabled: false
  },
  navigator: {
    xAxis: {
      dateTimeLabelFormats: {
        second: "%m/%e %I %P",
        minute: "%m/%e %I %P",
        hour: "%m/%e %I %P",
      }
    }
  },
	xAxis: {
    type: "datetime",
		gridLineColor: '#707073',
    gridLineWidth: 2,
    ordinal: false,
		labels: {
			style: {
				color: '#E0E0E3'
			},
      x: 18,
      useHTML: true,
      rotation: -45
		},
		lineColor: '#707073',
		minorGridLineColor: '#505053',
    minorTickInterval: 180000,
		tickColor: '#707073',
    tickWidth: 2,
    minorTickWidth: 1,
    dateTimeLabelFormats: {
        second: "%m/%e, %l:%M %P",
        minute: "%m/%e, %l:%M %P",
        hour: "%m/%e, %l %P",
	day: "%a, %m/%e",
	week: "Week of %b. %e",
	month: "%B %Y"
    },
    minRange: 600000,
    minTickInterval: 300000,
    startOnTick: true,
    endOnTick: true,
    tickAmount: 9,
	},
	yAxis: {
		gridLineColor: '#707073',
    gridLineWidth: 2,
    labels: {
      format: "{value}&deg;",
      style: {
  			color: '#E0E0E3',
      },
      y: 6,
      useHTML: true
    },
		tickColor: '#707073',
		tickWidth: 2,
    showLastLabel: true,

    minRange: 15,
    minTickInterval: 1,
    opposite: false,
    lineColor: '#707073',
		minorGridLineColor: '#505053',
    minorGridLineWidth: 1,
    minorTickInterval: 1,
	 },

  rangeSelector: {
    enabled: false,
    allButtonsEnabled: false
  },
	tooltip: {
		backgroundColor: '#707073',
    borderColor: '#707073',
    borderRadius: 5,
    valueDecimals: 2,
    useHTML: true,
    valueSuffix: "&deg;",
		style: {
		  color: '#E0E0E3'
		}
	},
	toolbar: {
		itemStyle: {
			color: 'silver'
		}
	},
	navigator: {
		handles: {
			backgroundColor: '#666',
			borderColor: '#AAA'
		},
		outlineColor: '#CCC',
		maskFill: 'rgba(255,255,255,0.1)',
		series: {
			color: '#7798BF',
			lineColor: '#A6C7ED'
		},
		xAxis: {
			gridLineColor: '#505053'
		}
	},

	scrollbar: {
		barBackgroundColor: '#808083',
		barBorderColor: '#808083',
		buttonArrowColor: '#CCC',
		buttonBackgroundColor: '#606063',
		buttonBorderColor: '#606063',
		rifleColor: '#FFF',
		trackBackgroundColor: '#404043',
		trackBorderColor: '#404043'
	},

	// special colors for some of the
	legendBackgroundColor: 'rgba(0, 0, 0, 0.5)',
	background2: '#505053',
	dataLabelsColor: '#B0B0B3',
	textColor: '#C0C0C0',
	contrastTextColor: '#F0F0F3',
	maskColor: 'rgba(255,255,255,0.3)'
};

// Apply the theme
Highcharts.setOptions(Highcharts.theme);
