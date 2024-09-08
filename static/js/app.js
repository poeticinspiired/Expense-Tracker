document.addEventListener('DOMContentLoaded', () => {
    const balanceElement = document.getElementById('balance');
    const transactionForm = document.getElementById('transaction-form');
    const transactionList = document.getElementById('transaction-list');
    const amountInput = document.getElementById('amount');
    const descriptionInput = document.getElementById('description');
    const typeSelect = document.getElementById('type');

    let transactions = JSON.parse(localStorage.getItem('transactions')) || [];

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
    }

    window.removeTransaction = function(index) {
        transactions.splice(index, 1);
        localStorage.setItem('transactions', JSON.stringify(transactions));
        updateBalance();
        renderTransactions();
    };

    transactionForm.addEventListener('submit', addTransaction);

    updateBalance();
    renderTransactions();

    // Fetch and display current time from the server
    fetch('/api/current_time')
        .then(response => response.json())
        .then(data => {
            document.getElementById('current-time').textContent = data.current_time;
        })
        .catch(error => console.error('Error fetching current time:', error));
});
