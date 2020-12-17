function update() {
    document.getElementById("update").style.color = "#888";
    fetch('https://api.coldness.vrabe.tw')
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            const minTempTime = new Date(data.minTempTime);
            if (data.coldness === "無") {
                document.getElementById("result-1").textContent = "今天沒有冷空氣";
                document.getElementById("result-2").textContent = "";
            } else {
                document.getElementById("result-1").textContent = "今天的冷空氣是";
                document.getElementById("result-2").textContent = data.coldness;
            }
            document.getElementById("current-temp").textContent = data.temp.toFixed(1);
            document.getElementById("min-temp").textContent = data.minTemp.toFixed(1);
            document.getElementById("update-time").textContent = data.time;
            document.getElementById("min-temp-time").textContent = minTempTime.toLocaleTimeString([], { hour12: false, hour: "2-digit", minute: "2-digit" });
            document.getElementById("loading-mask").style.display = 'none';
            document.getElementById("update").style.color = "#000";
        });
}

update();