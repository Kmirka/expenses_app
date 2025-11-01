fetch("/chart-data")
    .then(response => response.json())
    .then(data => {
        if (data.labels.length === 0) return; // якщо немає даних
        const ctx = document.getElementById("expensesChart").getContext("2d");
        new Chart(ctx, {
            type: "pie", // або "bar", "doughnut"
            data: {
                labels: data.labels,
                datasets: [{
                    label: "Витрати",
                    data: data.values,
                    backgroundColor: [
                        "rgba(255, 99, 132, 0.6)",
                        "rgba(54, 162, 235, 0.6)",
                        "rgba(255, 206, 86, 0.6)",
                        "rgba(75, 192, 192, 0.6)",
                        "rgba(153, 102, 255, 0.6)",
                        "rgba(255, 159, 64, 0.6)"
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: false,           // відключає адаптивність
                maintainAspectRatio: true    // дотримується пропорцій канвасу
            }
        });
    });