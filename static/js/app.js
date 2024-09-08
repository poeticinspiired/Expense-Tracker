document.addEventListener('DOMContentLoaded', () => {
    const balanceElement = document.getElementById('balance');
    const transactionForm = document.getElementById('transaction-form');
    const transactionList = document.getElementById('transaction-list');
    const amountInput = document.getElementById('amount');
    const descriptionInput = document.getElementById('description');
    const typeSelect = document.getElementById('type');
    const categoryInput = document.getElementById('category');
    const dateInput = document.getElementById('date');
    const isRecurringCheckbox = document.getElementById('is-recurring');
    const recurrenceIntervalContainer = document.getElementById('recurrence-interval-container');
    const recurrenceIntervalSelect = document.getElementById('recurrence-interval');
    const categoryFilterSelect = document.getElementById('category-filter');
    const expenseChartCtx = document.getElementById('expense-chart').getContext('2d');
    const processRecurringButton = document.getElementById('process-recurring');

    let transactions = [];
    let categories = [];
    let expenseChart;

    function updateBalance() {
        const balance = transactions.reduce((acc, transaction) => {
            return transaction.type === 'income' ? acc + transaction.amount : acc - transaction.amount;
        }, 0);

        balanceElement.textContent = balance.toFixed(2);
        balanceElement.className = balance >= 0 ? 'balance positive' : 'balance negative';
    }

    function renderTransactions(filteredTransactions = transactions) {
        transactionList.innerHTML = '';
        filteredTransactions.forEach((transaction) => {
            const li = document.createElement('li');
            li.className = `transaction-item ${transaction.type}`;
            li.innerHTML = `
                <span>${transaction.description}</span>
                <span>${transaction.type === 'income' ? '+' : '-'}$${transaction.amount.toFixed(2)}</span>
                <span>${transaction.category}</span>
                <span>${transaction.date}</span>
                <span>${transaction.is_recurring ? 'Recurring' : ''}</span>
                <button class="btn btn-sm btn-danger" onclick="removeTransaction(${transaction.id})">Remove</button>
            `;
            transactionList.appendChild(li);
        });
    }

    function updateChart(filteredTransactions = transactions) {
        const labels = filteredTransactions.map(t => t.description);
        const data = filteredTransactions.map(t => t.amount);
        const backgroundColors = filteredTransactions.map(t => t.type === 'income' ? 'rgba(75, 192, 192, 0.2)' : 'rgba(255, 99, 132, 0.2)');
        const borderColors = filteredTransactions.map(t => t.type === 'income' ? 'rgba(75, 192, 192, 1)' : 'rgba(255, 99, 132, 1)');

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
        const category = categoryInput.value.trim();
        const date = dateInput.value;
        const is_recurring = isRecurringCheckbox.checked;
        const recurrence_interval = is_recurring ? recurrenceIntervalSelect.value : null;

        if (isNaN(amount) || amount <= 0 || description === '' || category === '' || date === '') {
            alert('Please enter valid transaction details');
            return;
        }

        const transaction = { amount, description, type, category, date, is_recurring, recurrence_interval };

        fetch('/api/transactions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(transaction),
        })
        .then(response => response.json())
        .then(data => {
            transactions.push(data);
            updateCategories();
            updateBalance();
            renderTransactions();
            updateChart();
            transactionForm.reset();
            dateInput.value = new Date().toISOString().split('T')[0];
            recurrenceIntervalContainer.style.display = 'none';
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    function removeTransaction(id) {
        fetch(`/api/transactions/${id}`, {
            method: 'DELETE',
        })
        .then(response => {
            if (response.ok) {
                transactions = transactions.filter(t => t.id !== id);
                updateCategories();
                updateBalance();
                renderTransactions();
                updateChart();
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    function updateCategories() {
        categories = [...new Set(transactions.map(t => t.category))];
        categoryFilterSelect.innerHTML = '<option value="">All Categories</option>';
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            categoryFilterSelect.appendChild(option);
        });
    }

    function filterTransactions() {
        const selectedCategory = categoryFilterSelect.value;
        const filteredTransactions = selectedCategory
            ? transactions.filter(t => t.category === selectedCategory)
            : transactions;
        renderTransactions(filteredTransactions);
        updateChart(filteredTransactions);
    }

    function processRecurringTransactions() {
        fetch('/api/process_recurring_transactions', {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            transactions = transactions.concat(data);
            updateCategories();
            updateBalance();
            renderTransactions();
            updateChart();
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    transactionForm.addEventListener('submit', addTransaction);
    categoryFilterSelect.addEventListener('change', filterTransactions);
    processRecurringButton.addEventListener('click', processRecurringTransactions);

    isRecurringCheckbox.addEventListener('change', () => {
        recurrenceIntervalContainer.style.display = isRecurringCheckbox.checked ? 'block' : 'none';
    });

    // Fetch transactions from the server
    fetch('/api/transactions')
        .then(response => response.json())
        .then(data => {
            transactions = data;
            updateCategories();
            updateBalance();
            renderTransactions();
            updateChart();
        })
        .catch((error) => {
            console.error('Error:', error);
        });

    // Fetch and display current time from the server
    fetch('/api/current_time')
        .then(response => response.json())
        .then(data => {
            document.getElementById('current-time').textContent = data.current_time;
        })
        .catch(error => console.error('Error fetching current time:', error));

    // Set default date to today
    dateInput.value = new Date().toISOString().split('T')[0];

    window.removeTransaction = removeTransaction;
});
