let city_selected = null;
let category_selected = null;

// Spinner 표시 / 숨김 토글 함수
function showSpinner() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) spinner.style.display = 'flex';
}

function hideSpinner() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) spinner.style.display = 'none';
}



async function loadSummary() {
    let response;
    if (city_selected === null && category_selected === null) {
        response = await fetch("/dashboard/summary");
    }
    else if (city_selected === null) {
        response = await fetch(`/dashboard/summary?category=${category_selected}`);
    }
    else if (category_selected === null) {
        response = await fetch(`/dashboard/summary?city=${city_selected}`);
    }
    else {
        response = await fetch(`/dashboard/summary?city=${city_selected}&category=${category_selected}`);
    }

    const data = await response.json();

    document.getElementById('kpi-total-sales').innerText = `$${data.sales}`;
    document.getElementById('kpi-total-orders').innerText = `${data.orders}`;
    document.getElementById('kpi-customer-count').innerText = `${data.customers}`;

    // console.log('data.customers at line 37 of dashboard.js :', data.customers);

    document.getElementById('kpi-top-category').innerText = `${data.top_category}`;
    document.getElementById("구매분석리포트").innerText = (city_selected === null) ? "구매 분석 리포트" : `구매 분석 리포트 for ${city_selected}`;

    if (data.cusomers) return true;
    else return false;
}


async function loadLinePlot() {
    let response;
    if (city_selected === null && category_selected === null) {
        response = await fetch("/dashboard/monthly_sales");
    }
    else if (category_selected === null) {
        response = await fetch(`/dashboard/monthly_sales?city=${city_selected}`);
    }
    else if (city_selected === null) {
        response = await fetch(`/dashboard/monthly_sales?category=${category_selected}`);
    }
    else {
        response = await fetch(`/dashboard/monthly_sales?city=${city_selected}&category=${category_selected}`);
    }

    const data = await response.json();

    let line_chart = document.getElementById('plotly-line-chart');

    const trace = {
        x: data.months,
        y: data.sales,
        mode: "lines+markers",
        type: "scatter"
    };

    const layout = {
        title:(city_selected === null) ? "Monthly Sales" : `Monthly Sales for ${city_selected}`,
        xaxis: {
            title: "Month"
        },
        yaxis: {
            title: "Sales"
        }
    };

    Plotly.newPlot(line_chart, [trace], layout);

    line_chart.on("plotly_click", function(data){
        console.log(data);
    });
}

async function loadPieChart() {
    let response
    if (city_selected === null) {
        response = await fetch("/dashboard/piechart_categories");
    }
    else {
        response = await fetch(`/dashboard/piechart_categories?city=${city_selected}`);
    }

    const categoryDict = await response.json(); // 예: { "전자기기": 450, "의류": 300 }

    // 2. Dictionary의 key, value를 각각 배열로 추출
    const labels = Object.keys(categoryDict);   // ["전자기기", "의류", ...]
    const values = Object.values(categoryDict); // [450, 300, ...]

    const data = [{
        type: 'pie',
        labels: labels,
        values: values,
        textinfo: 'label+percent',
        hoverinfo: 'label+value+percent'
    }];

    const layout = {
        // title: '카테고리별 판매 비중',
        title:(city_selected === null) ? "카테고리별 판매 비중" : `카테고리별 판매 비중 for ${city_selected}`,
        margin: { l: 20, r: 20, t: 40, b: 20 },
        autosize: true
    };

    const config = { responsive: true, displayModeBar: false };

    // 4. 'plotly-pie-chart' id 영역에 렌더링
    // Plotly.react('plotly-pie-chart', data, layout, config);

    let pie_chart = document.getElementById('plotly-pie-chart');
    Plotly.react(pie_chart, data, layout, config);

    pie_chart.removeAllListeners('plotly_click');
    pie_chart.on("plotly_click", function(data){
        // console.log('data: ', data);
        // console.log('data.points[0].label', data.points[0].label);
        category_selected = data.points[0].label;
        category_selected = category_selected.replace(' ', '%20');
        redrawCharts_from_categoryChart();
    });
}

function redrawCharts_from_categoryChart() {
    showSpinner(); // 1. API 호출 시작 전 Spinner 켜기
    loadSummary();
    loadLinePlot();
    loadBarChart();
    hideSpinner(); // 2. 성공/실패 상관없이 연산이 끝나면 Spinner 끄기
}


async function loadBarChart() {
    let response;
    if (category_selected === null) {
        response = await fetch("/dashboard/barchart_cities");
    }
    else {
        response = await fetch(`/dashboard/barchart_cities?category=${category_selected}`);
    }

    const cityDict = await response.json(); // 예:
    // const cityDict = {"서울": 20, "울산": 50, "부산": 10};

    const data = [{
        x: Object.keys(cityDict),   // ["서울", "울산", "부산"]
        y: Object.values(cityDict), // [20, 50, 10]
        type: 'bar',
        text: Object.values(cityDict).map(String),
        textposition: 'auto',
        marker: {
            color: ['#3c4b64', '#321fdb', '#e55353'] // CoreUI 스타일 차트 색상
        }
    }];

    const layout = {
        title: '지역별 구매 분포',
        margin: { l: 20, r: 20, t: 40, b: 20 },
        autosize: true
    };

    let bar_chart = document.getElementById('plotly-bar-chart');
    Plotly.react(bar_chart, data, layout, { responsive: true, displayModeBar: false });

    bar_chart.removeAllListeners('plotly_click');
    bar_chart.on("plotly_click", function(data){
        city_selected = data.points[0].x;
        city_selected = city_selected.replace(' ', '%20');
        redrawCharts_from_cityChart();
    });
}


function redrawCharts_from_cityChart() {
    showSpinner(); // 1. API 호출 시작 전 Spinner 켜기
    loadSummary();
    loadLinePlot();
    loadPieChart();
    hideSpinner(); // 2. 성공/실패 상관없이 연산이 끝나면 Spinner 끄기
}