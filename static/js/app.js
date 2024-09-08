document.addEventListener('DOMContentLoaded', () => {
    const balanceElement = document.getElementById('balance');
    const transactionForm = document.getElementById('transaction-form');
    const transactionList = document.getElementById('transaction-list');
    const amountInput = document.getElementById('amount');
    const descriptionInput = document.getElementById('description');
    const typeSelect = document.getElementById('type');
    const expenseChartCtx = document.getElementById('expense-chart').getContext('2d');

    let transactions = JSON.parse(localStorage.getItem('transactions')) || [];
    let expenseChart;

    function updateBalance() {
        const balance = transactions.reduce((acc, transaction) => {
            return transaction.type === 'income' ? acc + transaction.amount : acc - transaction.amount;
        }, 0);

        balanceElement.textContent = balance.toFixed(2);
        balanceElement.className = balance >= 0 ? 'balance positive' : 'balance negative';
    }

    function renderTransactions() {
        transactionList.innerHTML = '';
        transactions.forEach((transaction, index) => {
            const li = document.createElement('li');
            li.className = `transaction-item ${transaction.type}`;
            li.innerHTML = `
                <span>${transaction.description}</span>
                <span>${transaction.type === 'income' ? '+' : '-'}$${transaction.amount.toFixed(2)}</span>
                <button class="btn btn-sm btn-danger" onclick="removeTransaction(${index})">Remove</button>
            `;
            transactionList.appendChild(li);
        });
    }

    function updateChart() {
        const labels = transactions.map(t => t.description);
        const data = transactions.map(t => t.amount);
        const backgroundColors = transactions.map(t => t.type === 'income' ? 'rgba(75, 192, 192, 0.2)' : 'rgba(255, 99, 132, 0.2)');
        const borderColors = transactions.map(t => t.type === 'income' ? 'rgba(75, 192, 192, 1)' : 'rgba(255, 99, 132, 1)');

        if (expenseChart) {
            expenseChart.destroy();
        }

        expenseChart = new Chart(expenseChartCtx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Transaction Amount',
                    data: data,
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    function addTransaction(e) {
        e.preventDefault();
        const amount = parseFloat(amountInput.value);
        const description = descriptionInput.value.trim();
        const type = typeSelect.value;

        if (isNaN(amount) || amount <= 0 || description === '') {
            alert('Please enter a valid amount and description');
            return;
        }

        const transaction = { amount, description, type };
        transactions.push(transaction);
        localStorage.setItem('transactions', JSON.stringify(transactions));

        amountInput.value = '';
        descriptionInput.value = '';
        typeSelect.value = 'expense';

        updateBalance();
        renderTransactions();
        updateChart();
    }

    window.removeTransaction = function(index) {
        transactions.splice(index, 1);
        localStorage.setItem('transactions', JSON.stringify(transactions));
        updateBalance();
        renderTransactions();
        updateChart();
    };

    transactionForm.addEventListener('submit', addTransaction);

    updateBalance();
    renderTransactions();
    updateChart();

    // Fetch and display current time from the server
    fetch('/api/current_time')
        .then(response => response.json())
        .then(data => {
            document.getElementById('current-time').textContent = data.current_time;
        })
        .catch(error => console.error('Error fetching current time:', error));
});
