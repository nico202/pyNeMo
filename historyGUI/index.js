
//************************************************************
// Data notice the structure
//************************************************************

var data; // a global

d3.json("data.json", function(error, json) {
  if (error) return console.warn(error);
  data = json;
});
alert("done");

//data = [[{"y": -57.486026763916016, "x": 0}, {"y": -40.88831329345703, "x": 1}, {"y": -50.0, "x": 2}, {"y": -23.74584197998047, "x": 3}, {"y": -50.0, "x": 4}, {"y": -28.266111373901367, "x": 5}, {"y": -50.0, "x": 6}, {"y": -48.504581451416016, "x": 7}, {"y": -26.914539337158203, "x": 8}, {"y": -50.0, "x": 9}, {"y": -51.52680969238281, "x": 10}, {"y": -40.242835998535156, "x": 11}, {"y": -12.969738960266113, "x": 12}, {"y": -50.0, "x": 13}, {"y": -54.19658279418945, "x": 14}, {"y": -49.35361862182617, "x": 15}, {"y": -36.73988342285156, "x": 16}, {"y": -50.0, "x": 17}, {"y": -56.40504455566406, "x": 18}, {"y": -55.46046447753906, "x": 19}, {"y": -53.628570556640625, "x": 20}, {"y": -49.88093566894531, "x": 21}, {"y": -55.183475494384766, "x": 22}, {"y": -52.47040939331055, "x": 23}, {"y": -46.61969757080078, "x": 24}, {"y": -28.354507446289062, "x": 25}, {"y": -50.0, "x": 26}, {"y": -43.08711242675781, "x": 27}, {"y": -15.8326416015625, "x": 28}, {"y": -50.0, "x": 29}, {"y": -45.82243728637695, "x": 30}, {"y": -31.966590881347656, "x": 31}, {"y": -50.0, "x": 32}, {"y": -48.20216751098633, "x": 33}, {"y": -42.865753173828125, "x": 34}, {"y": -21.518585205078125, "x": 35}, {"y": -50.0, "x": 36}, {"y": -50.222450256347656, "x": 37}, {"y": -50.35553741455078, "x": 38}, {"y": -50.27876663208008, "x": 39}, {"y": -49.70573425292969, "x": 40}, {"y": -47.88958740234375, "x": 41}, {"y": -42.39048385620117, "x": 42}, {"y": -19.71572494506836, "x": 43}, {"y": -50.0, "x": 44}, {"y": -50.55990982055664, "x": 45}, {"y": -51.47417449951172, "x": 46}, {"y": -53.115020751953125, "x": 47}, {"y": -56.020050048828125, "x": 48}, {"y": -60.46159362792969, "x": 49}], [{"y": -57.486026763916016, "x": 0}, {"y": -40.88831329345703, "x": 1}, {"y": -50.0, "x": 2}, {"y": -41.45074462890625, "x": 3}, {"y": 24.074052810668945, "x": 4}, {"y": -50.0, "x": 5}, {"y": -28.272335052490234, "x": 6}, {"y": -50.0, "x": 7}, {"y": -32.24838638305664, "x": 8}, {"y": -50.0, "x": 9}, {"y": -51.457828521728516, "x": 10}, {"y": -39.97773742675781, "x": 11}, {"y": 16.252262115478516, "x": 12}, {"y": -50.0, "x": 13}, {"y": -54.169677734375, "x": 14}, {"y": -49.27197265625, "x": 15}, {"y": -36.4486198425293, "x": 16}, {"y": -50.0, "x": 17}, {"y": -56.389869689941406, "x": 18}, {"y": -55.422203063964844, "x": 19}, {"y": -53.547149658203125, "x": 20}, {"y": -49.6967887878418, "x": 21}, {"y": -39.81694412231445, "x": 22}, {"y": 8.802216529846191, "x": 23}, {"y": -50.0, "x": 24}, {"y": -43.726478576660156, "x": 25}, {"y": -20.008827209472656, "x": 26}, {"y": -50.0, "x": 27}, {"y": -46.50790023803711, "x": 28}, {"y": -35.36883544921875, "x": 29}, {"y": 5.256298065185547, "x": 30}, {"y": -50.0, "x": 31}, {"y": -48.7794075012207, "x": 32}, {"y": -59.328636169433594, "x": 33}, {"y": -64.01948547363281, "x": 34}, {"y": -68.09961700439453, "x": 35}, {"y": -70.53176879882812, "x": 36}, {"y": -78.63233947753906, "x": 37}, {"y": -74.20814514160156, "x": 38}, {"y": -72.59114837646484, "x": 39}, {"y": -71.72688293457031, "x": 40}, {"y": -71.12452697753906, "x": 41}, {"y": -70.6213150024414, "x": 42}, {"y": -70.15470886230469, "x": 43}, {"y": -69.69819641113281, "x": 44}, {"y": -76.72532653808594, "x": 45}, {"y": -72.02447509765625, "x": 46}, {"y": -69.97367095947266, "x": 47}, {"y": -68.73362731933594, "x": 48}, {"y": -67.81751251220703, "x": 49}]];

