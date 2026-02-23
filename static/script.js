function startSpeech() {

    if (!('webkitSpeechRecognition' in window)) {
        alert("Speech Recognition not supported in this browser. Use Chrome.");
        return;
    }

    const recognition = new webkitSpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;

    recognition.start();

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById("answerBox").value += " " + transcript;
    };

    recognition.onerror = function(event) {
        alert("Error occurred in recognition: " + event.error);
    };
}
options: {
    responsive: true,
    devicePixelRatio: 2,
    animation: { duration: 1200 },
    plugins: {
        legend: {
            labels: { color: "white" }
        }
    },
    scales: {
        x: { ticks: { color: "white" } },
        y: { ticks: { color: "white" }, beginAtZero: true, max: 10 }
    }
}
datasets: [{
    label: "Interview Score",
    data: scores,
    borderColor: "#00e0ff",
    backgroundColor: "rgba(0,224,255,0.15)",
    borderWidth: 3,
    tension: 0.4,
    fill: true,
    pointRadius: 6,
    pointBackgroundColor: "#ffffff"
}]
<script>
let timeLeft = 60;
let timerDisplay = document.getElementById("timer");

let countdown = setInterval(function() {
    timeLeft--;
    timerDisplay.innerText = "⏱ Time Left: " + timeLeft + "s";

    if(timeLeft <= 0) {
        clearInterval(countdown);
        alert("Time's up! Answer submitted.");
        document.querySelector("form").submit();
    }
}, 1000);
</script>
function showLoader() {
    document.getElementById("loader").style.display = "block";
}

function hideLoader() {
    document.getElementById("loader").style.display = "none";
}
document.querySelectorAll(".nav-item").forEach(item => {
    item.addEventListener("click", function () {
        this.style.transform = "scale(0.9)";
        setTimeout(() => {
            this.style.transform = "";
        }, 150);
    });
});
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/sw.js');
}