console.log("document.location.host : "+ document.location.host);

Highcharts.setOptions({
  global: {
    useUTC: false,
  }
});

var connection = new autobahn.Connection({
   url: 'ws://' + document.location.host + '/ws',
   realm: 'grow',
   debug: true
});

SetSeverity = function(e, sev) {
  e.removeClass("good moderate bad");
  if (sev == 0)
    e.addClass("good")
  else if (sev == 1) {}
  else if (sev == 2)
    e.addClass("moderate")
  else
    e.addClass("bad")
}

UpdateReading = function(loc, temp, cls, target, range, postfix) {
  var e = $("#" + loc + "-" + cls).html(temp.toFixed(1) + postfix);
  SetSeverity(e, Math.floor(Math.abs((temp - target) / range)));
}

UpdateTemp = function(loc, temp) {
  UpdateReading(loc, temp, "temp", 80, 4, "&deg;");
}

UpdateHumidity = function(loc, humidity) {
  UpdateReading(loc, humidity, "humidity", 40, 10, "&deg;");
}

UpdateIndex = function(loc, index) {
  UpdateReading(loc, index, "hindex", 75, 4, "&deg;");
}

MakeChart = function(colors) {
  chart = {
    rangeSelector: {
      enabled: false,
    },
    xAxis: {
      ordinal: false,
    }
  };

  if (typeof(colors) !== 'undefined')
    chart.colors = colors;

  return chart;
}

MakeAxis = function(fmt, opp) {
  return {
    labels: {
      format: fmt,
      y: 6,
    },
    showLastLabel: true,
    opposite: opp,
  }
}

MakeData = function(name, axis, postfix, data, type) {
  return {
    name: name,
    yAxis: axis,
    type: type,
    tooltip: { valueSuffix: postfix },
    data: data};
}

connection.onopen = function(session) {

  function onDHT(args) {
    dht = args[0];

    UpdateTemp(dht.location, dht.temp);
    UpdateHumidity(dht.location, dht.humidity);
    UpdateIndex(dht.location, dht.index);
  }

  function onWater(args) {
    water = args[0];

    $("#water-" + water.location).html(water.value.toFixed(2));
  }

  function onAlert(args) {
    alrt = args[0]

    console.log("alert[" + alrt.severity + "]: " + alrt.message);
  }

  function onSubError(error) {
    console.log("Subscription Error: " + error);
  }

  function onSubSuccess(subscription) {
    console.log("Subscribed to " + subscription);
  }

  session.subscribe('bot.sensor.dht', onDHT).then(onSubSuccess, onSubError);
  session.subscribe('bot.sensor.water', onWater).then(onSubSuccess, onSubError);

  session.call('bot.db.dht', [0]).then(function(rows0) {
  session.call('bot.db.dht', [1]).then(function(rows1) {
  session.call('bot.db.water', [0]).then(function(water0) {
  session.call('bot.db.water', [1]).then(function(water1) {
  session.call('bot.db.water', [2]).then(function(water2) {

  session.call('bot.db.light', [0]).then(function(light0) {
  session.call('bot.db.light', [1]).then(function(light1) {
  session.call('bot.db.light', [2]).then(function(light2) {

      function toTemp(val) {
        return [val[0] * 1000, val[1]]
      }

      function toRH(val) {
        return [val[0] * 1000, val[2]]
      }

      function toWater(val) {
        return [val[0] * 1000, val[1]]
      }

      climateChart = MakeChart(
        ["#3498db", "#2980b9", "#d35400", "#e67e22"]);

      climateChart.yAxis = [
        MakeAxis("{value}&deg;", false),
        MakeAxis("{value}%", true)
      ];

      climateChart.series = [
        MakeData('RH Left', 1, '%', rows0.map(toRH), 'spline'),
        MakeData('RH Right', 1, '%', rows1.map(toRH), 'spline'),
        MakeData('Temp. Left', 0, '&deg;', rows0.map(toTemp), 'spline'),
        MakeData('Temp. Right', 0, '&deg;', rows1.map(toTemp), 'spline'),
      ];

      waterChart = MakeChart();
      waterChart.yAxis = MakeAxis("{value:.2f}", false);
      waterChart.yAxis.min = 0;
      waterChart.yAxis.max = 1;
      waterChart.yAxis.minorTickInterval = .1;

      waterChart.series = [
        MakeData('Water A', 0, '', water0.map(toWater), 'areaspline'),
        MakeData('Water B', 0, '', water1.map(toWater), 'areaspline'),
        MakeData('Water C', 0, '', water2.map(toWater), 'spline'),
      ]

      lightChart = MakeChart();
      lightChart.yAxis = MakeAxis("{value.2f}", false);
      lightChart.yAxis.min = 0;
      lightChart.yAxis.max = 5;
      lightChart.yAxis.minorTickInterval = .5;

      waterChart.series = [
        MakeData('Light A', 0, '', light0.map(toWater), 'areaspline'),
        MakeData('Light B', 0, '', light1.map(toWater), 'areaspline'),
        MakeData('Light C', 0, '', light2.map(toWater), 'spline'),
      ]

      $('#climatechart').highcharts('StockChart', climateChart);
      $('#feedingchart').highcharts('StockChart', waterChart);
      $('#lightchart').highcharts('StockChart', lightChart);

      $(window).resize();
  });
  });
  });
  });
  });
  });
  });
  });
}

connection.onclose = function(reason, details) {
  console.log("conn closed.");
  console.log("reason: " + reason);
  console.log(details);
};


connection.open();

$(document).ready(function() {
});
