class HashApp {
    constructor() {
        this.gost_512 = new GOST3411(512);
        this.gost_256 = new GOST3411(256);
        this.sha1 = new SHA1();
        this.lastResult = null;
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        document.getElementById('calculate-btn').addEventListener('click', () => {
            this.calculateHash();
        });

        document.getElementById('clear-btn').addEventListener('click', () => {
            this.clearAll();
        });

        this.initializeContextMenus();
    }

    switchTab(tabId) {
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });

        document.querySelectorAll('.tab-button').forEach(button => {
            button.classList.remove('active');
        });

        document.getElementById(tabId).classList.add('active');
        
        document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
    }

    initializeContextMenus() {
        const textAreas = document.querySelectorAll('textarea');
        textAreas.forEach(textArea => {
            textArea.addEventListener('contextmenu', (e) => {
                e.preventDefault();
            });
        });
    }

    calculateHash() {
        try {
            const data = document.getElementById('text-input').value;
            const sourceInfo = `Источник: ${!data ? 'Пустая строка' : `Текст (${data.length} символов)`}`;

            const algorithm = document.querySelector('input[name="algorithm"]:checked').value;
            let hashResult, algoName;

            switch (algorithm) {
                case "gost_512":
                    hashResult = this.gost_512.hashHex(data);
                    algoName = "ГОСТ 34.11 (512 бит)";
                    break;
                case "gost_256":
                    hashResult = this.gost_256.hashHex(data);
                    algoName = "ГОСТ 34.11 (256 бит)";
                    break;
                case "sha1":
                    hashResult = this.sha1.hashHex(data);
                    algoName = "SHA-1 (160 бит)";
                    break;
            }

            document.getElementById('info-label').textContent = `${sourceInfo} | Алгоритм: ${algoName}`;

            const resultText = `Хеш-значение:\n${hashResult}\n\n` +
                             `Длина: ${hashResult.length} символов (${hashResult.length * 4} бит)\n` +
                             `Алгоритм: ${algoName}\n` +
                             `Источник: ${!data ? 'пустая строка' : 'введённый текст'}`;

            document.getElementById('result-text').value = resultText;

            this.lastResult = {
                hash: hashResult,
                algorithm: algoName,
                source: sourceInfo,
                data: data
            };

        } catch (error) {
            alert(`Ошибка при вычислении хеша: ${error.message}`);
        }
    }

    clearAll() {
        document.getElementById('text-input').value = '';
        document.getElementById('result-text').value = '';
        document.getElementById('info-label').textContent = '';
        this.lastResult = null;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new HashApp();
});