var colors = [
	'steelblue',
	'green',
	'red',
	'purple'
]
 
 
//************************************************************
// Create Margins and Axis and hook our zoom function
//************************************************************
var margin = {top: 20, right: 30, bottom: 30, left: 50},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;
	
var x = d3.scale.linear()
    .domain([0, 300])
    .range([0, width]);
 
var y = d3.scale.linear()
    .domain([-100, 30])
    .range([height, 0]);
	
var xAxis = d3.svg.axis()
    .scale(x)
	.tickSize(-height)
	.tickPadding(10)	
	.tickSubdivide(true)	
    .orient("bottom");	
	
var yAxis = d3.svg.axis()
    .scale(y)
	.tickPadding(10)
	.tickSize(-width)
	.tickSubdivide(true)	
    .orient("left");
	
var zoom = d3.behavior.zoom()
    .x(x)
    .y(y)
    .scaleExtent([-100, 20])
    .on("zoom", zoomed);	
	
	
 
	
	
//************************************************************
// Generate our SVG object
//************************************************************	
var svg = d3.select("body").append("svg")
	.call(zoom)
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
	.append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
 
svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis);
 
svg.append("g")
    .attr("class", "y axis")
    .call(yAxis);
 
svg.append("g")
	.attr("class", "y axis")
	.append("text")
	.attr("class", "axis-label")
	.attr("transform", "rotate(-90)")
	.attr("y", (-margin.left) + 10)
	.attr("x", -height/2)
	.text('Axis Label');	
 
svg.append("clipPath")
	.attr("id", "clip")
	.append("rect")
	.attr("width", width)
	.attr("height", height);
	
	
	
	
	
//************************************************************
// Create D3 line object and draw data on our SVG object
//************************************************************
var line = d3.svg.line()
    .interpolate("linear")	
    .x(function(d) { return x(d.x); })
    .y(function(d) { return y(d.y); });		
	
svg.selectAll('.line')
	.data(data)
	.enter()
	.append("path")
    .attr("class", "line")
	.attr("clip-path", "url(#clip)")
	.attr('stroke', function(d,i){ 			
		return colors[i%colors.length];
	})
    .attr("d", line);		
	
	
	
	
//************************************************************
// Draw points on SVG object based on the data given
//************************************************************
var points = svg.selectAll('.dots')
	.data(data)
	.enter()
	.append("g")
    .attr("class", "dots")
	.attr("clip-path", "url(#clip)");	
 
points.selectAll('.dot')
	.data(function(d, index){ 		
		var a = [];
		d.forEach(function(point,i){
			a.push({'index': index, 'point': point});
		});		
		return a;
	})
	.enter()
	.append('circle')
	.attr('class','dot')
	.attr("r", 2.5)
	.attr('fill', function(d,i){ 	
		return colors[d.index%colors.length];
	})	
	.attr("transform", function(d) { 
		return "translate(" + x(d.point.x) + "," + y(d.point.y) + ")"; }
	);
	
 
	
	
	
	
//************************************************************
// Zoom specific updates
//************************************************************
function zoomed() {
	svg.select(".x.axis").call(xAxis);
	svg.select(".y.axis").call(yAxis);   
	svg.selectAll('path.line').attr('d', line);  
 
	points.selectAll('circle').attr("transform", function(d) { 
		return "translate(" + x(d.point.x) + "," + y(d.point.y) + ")"; }
	);  
}
